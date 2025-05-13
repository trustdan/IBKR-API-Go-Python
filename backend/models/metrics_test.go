package models

import (
	"encoding/json"
	"testing"
	"time"
)

func TestAllMetricsJsonMarshaling(t *testing.T) {
	// Create a test timestamp
	testTime := time.Date(2023, 7, 15, 10, 30, 0, 0, time.UTC)

	// Create sample metrics
	metrics := AllMetrics{
		Portfolio: PortfolioMetrics{
			Timestamp:          testTime,
			Equity:             100000.50,
			RealizedPNLToday:   1250.75,
			UnrealizedPNL:      -350.25,
			OpenPositionsCount: 3,
			BuyingPower:        45000.00,
		},
		Trades: TradeStatsToday{
			ExecutedCount: 10,
			WinCount:      7,
			LossCount:     3,
			WinRate:       0.7,
			AvgWinAmount:  350.50,
			AvgLossAmount: -150.25,
		},
		System: SystemHealthMetrics{
			AvgOrderLatencyMs: 125.5,
			ApiErrorCount:     2,
			LastDataSync:      testTime,
		},
		OpenPositions: []Position{
			{
				Symbol:       "AAPL",
				Quantity:     100,
				EntryPrice:   175.50,
				CurrentPrice: 180.25,
				UnrealizedPL: 475.00,
				Strategy:     "BullPutSpread",
				OpenTime:     testTime.Format(time.RFC3339),
			},
		},
	}

	// Marshal to JSON
	jsonData, err := json.Marshal(metrics)
	if err != nil {
		t.Fatalf("Failed to marshal metrics to JSON: %v", err)
	}

	// Unmarshal back to verify roundtrip
	var unmarshaledMetrics AllMetrics
	err = json.Unmarshal(jsonData, &unmarshaledMetrics)
	if err != nil {
		t.Fatalf("Failed to unmarshal metrics from JSON: %v", err)
	}

	// Verify key fields
	if unmarshaledMetrics.Portfolio.Equity != metrics.Portfolio.Equity {
		t.Errorf("Portfolio Equity mismatch: got %v, want %v",
			unmarshaledMetrics.Portfolio.Equity, metrics.Portfolio.Equity)
	}

	if unmarshaledMetrics.Trades.WinRate != metrics.Trades.WinRate {
		t.Errorf("Trades WinRate mismatch: got %v, want %v",
			unmarshaledMetrics.Trades.WinRate, metrics.Trades.WinRate)
	}

	if len(unmarshaledMetrics.OpenPositions) != len(metrics.OpenPositions) {
		t.Errorf("OpenPositions length mismatch: got %v, want %v",
			len(unmarshaledMetrics.OpenPositions), len(metrics.OpenPositions))
	}

	if len(unmarshaledMetrics.OpenPositions) > 0 {
		if unmarshaledMetrics.OpenPositions[0].Symbol != metrics.OpenPositions[0].Symbol {
			t.Errorf("Position Symbol mismatch: got %v, want %v",
				unmarshaledMetrics.OpenPositions[0].Symbol, metrics.OpenPositions[0].Symbol)
		}
	}
}
