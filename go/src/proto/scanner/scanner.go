// Package scanner contains manually created stubs for the scanner.proto definitions
// This is a temporary solution until protoc is installed and configured
package scanner

import (
	"context"
)

// UnimplementedScannerServiceServer is a placeholder implementation
type UnimplementedScannerServiceServer struct{}

// Scan is a no-op implementation
func (s *UnimplementedScannerServiceServer) Scan(context.Context, *ScanRequest) (*ScanResponse, error) {
	return nil, nil
}

// BulkFetch is a no-op implementation
func (s *UnimplementedScannerServiceServer) BulkFetch(context.Context, *BulkFetchRequest) (*BulkFetchResponse, error) {
	return nil, nil
}

// GetMetrics is a no-op implementation
func (s *UnimplementedScannerServiceServer) GetMetrics(context.Context, *MetricsRequest) (*MetricsResponse, error) {
	return nil, nil
}

// ScannerServiceServer is the server API for ScannerService service
type ScannerServiceServer interface {
	// Scan performs a market scan based on provided criteria
	Scan(context.Context, *ScanRequest) (*ScanResponse, error)
	// BulkFetch retrieves market data for multiple symbols
	BulkFetch(context.Context, *BulkFetchRequest) (*BulkFetchResponse, error)
	// GetMetrics retrieves performance metrics for the scanner service
	GetMetrics(context.Context, *MetricsRequest) (*MetricsResponse, error)
}

// ScanRequest represents a request to scan the market
type ScanRequest struct {
	Symbols    []string
	Strategies []string
	DateRange  *DateRange
}

// DateRange specifies a date range for data
type DateRange struct {
	StartDate string
	EndDate   string
}

// BulkFetchRequest is used to fetch historical data for multiple symbols
type BulkFetchRequest struct {
	Symbols   []string
	DateRange *DateRange
}

// BulkFetchResponse contains historical market data for multiple symbols
type BulkFetchResponse struct {
	Data             map[string][]byte
	FetchTimeSeconds float32
}

// ScanResponse contains market scan results
type ScanResponse struct {
	Signals         map[string]*SignalList
	ScanTimeSeconds float32
}

// SignalList represents a list of trading signals
type SignalList struct {
	SignalTypes []string
}

// MetricsRequest is used to retrieve performance metrics
type MetricsRequest struct {
	// Empty for now
}

// MetricsResponse contains performance metrics for the scanner service
type MetricsResponse struct {
	AvgScanTimeSeconds float32
	SymbolsPerSecond   float32
	TotalScans         int32
	MemoryUsageMb      float32
	CpuUsagePercent    float32
	ErrorCount         int32
	CacheHitRate       float32
}

// RegisterScannerServiceServer registers the server implementation
func RegisterScannerServiceServer(s interface{}, srv ScannerServiceServer) {
	// This is a stub function - in real code, this would register with gRPC
}

