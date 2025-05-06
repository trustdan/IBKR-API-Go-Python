package main

import (
	"context"
	"sync"
	"time"

	"github.com/patrickmn/go-cache"
	"github.com/sirupsen/logrus"
	"github.com/yourusername/auto-vertical-spread-trader/go/src/config"
)

// MarketData represents stock market data
type MarketData struct {
	Symbol     string      `json:"symbol"`
	Timestamp  time.Time   `json:"timestamp"`
	Open       float64     `json:"open"`
	High       float64     `json:"high"`
	Low        float64     `json:"low"`
	Close      float64     `json:"close"`
	Volume     int64       `json:"volume"`
	Indicators interface{} `json:"indicators,omitempty"`
}

// DataProvider defines the interface for getting historical market data
type DataProvider interface {
	// GetHistoricalData retrieves historical market data for a symbol
	GetHistoricalData(ctx context.Context, symbol, startDate, endDate string) ([]MarketData, error)
}

// CachedDataProvider implements the DataProvider interface with caching support
type CachedDataProvider struct {
	config        *config.Config
	dataProvider  DataProvider
	cache         *cache.Cache
	cacheHits     int
	cacheMisses   int
	mu            sync.RWMutex
	metricTracker MetricRecorder
}

// MetricRecorder defines the interface for recording metrics
type MetricRecorder interface {
	RecordCacheHit()
	RecordCacheMiss()
}

// NewDataProvider creates a new data provider with the specified configuration
func NewDataProvider(cfg *config.Config) DataProvider {
	// Create the base data provider
	var provider DataProvider
	switch cfg.DataProviderType {
	case "mock":
		provider = NewMockDataProvider(cfg)
	case "yahoo":
		provider = NewYahooDataProvider(cfg)
	case "ibkr":
		provider = NewIBKRDataProvider(cfg)
	default:
		logrus.Warnf("Unknown data provider type: %s, using mock", cfg.DataProviderType)
		provider = NewMockDataProvider(cfg)
	}

	// If caching is enabled, wrap the provider with a cache
	if cfg.CacheEnabled {
		return NewCachedDataProvider(cfg, provider, nil)
	}

	return provider
}

// NewCachedDataProvider creates a new cached data provider
func NewCachedDataProvider(cfg *config.Config, provider DataProvider, metricTracker MetricRecorder) *CachedDataProvider {
	return &CachedDataProvider{
		config:        cfg,
		dataProvider:  provider,
		cache:         cache.New(cfg.CacheTTL, cfg.CacheCleanupInterval),
		metricTracker: metricTracker,
	}
}

// GetHistoricalData retrieves historical market data with caching
func (c *CachedDataProvider) GetHistoricalData(ctx context.Context, symbol, startDate, endDate string) ([]MarketData, error) {
	// Create cache key
	cacheKey := symbol + ":" + startDate + ":" + endDate

	// Check if data is in cache
	if data, found := c.cache.Get(cacheKey); found {
		c.mu.Lock()
		c.cacheHits++
		c.mu.Unlock()

		if c.metricTracker != nil {
			c.metricTracker.RecordCacheHit()
		}

		return data.([]MarketData), nil
	}

	// Data not in cache, fetch from provider
	c.mu.Lock()
	c.cacheMisses++
	c.mu.Unlock()

	if c.metricTracker != nil {
		c.metricTracker.RecordCacheMiss()
	}

	data, err := c.dataProvider.GetHistoricalData(ctx, symbol, startDate, endDate)
	if err != nil {
		return nil, err
	}

	// Store in cache
	c.cache.Set(cacheKey, data, cache.DefaultExpiration)

	return data, nil
}

// MockDataProvider implements the DataProvider interface for testing
type MockDataProvider struct {
	config *config.Config
}

// NewMockDataProvider creates a new mock data provider
func NewMockDataProvider(cfg *config.Config) *MockDataProvider {
	return &MockDataProvider{
		config: cfg,
	}
}

// GetHistoricalData generates mock historical data
func (m *MockDataProvider) GetHistoricalData(ctx context.Context, symbol, startDate, endDate string) ([]MarketData, error) {
	// Parse start and end dates
	start, err := time.Parse("2006-01-02", startDate)
	if err != nil {
		start = time.Now().AddDate(0, -1, 0) // Default to 1 month ago
	}

	end, err := time.Parse("2006-01-02", endDate)
	if err != nil {
		end = time.Now() // Default to today
	}

	// Generate mock data
	data := make([]MarketData, 0)
	price := 100.0 // Starting price

	for d := start; d.Before(end) || d.Equal(end); d = d.AddDate(0, 0, 1) {
		// Skip weekends
		if d.Weekday() == time.Saturday || d.Weekday() == time.Sunday {
			continue
		}

		// Add some randomness to the price
		changePercent := (float64(d.Nanosecond()%200) - 100) / 1000 // -10% to +10%
		price = price * (1 + changePercent)

		// Create a data point
		marketData := MarketData{
			Symbol:    symbol,
			Timestamp: d,
			Open:      price * 0.99,
			High:      price * 1.02,
			Low:       price * 0.98,
			Close:     price,
			Volume:    int64(1000000 + d.Nanosecond()%1000000),
		}

		data = append(data, marketData)
	}

	return data, nil
}

// YahooDataProvider implements the DataProvider interface using Yahoo Finance
type YahooDataProvider struct {
	config *config.Config
}

// NewYahooDataProvider creates a new Yahoo Finance data provider
func NewYahooDataProvider(cfg *config.Config) *YahooDataProvider {
	return &YahooDataProvider{
		config: cfg,
	}
}

// GetHistoricalData retrieves historical data from Yahoo Finance
func (y *YahooDataProvider) GetHistoricalData(ctx context.Context, symbol, startDate, endDate string) ([]MarketData, error) {
	// In a real implementation, this would use the Yahoo Finance API
	// For now, return mock data
	logrus.Info("Yahoo Finance API not implemented, using mock data")
	mockProvider := NewMockDataProvider(y.config)
	return mockProvider.GetHistoricalData(ctx, symbol, startDate, endDate)
}

// IBKRDataProvider implements the DataProvider interface using Interactive Brokers
type IBKRDataProvider struct {
	config *config.Config
}

// NewIBKRDataProvider creates a new IBKR data provider
func NewIBKRDataProvider(cfg *config.Config) *IBKRDataProvider {
	return &IBKRDataProvider{
		config: cfg,
	}
}

// GetHistoricalData retrieves historical data from Interactive Brokers
func (i *IBKRDataProvider) GetHistoricalData(ctx context.Context, symbol, startDate, endDate string) ([]MarketData, error) {
	// In a real implementation, this would use the IBKR API
	// For now, return mock data
	logrus.Info("IBKR API not implemented, using mock data")
	mockProvider := NewMockDataProvider(i.config)
	return mockProvider.GetHistoricalData(ctx, symbol, startDate, endDate)
}
