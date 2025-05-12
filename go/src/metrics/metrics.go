package metrics

import (
	"sync"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/shirou/gopsutil/cpu"
)

// MetricsData contains performance metrics for the scanner
type MetricsData struct {
	AvgScanTime      float64
	SymbolsPerSecond float64
	TotalScans       int
	TotalFetches     int
	CPUUsage         float64
	ErrorCount       int
	CacheHitRate     float64
}

// MetricTracker tracks performance metrics for the scanner service
type MetricTracker struct {
	mu                sync.RWMutex
	scanTimes         []float64
	fetchTimes        []float64
	totalSymbols      int
	totalScans        int
	totalFetches      int
	errorCount        int
	cacheHits         int
	cacheRequests     int
	lastCPUCheckTime  time.Time
	lastCPUPercentage float64

	// Prometheus metrics
	scanDuration      prometheus.Histogram
	fetchDuration     prometheus.Histogram
	scanCounter       prometheus.Counter
	fetchCounter      prometheus.Counter
	errorCounter      prometheus.Counter
	symbolsScanned    prometheus.Counter
	symbolsPerSecond  prometheus.Gauge
	cacheHitRateGauge prometheus.Gauge
	memoryUsageGauge  prometheus.Gauge
	cpuUsageGauge     prometheus.Gauge
}

// NewMetricTracker creates a new metric tracker
func NewMetricTracker() *MetricTracker {
	// Register Prometheus metrics
	scanDuration := promauto.NewHistogram(prometheus.HistogramOpts{
		Name:    "scanner_scan_duration_seconds",
		Help:    "Duration of scan operations",
		Buckets: prometheus.ExponentialBuckets(0.01, 2, 10), // 0.01s to ~10s
	})

	fetchDuration := promauto.NewHistogram(prometheus.HistogramOpts{
		Name:    "scanner_fetch_duration_seconds",
		Help:    "Duration of fetch operations",
		Buckets: prometheus.ExponentialBuckets(0.01, 2, 10),
	})

	scanCounter := promauto.NewCounter(prometheus.CounterOpts{
		Name: "scanner_scan_total",
		Help: "Total number of scan operations",
	})

	fetchCounter := promauto.NewCounter(prometheus.CounterOpts{
		Name: "scanner_fetch_total",
		Help: "Total number of fetch operations",
	})

	errorCounter := promauto.NewCounter(prometheus.CounterOpts{
		Name: "scanner_errors_total",
		Help: "Total number of errors",
	})

	symbolsScanned := promauto.NewCounter(prometheus.CounterOpts{
		Name: "scanner_symbols_total",
		Help: "Total number of symbols scanned",
	})

	symbolsPerSecond := promauto.NewGauge(prometheus.GaugeOpts{
		Name: "scanner_symbols_per_second",
		Help: "Rate of symbols scanned per second",
	})

	cacheHitRateGauge := promauto.NewGauge(prometheus.GaugeOpts{
		Name: "scanner_cache_hit_rate",
		Help: "Cache hit rate percentage",
	})

	memoryUsageGauge := promauto.NewGauge(prometheus.GaugeOpts{
		Name: "scanner_memory_usage_bytes",
		Help: "Memory usage in bytes",
	})

	cpuUsageGauge := promauto.NewGauge(prometheus.GaugeOpts{
		Name: "scanner_cpu_usage_percent",
		Help: "CPU usage percentage",
	})

	return &MetricTracker{
		scanTimes:         make([]float64, 0, 100),
		fetchTimes:        make([]float64, 0, 100),
		lastCPUCheckTime:  time.Now(),
		scanDuration:      scanDuration,
		fetchDuration:     fetchDuration,
		scanCounter:       scanCounter,
		fetchCounter:      fetchCounter,
		errorCounter:      errorCounter,
		symbolsScanned:    symbolsScanned,
		symbolsPerSecond:  symbolsPerSecond,
		cacheHitRateGauge: cacheHitRateGauge,
		memoryUsageGauge:  memoryUsageGauge,
		cpuUsageGauge:     cpuUsageGauge,
	}
}

// RecordScan records metrics for a scan operation
func (m *MetricTracker) RecordScan(symbolCount int, scanTime float64) {
	m.mu.Lock()
	defer m.mu.Unlock()

	// Record scan time, keeping only the last 100 entries
	if len(m.scanTimes) >= 100 {
		m.scanTimes = m.scanTimes[1:]
	}
	m.scanTimes = append(m.scanTimes, scanTime)

	m.totalSymbols += symbolCount
	m.totalScans++

	// Update Prometheus metrics
	m.scanDuration.Observe(scanTime)
	m.scanCounter.Inc()
	m.symbolsScanned.Add(float64(symbolCount))

	if scanTime > 0 {
		symbolsPerSecond := float64(symbolCount) / scanTime
		m.symbolsPerSecond.Set(symbolsPerSecond)
	}

	// Update CPU usage metrics every 5 seconds
	if time.Since(m.lastCPUCheckTime) > 5*time.Second {
		m.updateCPUUsage()
	}
}

// RecordFetch records metrics for a fetch operation
func (m *MetricTracker) RecordFetch(symbolCount int, fetchTime float64) {
	m.mu.Lock()
	defer m.mu.Unlock()

	// Record fetch time, keeping only the last 100 entries
	if len(m.fetchTimes) >= 100 {
		m.fetchTimes = m.fetchTimes[1:]
	}
	m.fetchTimes = append(m.fetchTimes, fetchTime)

	m.totalFetches++

	// Update Prometheus metrics
	m.fetchDuration.Observe(fetchTime)
	m.fetchCounter.Inc()
}

// RecordCacheHit records a cache hit
func (m *MetricTracker) RecordCacheHit() {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.cacheHits++
	m.cacheRequests++

	// Update cache hit rate
	hitRate := float64(m.cacheHits) / float64(m.cacheRequests)
	m.cacheHitRateGauge.Set(hitRate * 100) // percentage
}

// RecordCacheMiss records a cache miss
func (m *MetricTracker) RecordCacheMiss() {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.cacheRequests++

	// Update cache hit rate
	hitRate := float64(m.cacheHits) / float64(m.cacheRequests)
	m.cacheHitRateGauge.Set(hitRate * 100) // percentage
}

// IncrementErrorCount increments the error counter
func (m *MetricTracker) IncrementErrorCount() {
	m.mu.Lock()
	defer m.mu.Unlock()

	m.errorCount++
	m.errorCounter.Inc()
}

// GetMetrics returns the current metrics
func (m *MetricTracker) GetMetrics() MetricsData {
	m.mu.RLock()
	defer m.mu.RUnlock()

	// Calculate average scan time
	var avgScanTime float64
	if len(m.scanTimes) > 0 {
		sum := 0.0
		for _, t := range m.scanTimes {
			sum += t
		}
		avgScanTime = sum / float64(len(m.scanTimes))
	}

	// Calculate symbols per second
	var symbolsPerSecond float64
	if m.totalScans > 0 && avgScanTime > 0 {
		symbolsPerSecond = float64(m.totalSymbols) / float64(m.totalScans) / avgScanTime
	}

	// Calculate cache hit rate
	var cacheHitRate float64
	if m.cacheRequests > 0 {
		cacheHitRate = float64(m.cacheHits) / float64(m.cacheRequests) * 100
	}

	return MetricsData{
		AvgScanTime:      avgScanTime,
		SymbolsPerSecond: symbolsPerSecond,
		TotalScans:       m.totalScans,
		TotalFetches:     m.totalFetches,
		CPUUsage:         m.lastCPUPercentage,
		ErrorCount:       m.errorCount,
		CacheHitRate:     cacheHitRate,
	}
}

// updateCPUUsage updates the CPU usage metric
func (m *MetricTracker) updateCPUUsage() {
	// Get CPU usage
	percent, err := cpu.Percent(0, false)
	if err == nil && len(percent) > 0 {
		m.lastCPUPercentage = percent[0]
		m.cpuUsageGauge.Set(m.lastCPUPercentage)
	}
	m.lastCPUCheckTime = time.Now()
}

