package scanner

import (
	"context"
	"sync"
	"time"

	"github.com/patrickmn/go-cache"
	"github.com/sirupsen/logrus"
	"github.com/trustdan/ibkr-trader/go/pkg/proto"
)

// ScannerService implements the proto.ScannerServiceServer interface
type ScannerService struct {
	proto.UnimplementedScannerServiceServer
	config       *Config
	resultsCache *cache.Cache
	lastScan     time.Time
	scanMutex    sync.Mutex
}

// NewScannerService creates a new scanner service instance
func NewScannerService(config *Config) *ScannerService {
	// Create cache with default expiration time from config
	resultsCache := cache.New(time.Duration(config.CacheTTL)*time.Minute, time.Duration(config.CacheTTL*2)*time.Minute)

	service := &ScannerService{
		config:       config,
		resultsCache: resultsCache,
		lastScan:     time.Time{},
	}

	return service
}

// ScanMarket performs a market scan based on the provided criteria
func (s *ScannerService) ScanMarket(ctx context.Context, req *proto.ScanRequest) (*proto.ScanResponse, error) {
	logrus.Infof("Received scan request for symbol: %s, full scan: %v", req.Symbol, req.FullScan)

	s.scanMutex.Lock()
	defer s.scanMutex.Unlock()

	// Perform market scan (placeholder implementation)
	results := s.performScan(req)

	// Update cache
	cacheKey := "latest_scan"
	s.resultsCache.Set(cacheKey, results, cache.DefaultExpiration)
	s.lastScan = time.Now()

	return &proto.ScanResponse{
		Results:   results,
		Timestamp: time.Now().Unix(),
		Status:    "success",
	}, nil
}

// GetScanResults retrieves the latest scan results
func (s *ScannerService) GetScanResults(ctx context.Context, req *proto.ResultsRequest) (*proto.ScanResponse, error) {
	logrus.Infof("Received request for scan results, limit: %d", req.Limit)

	// Get cached results
	cacheKey := "latest_scan"
	cachedResults, found := s.resultsCache.Get(cacheKey)

	var results []*proto.ScanResult
	status := "no_results"

	if found {
		results = cachedResults.([]*proto.ScanResult)
		status = "success"

		// Apply limit if specified
		if req.Limit > 0 && int(req.Limit) < len(results) {
			results = results[:req.Limit]
		}
	}

	return &proto.ScanResponse{
		Results:   results,
		Timestamp: s.lastScan.Unix(),
		Status:    status,
	}, nil
}

// performScan executes the actual market scanning logic
func (s *ScannerService) performScan(req *proto.ScanRequest) []*proto.ScanResult {
	// This would be replaced with actual IBKR API calls in a real implementation

	// Create some dummy data for testing
	results := []*proto.ScanResult{
		{
			Symbol:              "AAPL",
			Price:               175.23,
			Iv:                  0.32,
			Strategy:            "BULL_PUT_SPREAD",
			PotentialProfit:     0.45,
			MaxLoss:             1.55,
			ProbabilityOfProfit: 0.75,
			Options: []*proto.OptionData{
				{
					Contract:   "AAPL230917P170",
					Strike:     170.0,
					Expiration: "2023-09-17",
					OptionType: "PUT",
					Bid:        1.25,
					Ask:        1.30,
					Iv:         0.30,
					Delta:      -0.25,
					Theta:      -0.05,
					Gamma:      0.02,
					Vega:       0.10,
				},
				{
					Contract:   "AAPL230917P165",
					Strike:     165.0,
					Expiration: "2023-09-17",
					OptionType: "PUT",
					Bid:        0.80,
					Ask:        0.85,
					Iv:         0.28,
					Delta:      -0.18,
					Theta:      -0.04,
					Gamma:      0.015,
					Vega:       0.08,
				},
			},
		},
	}

	return results
}
