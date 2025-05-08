package main

import (
	"context"
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/BurntSushi/toml"
	"github.com/docker/docker/api/types/container"
	"github.com/docker/docker/api/types/filters"
	"github.com/docker/docker/client"
)

// Config represents the trading configuration structure
type Config struct {
	IBKR     IBKRConfig
	Data     DataConfig
	Trading  TradingConfig
	Strategy StrategyConfig
	Options  OptionsConfig
	Universe UniverseConfig
	Scanner  ScannerConfig
	Logging  LoggingConfig
}

// IBKRConfig holds IBKR connection settings
type IBKRConfig struct {
	Host     string `toml:"host"`
	Port     int    `toml:"port"`
	ClientID int    `toml:"client_id"`
	ReadOnly bool   `toml:"read_only"`
	Account  string `toml:"account"`
}

// DataConfig holds data management settings
type DataConfig struct {
	CacheDir              string `toml:"cache_dir"`
	UniverseCacheExpiry   int    `toml:"universe_cache_expiry"`
	MinuteDataCacheExpiry int    `toml:"minute_data_cache_expiry"`
	OptionsCacheExpiry    int    `toml:"options_cache_expiry"`
}

// TradingConfig holds trading execution settings
type TradingConfig struct {
	Mode                   string  `toml:"mode"`
	MaxPositions           int     `toml:"max_positions"`
	MaxDailyTrades         int     `toml:"max_daily_trades"`
	RiskPerTrade           float64 `toml:"risk_per_trade"`
	PriceImprovementFactor float64 `toml:"price_improvement_factor"`
	AllowLateDayEntry      bool    `toml:"allow_late_day_entry"`
}

// StrategyConfig holds strategy-related settings
type StrategyConfig struct {
	HighBase     HighBaseConfig     `toml:"high_base"`
	LowBase      LowBaseConfig      `toml:"low_base"`
	BullPullback BullPullbackConfig `toml:"bull_pullback"`
	BearRally    BearRallyConfig    `toml:"bear_rally"`
}

// HighBaseConfig holds high base strategy settings
type HighBaseConfig struct {
	MaxATRRatio float64 `toml:"max_atr_ratio"`
	MinRSI      int     `toml:"min_rsi"`
}

// LowBaseConfig holds low base strategy settings
type LowBaseConfig struct {
	MinATRRatio float64 `toml:"min_atr_ratio"`
	MaxRSI      int     `toml:"max_rsi"`
}

// BullPullbackConfig holds bull pullback strategy settings
type BullPullbackConfig struct {
	RSIThreshold int `toml:"rsi_threshold"`
}

// BearRallyConfig holds bear rally strategy settings
type BearRallyConfig struct {
	RSIThreshold int `toml:"rsi_threshold"`
}

// OptionsConfig holds option selection settings
type OptionsConfig struct {
	MinDTE        int     `toml:"min_dte"`
	MaxDTE        int     `toml:"max_dte"`
	MinDelta      float64 `toml:"min_delta"`
	MaxDelta      float64 `toml:"max_delta"`
	MaxSpreadCost int     `toml:"max_spread_cost"`
	MinRewardRisk float64 `toml:"min_reward_risk"`
}

// UniverseConfig holds universe filtering settings
type UniverseConfig struct {
	MinMarketCap int64 `toml:"min_market_cap"`
	MinPrice     int   `toml:"min_price"`
	MinVolume    int   `toml:"min_volume"`
}

// ScannerConfig holds scanner settings
type ScannerConfig struct {
	Host           string `toml:"host"`
	Port           int    `toml:"port"`
	MaxConcurrency int    `toml:"max_concurrency"`
}

// LoggingConfig holds logging settings
type LoggingConfig struct {
	Level       string `toml:"level"`
	File        string `toml:"file"`
	MaxSizeMB   int    `toml:"max_size_mb"`
	BackupCount int    `toml:"backup_count"`
	Format      string `toml:"format"`
}

// ContainerInfo represents container information
type ContainerInfo struct {
	ID      string `json:"id"`
	Name    string `json:"name"`
	Status  string `json:"status"`
	Created string `json:"created"`
}

// App struct
type App struct {
	ctx       context.Context
	dockerCli *client.Client
	configDir string
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{
		configDir: getConfigDir(),
	}
}

// getConfigDir returns the directory where config files are stored
func getConfigDir() string {
	// Default to current working directory
	dir, err := os.Getwd()
	if err != nil {
		return "."
	}
	return filepath.Join(dir, "config")
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx

	// Initialize Docker client
	cli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		log.Printf("Warning: Failed to initialize Docker client: %v", err)
		return
	}
	a.dockerCli = cli

	// Ensure config directory exists
	if err := os.MkdirAll(a.configDir, 0755); err != nil {
		log.Printf("Warning: Failed to create config directory: %v", err)
	}

	go a.StartupSequenceCheck()
}

// shutdown is called when the app is closing
func (a *App) shutdown(ctx context.Context) {
	if a.dockerCli != nil {
		a.dockerCli.Close()
	}
}

// LoadConfig loads the configuration from the TOML file
func (a *App) LoadConfig() (*Config, error) {
	configPath := filepath.Join(a.configDir, "config.toml")

	// Check if config file exists
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		return nil, fmt.Errorf("configuration file not found: %s", configPath)
	}

	var config Config
	_, err := toml.DecodeFile(configPath, &config)
	if err != nil {
		return nil, fmt.Errorf("failed to decode config file: %w", err)
	}

	return &config, nil
}

// SaveConfig saves the configuration to the TOML file
func (a *App) SaveConfig(config *Config) error {
	configPath := filepath.Join(a.configDir, "config.toml")

	// Create backup of existing config
	if _, err := os.Stat(configPath); err == nil {
		backupPath := configPath + ".bak"
		if err := copyFile(configPath, backupPath); err != nil {
			log.Printf("Warning: Failed to create backup: %v", err)
		}
	}

	// Create or truncate the file
	file, err := os.Create(configPath)
	if err != nil {
		return fmt.Errorf("failed to create config file: %w", err)
	}
	defer file.Close()

	// Encode the config as TOML
	if err := toml.NewEncoder(file).Encode(config); err != nil {
		return fmt.Errorf("failed to encode config: %w", err)
	}

	return nil
}

// copyFile copies the source file to the destination
func copyFile(src, dst string) error {
	input, err := ioutil.ReadFile(src)
	if err != nil {
		return err
	}
	return ioutil.WriteFile(dst, input, 0644)
}

// GetContainers returns a list of trader-related containers
func (a *App) GetContainers() ([]ContainerInfo, error) {
	if a.dockerCli == nil {
		return nil, errors.New("Docker client not initialized")
	}

	// Filter for our trader application containers
	f := filters.NewArgs()
	f.Add("label", "app=ibkr-trader")

	containers, err := a.dockerCli.ContainerList(a.ctx, container.ListOptions{
		All:     true,
		Filters: f,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to list containers: %w", err)
	}

	var result []ContainerInfo
	for _, c := range containers {
		result = append(result, ContainerInfo{
			ID:      c.ID[:12], // Short ID
			Name:    strings.TrimPrefix(c.Names[0], "/"),
			Status:  c.Status,
			Created: time.Unix(c.Created, 0).Format(time.RFC3339),
		})
	}

	return result, nil
}

// PauseContainer pauses a container by ID
func (a *App) PauseContainer(id string) error {
	if a.dockerCli == nil {
		return errors.New("Docker client not initialized")
	}

	if err := a.dockerCli.ContainerPause(a.ctx, id); err != nil {
		return fmt.Errorf("failed to pause container: %w", err)
	}

	return nil
}

// UnpauseContainer unpauses a container by ID
func (a *App) UnpauseContainer(id string) error {
	if a.dockerCli == nil {
		return errors.New("Docker client not initialized")
	}

	if err := a.dockerCli.ContainerUnpause(a.ctx, id); err != nil {
		return fmt.Errorf("failed to unpause container: %w", err)
	}

	return nil
}

// SendSignal sends a signal to a container
func (a *App) SendSignal(id, signal string) error {
	if a.dockerCli == nil {
		return errors.New("Docker client not initialized")
	}

	if err := a.dockerCli.ContainerKill(a.ctx, id, signal); err != nil {
		return fmt.Errorf("failed to send signal to container: %w", err)
	}

	return nil
}

// PauseStack pauses all trader containers
func (a *App) PauseStack() error {
	containers, err := a.GetContainers()
	if err != nil {
		return err
	}

	for _, c := range containers {
		if err := a.PauseContainer(c.ID); err != nil {
			return err
		}
	}

	return nil
}

// UnpauseStack unpauses all trader containers
func (a *App) UnpauseStack() error {
	containers, err := a.GetContainers()
	if err != nil {
		return err
	}

	for _, c := range containers {
		if err := a.UnpauseContainer(c.ID); err != nil {
			return err
		}
	}

	return nil
}

// ReloadConfig signals all containers to reload their configuration
func (a *App) ReloadConfig() error {
	containers, err := a.GetContainers()
	if err != nil {
		return err
	}

	for _, c := range containers {
		if err := a.SendSignal(c.ID, "SIGUSR1"); err != nil {
			return err
		}
	}

	return nil
}

// SaveAndRestart saves the config, pauses containers, updates config, and unpauses
func (a *App) SaveAndRestart(config *Config) error {
	// 1. Pause all containers
	if err := a.PauseStack(); err != nil {
		return fmt.Errorf("failed to pause containers: %w", err)
	}

	// 2. Save the configuration
	if err := a.SaveConfig(config); err != nil {
		// Try to unpause containers before returning the error
		_ = a.UnpauseStack()
		return fmt.Errorf("failed to save config: %w", err)
	}

	// 3. Unpause all containers
	if err := a.UnpauseStack(); err != nil {
		return fmt.Errorf("failed to unpause containers: %w", err)
	}

	// 4. Signal containers to reload configuration
	if err := a.ReloadConfig(); err != nil {
		return fmt.Errorf("failed to signal containers: %w", err)
	}

	return nil
}

// Status returns the current status of the trader stack
func (a *App) Status() (string, error) {
	if a.dockerCli == nil {
		return "Docker Not Connected", errors.New("Docker client not initialized")
	}

	containers, err := a.GetContainers()
	if err != nil {
		return "Error", err
	}

	if len(containers) == 0 {
		return "No Containers", nil
	}

	// Check if all containers are running
	allRunning := true
	for _, c := range containers {
		if !strings.Contains(c.Status, "Up") {
			allRunning = false
			break
		}
	}

	if allRunning {
		return "Running", nil
	}

	return "Partial", nil
}
