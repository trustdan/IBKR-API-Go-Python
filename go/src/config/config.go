package config

import (
	"io/ioutil"
	"log"
	"sync/atomic"
	"time"

	"github.com/fsnotify/fsnotify"
	"gopkg.in/yaml.v3"
)

// Config holds the configuration for the scanner service
type Config struct {
	// Server settings
	ServerHost string `yaml:"server_host"`
	ServerPort string `yaml:"server_port"`

	// Metrics server settings
	MetricsHost string `yaml:"metrics_host"`
	MetricsPort string `yaml:"metrics_port"`

	// Performance settings
	MaxConcurrency       int           `yaml:"max_concurrency"`
	MaxConcurrentStreams int           `yaml:"max_concurrent_streams"`
	MaxMessageSize       int           `yaml:"max_message_size"`
	SymbolTimeout        time.Duration `yaml:"symbol_timeout"`

	// Caching settings
	CacheEnabled         bool          `yaml:"cache_enabled"`
	CacheTTL             time.Duration `yaml:"cache_ttl"`
	CacheCleanupInterval time.Duration `yaml:"cache_cleanup_interval"`
	MaxCachedItems       int           `yaml:"max_cached_items"`

	// Data provider settings
	DataProviderType  string `yaml:"data_provider_type"`
	DataProviderURL   string `yaml:"data_provider_url"`
	DataProviderToken string `yaml:"data_provider_token"`

	// Debug settings
	Debug            bool   `yaml:"debug"`
	TracingEnabled   bool   `yaml:"tracing_enabled"`
	ProfilerEnabled  bool   `yaml:"profiler_enabled"`
	ProfilerEndpoint string `yaml:"profiler_endpoint"`
}

// Global atomic pointer to the current configuration
var globalConfig atomic.Pointer[Config]

// LoadConfig loads the configuration from a YAML file
func LoadConfig(configFile string) (*Config, error) {
	// Set default values
	config := &Config{
		ServerHost:           "0.0.0.0",
		ServerPort:           "50051",
		MetricsHost:          "0.0.0.0",
		MetricsPort:          "9090",
		MaxConcurrency:       50,
		MaxConcurrentStreams: 100,
		MaxMessageSize:       10 * 1024 * 1024, // 10MB
		SymbolTimeout:        5 * time.Second,
		CacheEnabled:         true,
		CacheTTL:             5 * time.Minute,
		CacheCleanupInterval: 1 * time.Minute,
		MaxCachedItems:       10000,
		DataProviderType:     "mock",
		Debug:                false,
		TracingEnabled:       false,
		ProfilerEnabled:      false,
		ProfilerEndpoint:     "/debug/pprof",
	}

	// Read config file
	data, err := ioutil.ReadFile(configFile)
	if err != nil {
		return config, err
	}

	// Parse YAML
	err = yaml.Unmarshal(data, config)
	if err != nil {
		return config, err
	}

	// Store the config in the atomic pointer
	globalConfig.Store(config)

	return config, nil
}

// DefaultConfig returns the default configuration
func DefaultConfig() *Config {
	return &Config{
		ServerHost:           "0.0.0.0",
		ServerPort:           "50051",
		MetricsHost:          "0.0.0.0",
		MetricsPort:          "9090",
		MaxConcurrency:       50,
		MaxConcurrentStreams: 100,
		MaxMessageSize:       10 * 1024 * 1024, // 10MB
		SymbolTimeout:        5 * time.Second,
		CacheEnabled:         true,
		CacheTTL:             5 * time.Minute,
		CacheCleanupInterval: 1 * time.Minute,
		MaxCachedItems:       10000,
		DataProviderType:     "mock",
		Debug:                false,
		TracingEnabled:       false,
		ProfilerEnabled:      false,
		ProfilerEndpoint:     "/debug/pprof",
	}
}

// GetConfig returns the current global configuration
func GetConfig() *Config {
	cfg := globalConfig.Load()
	if cfg == nil {
		// If no config is loaded yet, load default
		defaultCfg := DefaultConfig()
		globalConfig.Store(defaultCfg)
		return defaultCfg
	}
	return cfg
}

// WatchConfig watches for changes to the config file and automatically reloads
func WatchConfig(configFile string) error {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		return err
	}

	go func() {
		defer watcher.Close()
		for {
			select {
			case event, ok := <-watcher.Events:
				if !ok {
					return
				}
				if event.Op&fsnotify.Write == fsnotify.Write {
					log.Printf("Config file changed: %s", event.Name)
					if cfg, err := LoadConfig(configFile); err == nil {
						log.Println("Configuration reloaded successfully")
						globalConfig.Store(cfg)
					} else {
						log.Printf("Error reloading config: %v", err)
					}
				}
			case err, ok := <-watcher.Errors:
				if !ok {
					return
				}
				log.Printf("Config watcher error: %v", err)
			}
		}
	}()

	// Add the config file to the watcher
	err = watcher.Add(configFile)
	if err != nil {
		return err
	}

	log.Printf("Watching config file: %s", configFile)
	return nil
}
