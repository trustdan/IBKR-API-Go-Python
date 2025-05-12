package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"sync/atomic"
	"syscall"
	"time"

	"github.com/BurntSushi/toml"
	"github.com/fsnotify/fsnotify"
)

// Config represents the application configuration
type Config struct {
	IBKR struct {
		Host     string `toml:"host"`
		Port     int    `toml:"port"`
		ClientID int    `toml:"client_id"`
		ReadOnly bool   `toml:"read_only"`
	} `toml:"ibkr"`
	Trading struct {
		Mode            string  `toml:"mode"`
		MaxPositions    int     `toml:"max_positions"`
		RiskPerTradePct float64 `toml:"risk_per_trade_pct"`
		MaxLossPct      float64 `toml:"max_loss_pct"`
	} `toml:"trading"`
	// Add other sections as needed
}

// ConfigWatcher watches for changes to the config file
type ConfigWatcher struct {
	configPath string
	config     atomic.Value // *Config
	watcher    *fsnotify.Watcher
}

// NewConfigWatcher creates a new config watcher
func NewConfigWatcher(configPath string) (*ConfigWatcher, error) {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		return nil, fmt.Errorf("error creating watcher: %w", err)
	}

	cw := &ConfigWatcher{
		configPath: configPath,
		watcher:    watcher,
	}

	// Load initial config
	if err := cw.loadConfig(); err != nil {
		return nil, fmt.Errorf("error loading initial config: %w", err)
	}

	return cw, nil
}

// Start starts watching for config changes
func (cw *ConfigWatcher) Start() error {
	// Watch the directory containing the config file
	dir := "/config"
	if err := cw.watcher.Add(dir); err != nil {
		return fmt.Errorf("error watching directory %s: %w", dir, err)
	}

	go cw.watchConfig()
	return nil
}

// Stop stops watching for config changes
func (cw *ConfigWatcher) Stop() {
	cw.watcher.Close()
}

// GetConfig returns the current config
func (cw *ConfigWatcher) GetConfig() *Config {
	if cfg, ok := cw.config.Load().(*Config); ok {
		return cfg
	}
	return nil
}

// loadConfig loads the config from file
func (cw *ConfigWatcher) loadConfig() error {
	var config Config
	if _, err := toml.DecodeFile(cw.configPath, &config); err != nil {
		return err
	}
	cw.config.Store(&config)
	return nil
}

// watchConfig watches for changes to the config file
func (cw *ConfigWatcher) watchConfig() {
	for {
		select {
		case event, ok := <-cw.watcher.Events:
			if !ok {
				return
			}

			if event.Name == cw.configPath && (event.Has(fsnotify.Write) || event.Has(fsnotify.Create)) {
				log.Println("Config file modified, reloading...")
				if err := cw.loadConfig(); err != nil {
					log.Printf("Error reloading config: %v", err)
					continue
				}
				log.Println("Config successfully reloaded")
			}
		case err, ok := <-cw.watcher.Errors:
			if !ok {
				return
			}
			log.Printf("Error watching config: %v", err)
		}
	}
}

func printConfig(config *Config) {
	fmt.Println("\nCurrent configuration:")
	fmt.Println("=====================")
	fmt.Printf("IBKR:\n")
	fmt.Printf("  Host: %s\n", config.IBKR.Host)
	fmt.Printf("  Port: %d\n", config.IBKR.Port)
	fmt.Printf("  ClientID: %d\n", config.IBKR.ClientID)
	fmt.Printf("  ReadOnly: %t\n", config.IBKR.ReadOnly)
	fmt.Printf("\nTrading:\n")
	fmt.Printf("  Mode: %s\n", config.Trading.Mode)
	fmt.Printf("  MaxPositions: %d\n", config.Trading.MaxPositions)
	fmt.Printf("  RiskPerTradePct: %.2f\n", config.Trading.RiskPerTradePct)
	fmt.Printf("  MaxLossPct: %.2f\n", config.Trading.MaxLossPct)
}

func main() {
	configPath := "/config/config.toml"

	// For testing on Windows, use a local path
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		configPath = "config/config.toml"
	}

	log.Printf("Using config path: %s", configPath)

	cw, err := NewConfigWatcher(configPath)
	if err != nil {
		log.Fatalf("Error creating config watcher: %v", err)
	}
	defer cw.Stop()

	if err := cw.Start(); err != nil {
		log.Fatalf("Error starting config watcher: %v", err)
	}

	log.Println("Config watcher started")
	log.Println("Modify the config file to see changes")

	printConfig(cw.GetConfig())

	// Handle OS signals
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// Main loop
	for {
		select {
		case <-sigChan:
			log.Println("Shutting down...")
			return
		case <-time.After(10 * time.Second):
			log.Println("Process still running...")
		}
	}
}
