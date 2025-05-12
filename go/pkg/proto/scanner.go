// Package proto contains manually created stubs for protobuf definitions
// This is a temporary solution until protoc is installed
package proto

import (
	"context"
)

// UnimplementedScannerServiceServer is a placeholder implementation
type UnimplementedScannerServiceServer struct{}

// ScanMarket is a no-op implementation
func (s *UnimplementedScannerServiceServer) ScanMarket(context.Context, *ScanRequest) (*ScanResponse, error) {
	return nil, nil
}

// GetScanResults is a no-op implementation
func (s *UnimplementedScannerServiceServer) GetScanResults(context.Context, *ResultsRequest) (*ScanResponse, error) {
	return nil, nil
}

// ScannerServiceServer is the server API for ScannerService service
type ScannerServiceServer interface {
	// ScanMarket performs a full scan based on configured criteria
	ScanMarket(context.Context, *ScanRequest) (*ScanResponse, error)
	// GetScanResults retrieves the latest scan results
	GetScanResults(context.Context, *ResultsRequest) (*ScanResponse, error)
}

// ScanRequest represents a request to scan the market
type ScanRequest struct {
	Symbol   string   // Optional specific symbol to scan
	FullScan bool     // Whether to perform a full scan
	Criteria []string // Filtering criteria
}

// ResultsRequest is used to retrieve previous scan results
type ResultsRequest struct {
	Limit     int32 // Maximum number of results to return
	OlderThan int64 // Unix timestamp filter
}

// ScanResponse contains market scan results
type ScanResponse struct {
	Results   []*ScanResult
	Timestamp int64
	Status    string
}

// ScanResult represents a single opportunity found in the scan
type ScanResult struct {
	Symbol              string
	Price               float64
	Iv                  float64 // Implied volatility
	Options             []*OptionData
	Strategy            string
	PotentialProfit     float64
	MaxLoss             float64
	ProbabilityOfProfit float64
}

// OptionData contains details about a specific option
type OptionData struct {
	Contract   string
	Strike     float64
	Expiration string
	OptionType string // "CALL" or "PUT"
	Bid        float64
	Ask        float64
	Iv         float64
	Delta      float64
	Theta      float64
	Gamma      float64
	Vega       float64
}

// RegisterScannerServiceServer registers the server implementation
func RegisterScannerServiceServer(s interface{}, srv ScannerServiceServer) {
	// This is a stub function - in real code, this would register with gRPC
}
