package main

import (
	"context"
	"encoding/json"
	"flag"
	"net"
	"net/http"
	"os"
	"runtime"
	"runtime/pprof"
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/sirupsen/logrus"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"

	"github.com/yourusername/auto-vertical-spread-trader/go/src/config"
	"github.com/yourusername/auto-vertical-spread-trader/go/src/metrics"
	pb "github.com/yourusername/auto-vertical-spread-trader/go/src/proto/scanner"
)

// ScannerService implements the gRPC scanner service
type ScannerService struct {
	pb.UnimplementedScannerServiceServer
	config        *config.Config
	dataProvider  DataProvider
	metricTracker *metrics.MetricTracker
	workPool      chan struct{}
}

// NewScannerService creates a new scanner service
func NewScannerService(cfg *config.Config) *ScannerService {
	return &ScannerService{
		config:        cfg,
		dataProvider:  NewDataProvider(cfg),
		metricTracker: metrics.NewMetricTracker(),
		// Create a worker pool with configurable size
		workPool: make(chan struct{}, cfg.MaxConcurrency),
	}
}

// Scan implements the Scan RPC method
func (s *ScannerService) Scan(ctx context.Context, req *pb.ScanRequest) (*pb.ScanResponse, error) {
	startTime := time.Now()

	// Create result map with capacity hint for better performance
	signals := make(map[string]*pb.SignalList, len(req.Symbols))
	var mu sync.Mutex

	// Use errgroup for better error handling
	var wg sync.WaitGroup

	// Process each symbol concurrently
	for _, symbol := range req.Symbols {
		// Context cancellation check
		if ctx.Err() != nil {
			return nil, ctx.Err()
		}

		wg.Add(1)

		// Add job to worker pool - non-blocking select to prevent deadlocks
		select {
		case s.workPool <- struct{}{}:
		case <-ctx.Done():
			wg.Done()
			return nil, ctx.Err()
		}

		go func(sym string) {
			defer wg.Done()
			defer func() { <-s.workPool }() // Release worker

			// Fetch data for this symbol with timeout context
			symbolCtx, cancel := context.WithTimeout(ctx, s.config.SymbolTimeout)
			defer cancel()

			data, err := s.dataProvider.GetHistoricalData(symbolCtx, sym, req.DateRange.StartDate, req.DateRange.EndDate)
			if err != nil {
				logrus.Errorf("Error fetching data for %s: %v", sym, err)
				s.metricTracker.IncrementErrorCount()
				return
			}

			// Apply strategies with optimized concurrent indicator calculation
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

	// Calculate scan time
	scanTime := time.Since(startTime).Seconds()

	// Track metrics
	s.metricTracker.RecordScan(len(req.Symbols), scanTime)

	return &pb.ScanResponse{
		Signals:         signals,
		ScanTimeSeconds: float32(scanTime),
	}, nil
}

// BulkFetch implements the BulkFetch RPC method
func (s *ScannerService) BulkFetch(ctx context.Context, req *pb.BulkFetchRequest) (*pb.BulkFetchResponse, error) {
	startTime := time.Now()

	// Create result map with capacity hint
	data := make(map[string][]byte, len(req.Symbols))
	var mu sync.Mutex

	// Shared pool of buffers to reduce memory allocations
	bufferPool := sync.Pool{
		New: func() interface{} {
			// Pre-allocate reasonably sized buffer
			return make([]byte, 0, 32*1024)
		},
	}

	var wg sync.WaitGroup

	// Process each symbol concurrently
	for _, symbol := range req.Symbols {
		// Context cancellation check
		if ctx.Err() != nil {
			return nil, ctx.Err()
		}

		wg.Add(1)

		// Add job to worker pool
		select {
		case s.workPool <- struct{}{}:
		case <-ctx.Done():
			wg.Done()
			return nil, ctx.Err()
		}

		go func(sym string) {
			defer wg.Done()
			defer func() { <-s.workPool }() // Release worker

			// Fetch data for this symbol with timeout
			symbolCtx, cancel := context.WithTimeout(ctx, s.config.SymbolTimeout)
			defer cancel()

			marketData, err := s.dataProvider.GetHistoricalData(symbolCtx, sym, req.DateRange.StartDate, req.DateRange.EndDate)
			if err != nil {
				logrus.Errorf("Error fetching data for %s: %v", sym, err)
				s.metricTracker.IncrementErrorCount()
				return
			}

			// Get buffer from pool
			buffer := bufferPool.Get().([]byte)
			buffer = buffer[:0] // Reset buffer but keep capacity

			// Serialize the data with optimized buffer
			serialized, err := s.serializeMarketData(marketData, buffer)
			if err != nil {
				logrus.Errorf("Error serializing data for %s: %v", sym, err)
				bufferPool.Put(buffer) // Return buffer to pool
				s.metricTracker.IncrementErrorCount()
				return
			}

			// Store in result map
			mu.Lock()
			data[sym] = serialized
			mu.Unlock()

			// Return buffer to pool for future reuse
			bufferPool.Put(buffer)
		}(symbol)
	}

	// Wait for all goroutines to complete
	wg.Wait()

	// Calculate fetch time
	fetchTime := time.Since(startTime).Seconds()

	// Track metrics
	s.metricTracker.RecordFetch(len(req.Symbols), fetchTime)

	return &pb.BulkFetchResponse{
		Data:             data,
		FetchTimeSeconds: float32(fetchTime),
	}, nil
}

// GetMetrics implements the GetMetrics RPC method
func (s *ScannerService) GetMetrics(ctx context.Context, req *pb.MetricsRequest) (*pb.MetricsResponse, error) {
	metrics := s.metricTracker.GetMetrics()

	// Get additional system metrics
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	return &pb.MetricsResponse{
		AvgScanTimeSeconds: float32(metrics.AvgScanTime),
		SymbolsPerSecond:   float32(metrics.SymbolsPerSecond),
		TotalScans:         int32(metrics.TotalScans),
		MemoryUsageMb:      float32(memStats.Alloc) / 1024 / 1024,
		CpuUsagePercent:    float32(metrics.CPUUsage),
		ErrorCount:         int32(metrics.ErrorCount),
		CacheHitRate:       float32(metrics.CacheHitRate),
	}, nil
}

// evaluateStrategies evaluates all requested strategies on the provided data
func (s *ScannerService) evaluateStrategies(data interface{}, strategies []string) []string {
	// Create a channel for collecting signals from all strategies
	signalChan := make(chan string, len(strategies))

	// Launch concurrent evaluation of all strategies
	var wg sync.WaitGroup
	for _, strategy := range strategies {
		wg.Add(1)
		go func(strat string) {
			defer wg.Done()

			// Evaluate the strategy
			signal := s.evaluateStrategy(data, strat)
			if signal != "" {
				signalChan <- signal
			}
		}(strategy)
	}

	// Wait for all strategy evaluations to complete
	wg.Wait()
	close(signalChan)

	// Collect results
	var signals []string
	for signal := range signalChan {
		signals = append(signals, signal)
	}

	return signals
}

// evaluateStrategy evaluates a single strategy
func (s *ScannerService) evaluateStrategy(data interface{}, strategy string) string {
	// Implementation depends on the strategy
	// This would call the specific strategy implementation

	// For demonstration purposes
	switch strategy {
	case "HIGH_BASE":
		return "LONG"
	case "LOW_BASE":
		return "SHORT"
	default:
		return ""
	}
}

// serializeMarketData serializes market data to an optimized binary format
func (s *ScannerService) serializeMarketData(data interface{}, buffer []byte) ([]byte, error) {
	// For demonstration, using JSON but in production would use a more
	// efficient format like Protocol Buffers or FlatBuffers
	return json.Marshal(data)
}

func main() {
	// Command line flags
	cpuProfile := flag.String("cpuprofile", "", "write cpu profile to file")
	memProfile := flag.String("memprofile", "", "write memory profile to file")
	configPath := flag.String("config", "config.yaml", "path to config file")
	flag.Parse()

	// CPU profiling if enabled
	if *cpuProfile != "" {
		f, err := os.Create(*cpuProfile)
		if err != nil {
			logrus.Fatalf("could not create CPU profile: %v", err)
		}
		defer f.Close()
		if err := pprof.StartCPUProfile(f); err != nil {
			logrus.Fatalf("could not start CPU profile: %v", err)
		}
		defer pprof.StopCPUProfile()
	}

	// Load configuration
	cfg, err := config.LoadConfig(*configPath)
	if err != nil {
		logrus.Fatalf("Failed to load configuration: %v", err)
	}

	// Configure logging
	logrus.SetFormatter(&logrus.JSONFormatter{})
	if cfg.Debug {
		logrus.SetLevel(logrus.DebugLevel)
	}

	// Create scanner service
	service := NewScannerService(cfg)

	// Create gRPC server with performance tuning
	grpcOptions := []grpc.ServerOption{
		grpc.MaxConcurrentStreams(uint32(cfg.MaxConcurrentStreams)),
		grpc.MaxRecvMsgSize(cfg.MaxMessageSize),
		grpc.MaxSendMsgSize(cfg.MaxMessageSize),
	}
	server := grpc.NewServer(grpcOptions...)
	pb.RegisterScannerServiceServer(server, service)

	// Enable reflection for debugging
	if cfg.Debug {
		reflection.Register(server)
	}

	// Start Prometheus metrics server
	go func() {
		http.Handle("/metrics", promhttp.Handler())
		metricsAddr := cfg.MetricsHost + ":" + cfg.MetricsPort
		logrus.Infof("Starting metrics server on %s", metricsAddr)
		if err := http.ListenAndServe(metricsAddr, nil); err != nil {
			logrus.Errorf("Failed to start metrics server: %v", err)
		}
	}()

	// Start gRPC server
	lis, err := net.Listen("tcp", cfg.ServerHost+":"+cfg.ServerPort)
	if err != nil {
		logrus.Fatalf("Failed to listen: %v", err)
	}

	logrus.Infof("Starting scanner service on %s:%s", cfg.ServerHost, cfg.ServerPort)
	if err := server.Serve(lis); err != nil {
		logrus.Fatalf("Failed to serve: %v", err)
	}

	// Memory profiling if enabled
	if *memProfile != "" {
		f, err := os.Create(*memProfile)
		if err != nil {
			logrus.Fatalf("could not create memory profile: %v", err)
		}
		defer f.Close()
		runtime.GC() // get up-to-date statistics
		if err := pprof.WriteHeapProfile(f); err != nil {
			logrus.Fatalf("could not write memory profile: %v", err)
		}
	}
}
