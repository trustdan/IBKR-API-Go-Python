package scanner

import (
	"runtime"
	"sync"
	"time"
)

// Metrics holds performance metrics for the scanner service
type Metrics struct {
	AvgScanTime      float64
	SymbolsPerSecond float64
	TotalScans       int
	MemoryUsage      float64 // MB
	CPUUsage         float64 // Percentage
}

// MetricTracker tracks performance metrics for the scanner service
type MetricTracker struct {
	mu sync.Mutex

	// Scan metrics
	scanTimes      []float64
	symbolsCounts  []int
	fetchTimes     []float64
	fetchedSymbols []int

	// Execution counts
	totalScans   int
	totalFetches int

	// Last metrics update time
	lastUpdate time.Time
}

// NewMetricTracker creates a new metrics tracker
func NewMetricTracker() *MetricTracker {
	return &MetricTracker{
		scanTimes:      make([]float64, 0, 100),
		symbolsCounts:  make([]int, 0, 100),
		fetchTimes:     make([]float64, 0, 100),
		fetchedSymbols: make([]int, 0, 100),
		lastUpdate:     time.Now(),
	}
}

// RecordScan records metrics for a scan operation
func (m *MetricTracker) RecordScan(symbolsCount int, scanTime float64) {
	m.mu.Lock()
	defer m.mu.Unlock()

	// Add to scan metrics
	m.scanTimes = append(m.scanTimes, scanTime)
	m.symbolsCounts = append(m.symbolsCounts, symbolsCount)

	// Limit array size to last 100 entries
	if len(m.scanTimes) > 100 {
		m.scanTimes = m.scanTimes[1:]
		m.symbolsCounts = m.symbolsCounts[1:]
	}

	// Increment total count
	m.totalScans++
}

// RecordFetch records metrics for a bulk fetch operation
func (m *MetricTracker) RecordFetch(symbolsCount int, fetchTime float64) {
	m.mu.Lock()
	defer m.mu.Unlock()

	// Add to fetch metrics
	m.fetchTimes = append(m.fetchTimes, fetchTime)
	m.fetchedSymbols = append(m.fetchedSymbols, symbolsCount)

	// Limit array size to last 100 entries
	if len(m.fetchTimes) > 100 {
		m.fetchTimes = m.fetchTimes[1:]
		m.fetchedSymbols = m.fetchedSymbols[1:]
	}

	// Increment total count
	m.totalFetches++
}

// GetMetrics returns current performance metrics
func (m *MetricTracker) GetMetrics() Metrics {
	m.mu.Lock()
	defer m.mu.Unlock()

	metrics := Metrics{
		AvgScanTime:      m.calculateAvgScanTime(),
		SymbolsPerSecond: m.calculateSymbolsPerSecond(),
		TotalScans:       m.totalScans,
		MemoryUsage:      m.getMemoryUsage(),
		CPUUsage:         0, // Not implemented in this version
	}

	m.lastUpdate = time.Now()
	return metrics
}

// calculateAvgScanTime calculates the average scan time over recent scans
func (m *MetricTracker) calculateAvgScanTime() float64 {
	if len(m.scanTimes) == 0 {
		return 0
	}

	sum := 0.0
	for _, t := range m.scanTimes {
		sum += t
	}

	return sum / float64(len(m.scanTimes))
}

// calculateSymbolsPerSecond calculates the average symbols processed per second
func (m *MetricTracker) calculateSymbolsPerSecond() float64 {
	if len(m.scanTimes) == 0 || len(m.symbolsCounts) == 0 {
		return 0
	}

	totalSymbols := 0
	totalTime := 0.0

	for i := range m.scanTimes {
		totalSymbols += m.symbolsCounts[i]
		totalTime += m.scanTimes[i]
	}

	if totalTime == 0 {
		return 0
	}

	return float64(totalSymbols) / totalTime
}

// getMemoryUsage returns current memory usage in MB
func (m *MetricTracker) getMemoryUsage() float64 {
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	// Convert to MB
	memUsageMB := float64(memStats.Alloc) / (1024 * 1024)

	return memUsageMB
}

