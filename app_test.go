package main

import (
	"testing"
	"time"
)

func TestConfigValidation(t *testing.T) {
	tests := []struct {
		name        string
		config      Configuration
		shouldError bool
	}{
		{
			name: "Valid configuration",
			config: func() Configuration {
				// Create a valid configuration
				var config Configuration
				config.IBKRConnection.Host = "localhost"
				config.IBKRConnection.Port = 7497
				config.IBKRConnection.ClientIDTrading = 1
				config.IBKRConnection.ClientIDData = 2
				config.IBKRConnection.AccountCode = "DU123456"

				// Valid trading parameters
				config.TradingParameters.GlobalMaxConcurrentPositions = 10
				config.TradingParameters.DefaultRiskPerTradePercentage = 1.0
				config.TradingParameters.EmergencyStopLossPercentage = 5.0

				// Valid options filters
				config.OptionsFilters.MinOpenInterest = 500
				config.OptionsFilters.MaxBidAskSpreadPercentage = 0.6
				config.OptionsFilters.UseIVRankFilter = true
				config.OptionsFilters.MinIVRank = 25.0
				config.OptionsFilters.MaxIVRank = 75.0

				// Valid greek limits
				config.GreekLimits.UseGreekLimits = true
				config.GreekLimits.MaxAbsPositionDelta = 0.5
				config.GreekLimits.MaxAbsPositionGamma = 0.05
				config.GreekLimits.MaxAbsPositionVega = 10.0
				config.GreekLimits.MinPositionTheta = 0.1

				// Valid trading schedule
				config.TradingSchedule.Enabled = true
				config.TradingSchedule.StartTimeUTC = "13:30"
				config.TradingSchedule.StopTimeUTC = "20:00"
				config.TradingSchedule.DaysOfWeek = []string{"Mon", "Tue", "Wed", "Thu", "Fri"}

				return config
			}(),
			shouldError: false,
		},
		{
			name: "Invalid DTE range",
			config: func() Configuration {
				// Start with valid config
				var config Configuration
				config.IBKRConnection.Host = "localhost"
				config.IBKRConnection.Port = 7497
				config.IBKRConnection.ClientIDTrading = 1

				// Set invalid DTE range where MinDTE > MaxDTE
				config.TradeTiming.MinDTE = 90
				config.TradeTiming.MaxDTE = 30

				return config
			}(),
			shouldError: true,
		},
		{
			name: "Invalid IV rank range",
			config: func() Configuration {
				// Start with valid config
				var config Configuration
				config.IBKRConnection.Host = "localhost"
				config.IBKRConnection.Port = 7497
				config.IBKRConnection.ClientIDTrading = 1

				// Set invalid IV rank range where Min > Max
				config.OptionsFilters.UseIVRankFilter = true
				config.OptionsFilters.MinIVRank = 80.0
				config.OptionsFilters.MaxIVRank = 30.0

				return config
			}(),
			shouldError: true,
		},
		{
			name: "Invalid trading schedule times",
			config: func() Configuration {
				// Start with valid config
				var config Configuration
				config.IBKRConnection.Host = "localhost"
				config.IBKRConnection.Port = 7497
				config.IBKRConnection.ClientIDTrading = 1

				// Set invalid trading schedule times
				config.TradingSchedule.Enabled = true
				config.TradingSchedule.StartTimeUTC = "25:30" // Invalid hour
				config.TradingSchedule.StopTimeUTC = "20:00"

				return config
			}(),
			shouldError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			app := NewApp()
			// We need to call app.validateConfig which should exist in your app.go
			// If it doesn't exist, you'll need to extract the validation logic into a separate method
			err := app.validateConfig(tt.config)

			if (err != nil) != tt.shouldError {
				t.Errorf("validateConfig() error = %v, shouldError %v", err, tt.shouldError)
			}
		})
	}
}

// Mock function to simulate the validation logic from app.go
// You'll need to implement this with your actual validation logic
func (a *App) validateConfig(config Configuration) error {
	// Example validation rules:

	// Validate DTE range
	if config.TradeTiming.MinDTE > config.TradeTiming.MaxDTE {
		return &ValidationError{Field: "TradeTiming.MinDTE/MaxDTE", Message: "MinDTE cannot be greater than MaxDTE"}
	}

	// Validate IV rank range if filter is enabled
	if config.OptionsFilters.UseIVRankFilter &&
		config.OptionsFilters.MinIVRank > config.OptionsFilters.MaxIVRank {
		return &ValidationError{Field: "OptionsFilters.MinIVRank/MaxIVRank", Message: "MinIVRank cannot be greater than MaxIVRank"}
	}

	// Validate trading schedule time format
	if config.TradingSchedule.Enabled {
		_, err := time.Parse("15:04", config.TradingSchedule.StartTimeUTC)
		if err != nil {
			return &ValidationError{Field: "TradingSchedule.StartTimeUTC", Message: "Invalid time format, should be HH:MM"}
		}

		_, err = time.Parse("15:04", config.TradingSchedule.StopTimeUTC)
		if err != nil {
			return &ValidationError{Field: "TradingSchedule.StopTimeUTC", Message: "Invalid time format, should be HH:MM"}
		}
	}

	return nil
}

// ValidationError represents a config validation error
type ValidationError struct {
	Field   string
	Message string
}

func (e *ValidationError) Error() string {
	return "Validation error in " + e.Field + ": " + e.Message
}
