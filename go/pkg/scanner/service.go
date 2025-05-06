package scanner

import (
	"context"
	"sync"
	"time"

	"github.com/sirupsen/logrus"
	pb "github.com/yourusername/ibkr-trader/pkg/proto"
)

// ScannerService implements the gRPC ScannerService interface
type ScannerService struct {
	pb.UnimplementedScannerServiceServer
	config        *Config
	dataProvider  DataProvider
	metricTracker *MetricTracker
}

// NewScannerService creates a new scanner service with the given configuration
func NewScannerService(config *Config) *ScannerService {
	return &ScannerService{
		config:        config,
		dataProvider:  NewDataProvider(config),
		metricTracker: NewMetricTracker(),
	}
}

// Scan implements the Scan RPC method
func (s *ScannerService) Scan(ctx context.Context, req *pb.ScanRequest) (*pb.ScanResponse, error) {
	startTime := time.Now()

	logrus.Infof("Scanning %d symbols", len(req.Symbols))

	// Create result map
	signals := make(map[string]*pb.SignalList)
	var mu sync.Mutex

	// Create a worker pool to limit concurrency
	workerPool := make(chan struct{}, s.config.MaxConcurrency)
	var wg sync.WaitGroup

	// Process each symbol concurrently
	for _, symbol := range req.Symbols {
		wg.Add(1)

		// Add job to worker pool
		workerPool <- struct{}{}

		go func(sym string) {
			defer wg.Done()
			defer func() { <-workerPool }() // Release worker

			// Check for context cancellation
			if ctx.Err() != nil {
				logrus.Warnf("Context cancelled while processing %s", sym)
				return
			}

			// Fetch data for this symbol
			data, err := s.dataProvider.GetHistoricalData(sym, req.DateRange.StartDate, req.DateRange.EndDate)
			if err != nil {
				logrus.Errorf("Error fetching data for %s: %v", sym, err)
				return
			}

			// Apply strategies
			signalTypes := s.evaluateStrategies(data, req.Strategies)

			// Store results with mutex to avoid race conditions
			if len(signalTypes) > 0 {
				mu.Lock()
				signals[sym] = &pb.SignalList{SignalTypes: signalTypes}
				mu.Unlock()
			}
		}(symbol)
	}

	// Wait for all goroutines to complete
	wg.Wait()
	close(workerPool)

	// Calculate scan time
	scanTime := time.Since(startTime).Seconds()

	// Track metrics
	s.metricTracker.RecordScan(len(req.Symbols), scanTime)

	logrus.Infof("Scan completed in %.2f seconds, found signals for %d symbols", scanTime, len(signals))

	return &pb.ScanResponse{
		Signals:         signals,
		ScanTimeSeconds: float32(scanTime),
	}, nil
}

// BulkFetch implements the BulkFetch RPC method
func (s *ScannerService) BulkFetch(ctx context.Context, req *pb.BulkFetchRequest) (*pb.BulkFetchResponse, error) {
	startTime := time.Now()

	logrus.Infof("Bulk fetching data for %d symbols", len(req.Symbols))

	// Create result map
	data := make(map[string][]byte)
	var mu sync.Mutex

	// Create a worker pool
	workerPool := make(chan struct{}, s.config.MaxConcurrency)
	var wg sync.WaitGroup

	// Process each symbol concurrently
	for _, symbol := range req.Symbols {
		wg.Add(1)

		// Add job to worker pool
		workerPool <- struct{}{}

		go func(sym string) {
			defer wg.Done()
			defer func() { <-workerPool }() // Release worker

			// Check for context cancellation
			if ctx.Err() != nil {
				logrus.Warnf("Context cancelled while processing %s", sym)
				return
			}

			// Fetch data for this symbol
			marketData, err := s.dataProvider.GetHistoricalData(sym, req.DateRange.StartDate, req.DateRange.EndDate)
			if err != nil {
				logrus.Errorf("Error fetching data for %s: %v", sym, err)
				return
			}

			// Serialize the data
			serialized, err := s.serializeMarketData(marketData)
			if err != nil {
				logrus.Errorf("Error serializing data for %s: %v", sym, err)
				return
			}

			// Store in result map
			mu.Lock()
			data[sym] = serialized
			mu.Unlock()
		}(symbol)
	}

	// Wait for all goroutines to complete
	wg.Wait()
	close(workerPool)

	// Calculate fetch time
	fetchTime := time.Since(startTime).Seconds()

	// Track metrics
	s.metricTracker.RecordFetch(len(req.Symbols), fetchTime)

	logrus.Infof("Bulk fetch completed in %.2f seconds for %d symbols", fetchTime, len(data))

	return &pb.BulkFetchResponse{
		Data:             data,
		FetchTimeSeconds: float32(fetchTime),
	}, nil
}

// GetMetrics implements the GetMetrics RPC method
func (s *ScannerService) GetMetrics(ctx context.Context, req *pb.MetricsRequest) (*pb.MetricsResponse, error) {
	metrics := s.metricTracker.GetMetrics()

	return &pb.MetricsResponse{
		AvgScanTimeSeconds: float32(metrics.AvgScanTime),
		SymbolsPerSecond:   float32(metrics.SymbolsPerSecond),
		TotalScans:         int32(metrics.TotalScans),
		MemoryUsageMb:      float32(metrics.MemoryUsage),
		CpuUsagePercent:    float32(metrics.CPUUsage),
	}, nil
}

// evaluateStrategies applies the requested strategies to the market data
func (s *ScannerService) evaluateStrategies(data interface{}, strategies []string) []string {
	// This is a placeholder implementation
	// In a real implementation, we would:
	// 1. Parse the market data into a common format
	// 2. Calculate indicators needed for each strategy
	// 3. Apply each strategy's rules to generate signals

	// For now, return a placeholder signal for demonstration
	return []string{"LONG"}
}

// serializeMarketData converts market data to bytes for transmission
func (s *ScannerService) serializeMarketData(data interface{}) ([]byte, error) {
	// This is a placeholder implementation
	// In a real implementation, we would:
	// 1. Convert the market data to a well-defined format
	// 2. Serialize it using gob, protobuf, or JSON

	// For now, return empty bytes for demonstration
	return []byte{}, nil
}
