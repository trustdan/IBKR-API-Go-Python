package scanner

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strconv"

	"github.com/sirupsen/logrus"
)

// Config holds configuration for the scanner service
type Config struct {
	// Server configuration
	ServerAddress string `json:"server_address"`

	// Performance configuration
	MaxConcurrency int `json:"max_concurrency"`

	// Data provider configuration
	DataProviderType string `json:"data_provider_type"`
	APIKey           string `json:"api_key"`

	// Logging configuration
	LogLevel string `json:"log_level"`

	// Cache configuration
	CacheTTL     int `json:"cache_ttl"`
	ScanInterval int `json:"scan_interval"`
}

// NewDefaultConfig creates a new configuration with default values
func NewDefaultConfig() *Config {
	return &Config{
		ServerAddress:    getEnvOrDefault("SERVER_ADDRESS", "0.0.0.0:50051"),
		MaxConcurrency:   getEnvIntOrDefault("MAX_CONCURRENCY", 50),
		DataProviderType: getEnvOrDefault("DATA_PROVIDER_TYPE", "mock"),
		APIKey:           getEnvOrDefault("API_KEY", ""),
		LogLevel:         getEnvOrDefault("LOG_LEVEL", "info"),
		CacheTTL:         getEnvIntOrDefault("CACHE_TTL", 15),
		ScanInterval:     getEnvIntOrDefault("SCAN_INTERVAL", 5),
	}
}

// LoadConfig loads the scanner service configuration from a JSON file
func LoadConfig(configPath string) (*Config, error) {
	// Resolve relative path if needed
	if !filepath.IsAbs(configPath) {
		workDir, err := os.Getwd()
		if err != nil {
			return nil, err
		}
		configPath = filepath.Join(workDir, configPath)
	}

	logrus.Infof("Loading configuration from: %s", configPath)

	// Read the configuration file
	configData, err := os.ReadFile(configPath)
	if err != nil {
		return nil, err
	}

	// Parse the JSON data
	var config Config
	if err := json.Unmarshal(configData, &config); err != nil {
		return nil, err
	}

	// Set defaults for empty values
	if config.ServerAddress == "" {
		config.ServerAddress = ":50051"
	}

	if config.LogLevel == "" {
		config.LogLevel = "info"
	}

	if config.CacheTTL == 0 {
		config.CacheTTL = 15 // 15 minutes default
	}

	if config.ScanInterval == 0 {
		config.ScanInterval = 5 // 5 minutes default
	}

	return &config, nil
}

// getEnvOrDefault gets an environment variable or returns a default value
func getEnvOrDefault(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}

// getEnvIntOrDefault gets an environment variable as int or returns a default value
func getEnvIntOrDefault(key string, defaultValue int) int {
	if value, exists := os.LookupEnv(key); exists {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
		logrus.Warnf("Invalid integer value for %s: %s, using default %d", key, value, defaultValue)
	}
	return defaultValue
}

