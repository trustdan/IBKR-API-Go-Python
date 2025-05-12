package main

import (
	"fmt"
	"math"
	"time"
)

// OptionFilter contains all the filter criteria for option selection
type OptionFilter struct {
	// Basic liquidity filters
	MinOpenInterest    int
	MaxBidAskSpreadPct float64

	// IV-based filters
	MinIVRank         float64
	MaxIVRank         float64
	MinCallPutSkewPct float64

	// Greek limits
	MaxThetaPerDay   float64
	MaxVegaExposure  float64
	MaxGammaExposure float64

	// Probability filters
	MinPOP            float64
	MaxWidthVsMovePct float64

	// Event avoidance
	SkipEarningsDays int
	SkipExDivDays    int

	// DTE selection
	UseDynamicDTE  bool
	DTECoefficient float64
}

// Option represents a single option contract
type Option struct {
	Symbol       string
	Expiry       time.Time
	Strike       float64
	Type         string // "call" or "put"
	Bid          float64
	Ask          float64
	IV           float64
	IVPercentile float64 // 0-100 (IV Rank)
	Delta        float64
	Gamma        float64
	Theta        float64
	Vega         float64
	OpenInterest int
	Volume       int
}

// OptionSpread represents a multi-leg option position
type OptionSpread struct {
	Symbol      string
	SpreadType  string // "vertical", "iron_condor", etc.
	Legs        []Option
	TotalDelta  float64
	TotalGamma  float64
	TotalTheta  float64
	TotalVega   float64
	ThetaPerDay float64
	Width       float64
	MaxProfit   float64
	MaxLoss     float64
	ModelPOP    float64 // Probability of Profit
}

// GetBidAskSpreadPct calculates the bid-ask spread as a percentage of mid price
func (o *Option) GetBidAskSpreadPct() float64 {
	mid := (o.Bid + o.Ask) / 2
	if mid == 0 {
		return math.MaxFloat64
	}
	return 100 * (o.Ask - o.Bid) / mid
}

// FilterOption applies all filters to determine if an option meets criteria
func FilterOption(opt Option, filter OptionFilter) bool {
	// 1. Check liquidity filters
	if opt.OpenInterest < filter.MinOpenInterest {
		fmt.Printf("Option %s %s at %.2f rejected: Open interest %d below min %d\n",
			opt.Symbol, opt.Type, opt.Strike, opt.OpenInterest, filter.MinOpenInterest)
		return false
	}

	spreadPct := opt.GetBidAskSpreadPct()
	if spreadPct > filter.MaxBidAskSpreadPct {
		fmt.Printf("Option %s %s at %.2f rejected: Spread %.2f%% above max %.2f%%\n",
			opt.Symbol, opt.Type, opt.Strike, spreadPct, filter.MaxBidAskSpreadPct)
		return false
	}

	// 2. Check IV-based filters
	if opt.IVPercentile < filter.MinIVRank || opt.IVPercentile > filter.MaxIVRank {
		fmt.Printf("Option %s %s at %.2f rejected: IV Rank %.2f outside range [%.2f, %.2f]\n",
			opt.Symbol, opt.Type, opt.Strike, opt.IVPercentile, filter.MinIVRank, filter.MaxIVRank)
		return false
	}

	// 3. Check Greek limits (for individual options)
	if math.Abs(opt.Theta) > filter.MaxThetaPerDay {
		fmt.Printf("Option %s %s at %.2f rejected: Theta %.2f above max %.2f\n",
			opt.Symbol, opt.Type, opt.Strike, math.Abs(opt.Theta), filter.MaxThetaPerDay)
		return false
	}

	if math.Abs(opt.Vega) > filter.MaxVegaExposure {
		fmt.Printf("Option %s %s at %.2f rejected: Vega %.2f above max %.2f\n",
			opt.Symbol, opt.Type, opt.Strike, math.Abs(opt.Vega), filter.MaxVegaExposure)
		return false
	}

	if math.Abs(opt.Gamma) > filter.MaxGammaExposure {
		fmt.Printf("Option %s %s at %.2f rejected: Gamma %.4f above max %.4f\n",
			opt.Symbol, opt.Type, opt.Strike, math.Abs(opt.Gamma), filter.MaxGammaExposure)
		return false
	}

	return true
}

// FilterSpread applies all filters to determine if a spread meets criteria
func FilterSpread(spread OptionSpread, filter OptionFilter, expectedMove float64) bool {
	// 1. Check probability filters
	if spread.ModelPOP < filter.MinPOP {
		fmt.Printf("Spread %s %s rejected: POP %.2f%% below min %.2f%%\n",
			spread.Symbol, spread.SpreadType, spread.ModelPOP, filter.MinPOP)
		return false
	}

	// 2. Check width vs expected move
	widthVsMovePct := 100 * spread.Width / expectedMove
	if widthVsMovePct > filter.MaxWidthVsMovePct {
		fmt.Printf("Spread %s %s rejected: Width/Move %.2f%% above max %.2f%%\n",
			spread.Symbol, spread.SpreadType, widthVsMovePct, filter.MaxWidthVsMovePct)
		return false
	}

	// 3. Check aggregate Greek limits
	if math.Abs(spread.ThetaPerDay) > filter.MaxThetaPerDay {
		fmt.Printf("Spread %s %s rejected: Daily theta %.2f above max %.2f\n",
			spread.Symbol, spread.SpreadType, math.Abs(spread.ThetaPerDay), filter.MaxThetaPerDay)
		return false
	}

	if math.Abs(spread.TotalVega) > filter.MaxVegaExposure {
		fmt.Printf("Spread %s %s rejected: Total vega %.2f above max %.2f\n",
			spread.Symbol, spread.SpreadType, math.Abs(spread.TotalVega), filter.MaxVegaExposure)
		return false
	}

	if math.Abs(spread.TotalGamma) > filter.MaxGammaExposure {
		fmt.Printf("Spread %s %s rejected: Total gamma %.4f above max %.4f\n",
			spread.Symbol, spread.SpreadType, math.Abs(spread.TotalGamma), filter.MaxGammaExposure)
		return false
	}

	return true
}

// SkipExpirationForEvents checks if an expiration date should be skipped due to nearby events
func SkipExpirationForEvents(expiry time.Time, earningsDate, exDivDate time.Time, filter OptionFilter) bool {
	// Skip expirations near earnings
	if !earningsDate.IsZero() {
		daysDiff := int(math.Abs(float64(earningsDate.Sub(expiry).Hours()) / 24))
		if daysDiff <= filter.SkipEarningsDays {
			fmt.Printf("Expiration %s rejected: Too close to earnings on %s (%d days)\n",
				expiry.Format("2006-01-02"), earningsDate.Format("2006-01-02"), daysDiff)
			return true
		}
	}

	// Skip expirations near ex-dividend
	if !exDivDate.IsZero() {
		daysDiff := int(math.Abs(float64(exDivDate.Sub(expiry).Hours()) / 24))
		if daysDiff <= filter.SkipExDivDays {
			fmt.Printf("Expiration %s rejected: Too close to ex-div on %s (%d days)\n",
				expiry.Format("2006-01-02"), exDivDate.Format("2006-01-02"), daysDiff)
			return true
		}
	}

	return false
}

// GetTargetDTE calculates the target DTE based on ATR if dynamic DTE is enabled
func GetTargetDTE(atr float64, filter OptionFilter) int {
	if !filter.UseDynamicDTE {
		return 0 // Use preferred DTEs from config
	}

	targetDTE := int(atr * filter.DTECoefficient)
	fmt.Printf("Calculated dynamic target DTE: %d based on ATR %.2f and coefficient %.2f\n",
		targetDTE, atr, filter.DTECoefficient)

	return targetDTE
}

// FindBestExpiration selects the best expiration date
func FindBestExpiration(expirations []time.Time, targetDTE int) time.Time {
	if len(expirations) == 0 {
		return time.Time{}
	}

	now := time.Now()
	closest := expirations[0]
	minDiff := math.MaxInt32

	for _, exp := range expirations {
		dte := int(exp.Sub(now).Hours() / 24)
		diff := int(math.Abs(float64(dte - targetDTE)))

		if diff < minDiff {
			minDiff = diff
			closest = exp
		}
	}

	return closest
}

// SelectOptionSpreads is the main function that applies all filters and returns viable spreads
func SelectOptionSpreads(
	symbol string,
	options []Option,
	filter OptionFilter,
	atr float64,
	earningsDate, exDivDate time.Time,
) []OptionSpread {
	result := []OptionSpread{}

	// Get all unique expiration dates
	expirations := map[time.Time]bool{}
	for _, opt := range options {
		expirations[opt.Expiry] = true
	}

	// Convert to slice
	expirationDates := []time.Time{}
	for exp := range expirations {
		// First check for event avoidance
		if SkipExpirationForEvents(exp, earningsDate, exDivDate, filter) {
			continue
		}
		expirationDates = append(expirationDates, exp)
	}

	// Get target DTE
	targetDTE := GetTargetDTE(atr, filter)

	// Find best expiration
	bestExpiry := FindBestExpiration(expirationDates, targetDTE)

	// Early exit if no valid expiration found
	if bestExpiry.IsZero() {
		fmt.Println("No valid expiration dates found after applying filters")
		return result
	}

	// Filter options by expiry and apply basic filters
	var validOptions []Option
	for _, opt := range options {
		if opt.Expiry.Equal(bestExpiry) && FilterOption(opt, filter) {
			validOptions = append(validOptions, opt)
		}
	}

	// Group by type
	calls := map[float64]Option{}
	puts := map[float64]Option{}

	for _, opt := range validOptions {
		if opt.Type == "call" {
			calls[opt.Strike] = opt
		} else {
			puts[opt.Strike] = opt
		}
	}

	// Calculate expected move (simplified example)
	expectedMove := atr * math.Sqrt(float64(int(bestExpiry.Sub(time.Now()).Hours()/24))/5.0)
	fmt.Printf("Expected move for %s by %s: $%.2f\n",
		symbol, bestExpiry.Format("2006-01-02"), expectedMove)

	// Build vertical spreads
	// For this example, we'll just create a few sample spreads
	// In a real implementation, this would be more sophisticated

	// Sample put credit spread
	if len(puts) >= 2 {
		var strikes []float64
		for strike := range puts {
			strikes = append(strikes, strike)
		}

		// Sort strikes in ascending order
		for i := 0; i < len(strikes); i++ {
			for j := i + 1; j < len(strikes); j++ {
				if strikes[i] > strikes[j] {
					strikes[i], strikes[j] = strikes[j], strikes[i]
				}
			}
		}

		// Find the middle strike
		midIdx := len(strikes) / 2
		if midIdx+1 < len(strikes) {
			shortStrike := strikes[midIdx]
			longStrike := strikes[midIdx-1]

			shortPut := puts[shortStrike]
			longPut := puts[longStrike]

			width := shortStrike - longStrike
			credit := shortPut.Bid - longPut.Ask
			maxProfit := credit * 100
			maxLoss := (width - credit) * 100
			pop := 100.0 * (1.0 - math.Abs(shortPut.Delta))

			spread := OptionSpread{
				Symbol:      symbol,
				SpreadType:  "put_vertical",
				Legs:        []Option{shortPut, longPut},
				TotalDelta:  shortPut.Delta + longPut.Delta,
				TotalGamma:  shortPut.Gamma + longPut.Gamma,
				TotalTheta:  shortPut.Theta + longPut.Theta,
				TotalVega:   shortPut.Vega + longPut.Vega,
				ThetaPerDay: shortPut.Theta + longPut.Theta,
				Width:       width,
				MaxProfit:   maxProfit,
				MaxLoss:     maxLoss,
				ModelPOP:    pop,
			}

			if FilterSpread(spread, filter, expectedMove) {
				result = append(result, spread)
			}
		}
	}

	// Similarly, build call credit spreads, iron condors, etc.

	return result
}

// RunOptionSelectorExample demonstrates how to use the option selector
func RunOptionSelectorExample() {
	// Example usage
	filter := OptionFilter{
		MinOpenInterest:    1000,
		MaxBidAskSpreadPct: 0.5,
		MinIVRank:          30.0,
		MaxIVRank:          70.0,
		MinCallPutSkewPct:  5.0,
		MaxThetaPerDay:     15.0,
		MaxVegaExposure:    0.8,
		MaxGammaExposure:   0.05,
		MinPOP:             60.0,
		MaxWidthVsMovePct:  150.0,
		SkipEarningsDays:   3,
		SkipExDivDays:      2,
		UseDynamicDTE:      true,
		DTECoefficient:     1.5,
	}

	// This would be populated with real data in production
	options := []Option{
		// Sample options data would go here
	}

	earningsDate := time.Now().Add(10 * 24 * time.Hour) // 10 days from now
	exDivDate := time.Now().Add(15 * 24 * time.Hour)    // 15 days from now

	spreads := SelectOptionSpreads("AAPL", options, filter, 5.0, earningsDate, exDivDate)

	fmt.Printf("Found %d viable spreads\n", len(spreads))
	for i, spread := range spreads {
		fmt.Printf("Spread %d: %s %s, Width: %.2f, Max Profit: $%.2f, Max Loss: $%.2f, POP: %.2f%%\n",
			i+1, spread.Symbol, spread.SpreadType, spread.Width, spread.MaxProfit, spread.MaxLoss, spread.ModelPOP)
	}
}
