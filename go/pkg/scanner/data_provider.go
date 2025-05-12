package scanner

import (
	"math/rand"
	"time"
)

// DataProvider is an interface for retrieving market data
type DataProvider interface {
	// GetHistoricalData retrieves historical market data for a symbol
	GetHistoricalData(symbol, startDate, endDate string) (interface{}, error)
}

// MockDataProvider is a mock implementation of DataProvider for testing
type MockDataProvider struct {
	config *Config
}

// NewDataProvider creates a data provider based on configuration
func NewDataProvider(config *Config) DataProvider {
	// Based on configuration, return the appropriate data provider
	switch config.DataProviderType {
	case "mock":
		return &MockDataProvider{config: config}
	default:
		// Default to mock provider for now
		return &MockDataProvider{config: config}
	}
}

// GetHistoricalData returns mock historical data for testing
func (m *MockDataProvider) GetHistoricalData(symbol, startDate, endDate string) (interface{}, error) {
	// Simulate processing time
	time.Sleep(time.Duration(rand.Intn(100)) * time.Millisecond)

	// For testing, just return a mock data structure
	// In a real implementation, this would fetch actual market data
	mockData := struct {
		Symbol    string
		StartDate string
		EndDate   string
		Data      []float64
	}{
		Symbol:    symbol,
		StartDate: startDate,
		EndDate:   endDate,
		Data:      generateMockPriceData(30),
	}

	return mockData, nil
}

// generateMockPriceData creates random price data for testing
func generateMockPriceData(days int) []float64 {
	// Start with a base price between 50 and 200
	basePrice := 50.0 + rand.Float64()*150.0

	// Generate daily prices with random fluctuations
	prices := make([]float64, days)
	currentPrice := basePrice

	for i := 0; i < days; i++ {
		// Random daily change between -2% and +2%
		change := (rand.Float64()*4.0 - 2.0) / 100.0
		currentPrice = currentPrice * (1.0 + change)
		prices[i] = currentPrice
	}

	return prices
}

// Initialize random seed
func init() {
	rand.Seed(time.Now().UnixNano())
}

