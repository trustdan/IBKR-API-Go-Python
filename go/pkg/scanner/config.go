package scanner

import (
	"encoding/json"
	"io/ioutil"
	"os"
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
}

// NewDefaultConfig creates a new configuration with default values
func NewDefaultConfig() *Config {
	return &Config{
		ServerAddress:    getEnvOrDefault("SERVER_ADDRESS", "0.0.0.0:50051"),
		MaxConcurrency:   getEnvIntOrDefault("MAX_CONCURRENCY", 50),
		DataProviderType: getEnvOrDefault("DATA_PROVIDER_TYPE", "mock"),
		APIKey:           getEnvOrDefault("API_KEY", ""),
		LogLevel:         getEnvOrDefault("LOG_LEVEL", "info"),
	}
}

// LoadConfig loads configuration from a JSON file
func LoadConfig(filePath string) (*Config, error) {
	config := NewDefaultConfig()

	// If file doesn't exist, use default config
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		logrus.Warnf("Config file %s not found, using defaults", filePath)
		return config, nil
	}

	// Read the file
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	// Parse JSON
	if err := json.Unmarshal(data, config); err != nil {
		return nil, err
	}

	return config, nil
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
