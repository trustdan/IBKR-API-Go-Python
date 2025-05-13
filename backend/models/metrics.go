package models

import "time"

// PortfolioMetrics contains real-time portfolio level metrics
type PortfolioMetrics struct {
	Timestamp          time.Time `json:"timestamp"`
	Equity             float64   `json:"equity"`
	RealizedPNLToday   float64   `json:"realizedPnlToday"`
	UnrealizedPNL      float64   `json:"unrealizedPnl"`
	OpenPositionsCount int       `json:"openPositionsCount"`
	BuyingPower        float64   `json:"buyingPower"`
}

// TradeStatsToday contains aggregated trade statistics for the current day
type TradeStatsToday struct {
	ExecutedCount int     `json:"executedCount"`
	WinCount      int     `json:"winCount"`
	LossCount     int     `json:"lossCount"`
	WinRate       float64 `json:"winRate"` // Calculated: WinCount / ExecutedCount
	AvgWinAmount  float64 `json:"avgWinAmount"`
	AvgLossAmount float64 `json:"avgLossAmount"`
}

// SystemHealthMetrics contains system performance and health indicators
type SystemHealthMetrics struct {
	AvgOrderLatencyMs float64   `json:"avgOrderLatencyMs"`
	ApiErrorCount     int       `json:"apiErrorCount"`
	LastDataSync      time.Time `json:"lastDataSync"`
}

// Position represents an individual open position in the portfolio
type Position struct {
	Symbol       string  `json:"symbol"`
	Quantity     int     `json:"quantity"`
	EntryPrice   float64 `json:"entryPrice"`
	CurrentPrice float64 `json:"currentPrice"`
	UnrealizedPL float64 `json:"unrealizedPl"`
	Strategy     string  `json:"strategy"`
	OpenTime     string  `json:"openTime"` // ISO format
}

// AllMetrics contains all the monitoring metrics in a single structure
type AllMetrics struct {
	Portfolio     PortfolioMetrics    `json:"portfolio"`
	Trades        TradeStatsToday     `json:"trades"`
	System        SystemHealthMetrics `json:"system"`
	OpenPositions []Position          `json:"openPositions"`
}
