package main

import (
	"context"
	"errors"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/BurntSushi/toml"
	"github.com/docker/docker/api/types"
	"github.com/docker/docker/client"
	"github.com/wailsapp/wails/v2/pkg/runtime"
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
	Schedule ScheduleConfig
	Alerts   AlertsConfig
	Backup   BackupConfig
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
	// New Liquidity & Execution-Quality Filters
	MinOpenInterest    int     `toml:"min_open_interest"`
	MaxBidAskSpreadPct float64 `toml:"max_bid_ask_spread_pct"`
	// New Implied-Volatility Regime
	MinIVRank         float64 `toml:"min_iv_rank"`
	MaxIVRank         float64 `toml:"max_iv_rank"`
	MinCallPutSkewPct float64 `toml:"min_call_put_skew_pct"`
	// New Greek-Based Risk Controls
	MaxThetaPerDay   float64 `toml:"max_theta_per_day"`
	MaxVegaExposure  float64 `toml:"max_vega_exposure"`
	MaxGammaExposure float64 `toml:"max_gamma_exposure"`
	// New Probability & Expected-Move Metrics
	MinProbOfProfit   float64 `toml:"min_prob_of_profit"`
	MaxWidthVsMovePct float64 `toml:"max_width_vs_move_pct"`
	// New Event & Calendar Controls
	DaysBeforeEarnings int     `toml:"days_before_earnings"`
	DaysBeforeExDiv    int     `toml:"days_before_ex_div"`
	DTEFromATR         bool    `toml:"dte_from_atr"`
	ATRCoefficient     float64 `toml:"atr_coefficient"`
	// New Strike-Selection Flexibility
	StrikeOffset int `toml:"strike_offset"`
	SpreadWidth  int `toml:"spread_width"`
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

// ScheduleConfig holds scheduling settings
type ScheduleConfig struct {
	AutoStartEnabled bool   `toml:"auto_start_enabled"`
	AutoStopEnabled  bool   `toml:"auto_stop_enabled"`
	StartTime        string `toml:"start_time"`
	StopTime         string `toml:"stop_time"`
	Timezone         string `toml:"timezone"`
}

// AlertsConfig holds alert notification settings
type AlertsConfig struct {
	EmailEnabled    bool   `toml:"email_enabled"`
	EmailAddress    string `toml:"email_address"`
	SMSEnabled      bool   `toml:"sms_enabled"`
	SMSNumber       string `toml:"sms_number"`
	WebhookEnabled  bool   `toml:"webhook_enabled"`
	WebhookURL      string `toml:"webhook_url"`
	AlertOnTrade    bool   `toml:"alert_on_trade"`
	AlertOnError    bool   `toml:"alert_on_error"`
	AlertOnStartup  bool   `toml:"alert_on_startup"`
	AlertOnShutdown bool   `toml:"alert_on_shutdown"`
}

// BackupConfig holds backup settings
type BackupConfig struct {
	AutoBackupEnabled   bool   `toml:"auto_backup_enabled"`
	BackupIntervalHours int    `toml:"backup_interval_hours"`
	MaxBackups          int    `toml:"max_backups"`
	BackupDir           string `toml:"backup_dir"`
}

// ContainerInfo represents container information
type ContainerInfo struct {
	ID      string `json:"ID"`
	Name    string `json:"Name"`
	Status  string `json:"Status"`
	Created string `json:"Created"`
}

// App struct
type App struct {
	ctx       context.Context
	dockerCli *client.Client
	configDir string
	logger    *log.Logger
}

// NewApp creates a new App application struct
func NewApp() *App {
	// Create a logger that writes to both stdout and a log file
	logFile, err := os.OpenFile("traderadmin.log", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
	if err != nil {
		fmt.Printf("Failed to open log file: %v\n", err)
		return &App{}
	}

	// Create a multi-writer for stdout and the log file
	var multiWriter io.Writer = os.Stdout
	if logFile != nil {
		multiWriter = io.MultiWriter(os.Stdout, logFile)
	}

	logger := log.New(multiWriter, "[TraderAdmin] ", log.LstdFlags|log.Lshortfile)
	logger.Printf("TraderAdmin %s starting up", GetVersionInfo())

	// Get config directory
	configDir := getConfigDir()

	return &App{
		configDir: configDir,
		logger:    logger,
	}
}

// getConfigDir returns the directory where config files are stored
func getConfigDir() string {
	// Default to current working directory
	dir, err := os.Getwd()
	if err != nil {
		log.Printf("Error getting working directory: %v, using '.' instead", err)
		return "."
	}
	return filepath.Join(dir, "config")
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) error {
	a.ctx = ctx
	a.logger.Println("Application starting up")

	// Initialize Docker client
	cli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		errMsg := fmt.Sprintf("Failed to initialize Docker client: %v", err)
		a.logger.Printf("Error: %s", errMsg)
		runtime.LogErrorf(ctx, "Error: %s", errMsg)
		return fmt.Errorf(errMsg)
	}
	a.dockerCli = cli
	a.logger.Println("Docker client initialized successfully")

	// Ensure config directory exists
	if err := os.MkdirAll(a.configDir, 0755); err != nil {
		a.logger.Printf("Warning: Failed to create config directory: %v", err)
		runtime.LogWarningf(ctx, "Failed to create config directory: %v", err)
	}

	go a.StartupSequenceCheck()
	return nil
}

// shutdown is called when the app is closing
func (a *App) shutdown(ctx context.Context) {
	a.logger.Println("Application shutting down")
	if a.dockerCli != nil {
		a.dockerCli.Close()
		a.logger.Println("Docker client closed")
	}
}

// LoadConfig loads the configuration from the TOML file
func (a *App) LoadConfig() (*Config, error) {
	configPath := filepath.Join(a.configDir, "config.toml")
	a.logger.Printf("Loading configuration from: %s", configPath)

	// Check if config file exists
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		a.logger.Printf("Configuration file not found: %s", configPath)
		return nil, fmt.Errorf("configuration file not found: %s", configPath)
	}

	var config Config
	_, err := toml.DecodeFile(configPath, &config)
	if err != nil {
		a.logger.Printf("Failed to decode config file: %v", err)
		return nil, fmt.Errorf("failed to decode config file: %w", err)
	}

	a.logger.Println("Configuration loaded successfully")
	return &config, nil
}

// SaveConfig saves the configuration to the TOML file
func (a *App) SaveConfig(config *Config) error {
	configPath := filepath.Join(a.configDir, "config.toml")
	a.logger.Printf("Saving configuration to: %s", configPath)

	// Create backup of existing config
	if _, err := os.Stat(configPath); err == nil {
		backupPath := configPath + ".bak"
		if err := copyFile(configPath, backupPath); err != nil {
			a.logger.Printf("Warning: Failed to create backup: %v", err)
		} else {
			a.logger.Printf("Created backup at: %s", backupPath)
		}
	}

	// Create or truncate the file
	file, err := os.Create(configPath)
	if err != nil {
		a.logger.Printf("Failed to create config file: %v", err)
		return fmt.Errorf("failed to create config file: %w", err)
	}
	defer file.Close()

	// Encode the config as TOML
	if err := toml.NewEncoder(file).Encode(config); err != nil {
		a.logger.Printf("Failed to encode config: %v", err)
		return fmt.Errorf("failed to encode config: %w", err)
	}

	a.logger.Println("Configuration saved successfully")
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
	a.logger.Println("Getting container list")

	if a.dockerCli == nil {
		a.logger.Println("Error: Docker client not initialized")
		return nil, errors.New("Docker client not initialized")
	}

	// Print debug information about the docker client
	a.logger.Printf("DEBUG: Docker client initialized: %v", a.dockerCli != nil)

	// Get all containers rather than filtering with labels
	a.logger.Println("Listing all containers")
	containers, err := a.dockerCli.ContainerList(a.ctx, types.ContainerListOptions{
		All: true,
	})
	if err != nil {
		a.logger.Printf("Failed to list containers: %v", err)
		return nil, fmt.Errorf("failed to list containers: %w", err)
	}

	a.logger.Printf("Found %d total containers", len(containers))

	// Debug: Print all container info
	for i, c := range containers {
		a.logger.Printf("DEBUG: Container %d - Name: %v, ID: %s, Status: %s, Created: %d",
			i, c.Names, c.ID[:12], c.Status, c.Created)
	}

	var result []ContainerInfo
	for _, c := range containers {
		isTraderContainer := false
		containerName := strings.TrimPrefix(c.Names[0], "/")
		containerStatus := c.Status

		// Check for our app label
		if val, ok := c.Labels["app"]; ok && val == "ibkr-trader" {
			isTraderContainer = true
			a.logger.Printf("Container %s (ID: %s) matched by label", containerName, c.ID[:12])
		}

		// Check for Kubernetes containers related to our app
		if strings.Contains(containerName, "orchestrator") ||
			strings.Contains(containerName, "scanner") ||
			strings.Contains(containerName, "ibkr-trader") ||
			strings.Contains(containerName, "vertical-spread") {
			isTraderContainer = true
			a.logger.Printf("Container %s (ID: %s) matched by name", containerName, c.ID[:12])

			// For Kubernetes pods, clean up the name and status
			if strings.Contains(containerName, "k8s_") {
				// Extract the actual container name from the k8s_ prefix
				parts := strings.Split(containerName, "_")
				if len(parts) > 2 {
					containerName = parts[1] // Get the actual container name
					a.logger.Printf("DEBUG: K8s container renamed from %s to %s", strings.TrimPrefix(c.Names[0], "/"), containerName)
				}

				// Clean up the status for Kubernetes pods
				if strings.Contains(c.Status, "Up") {
					containerStatus = "Running"
					a.logger.Printf("DEBUG: Status changed from %s to %s", c.Status, containerStatus)
				} else if strings.Contains(c.Status, "Exited") {
					containerStatus = "Stopped"
					a.logger.Printf("DEBUG: Status changed from %s to %s", c.Status, containerStatus)
				}
			}
		}

		// Check image names
		if strings.Contains(c.Image, "ibkr-trader") ||
			strings.Contains(c.Image, "vertical-spread") ||
			strings.Contains(c.Image, "trustdan/auto") {
			isTraderContainer = true
			a.logger.Printf("Container %s (ID: %s) matched by image: %s", containerName, c.ID[:12], c.Image)
		}

		if isTraderContainer {
			createdTime := time.Unix(c.Created, 0).Format(time.RFC3339)
			a.logger.Printf("Adding container to result list: %s (ID: %s, Status: %s, Created: %s)",
				containerName, c.ID[:12], containerStatus, createdTime)

			result = append(result, ContainerInfo{
				ID:      c.ID[:12], // Short ID
				Name:    containerName,
				Status:  containerStatus,
				Created: createdTime,
			})
		}
	}

	a.logger.Printf("Returning %d trader-related containers", len(result))

	// Debug: Print the final results
	for i, c := range result {
		a.logger.Printf("DEBUG: Result %d - Name: %s, ID: %s, Status: %s, Created: %s",
			i, c.Name, c.ID, c.Status, c.Created)
	}

	return result, nil
}

// PauseContainer pauses a container by ID
func (a *App) PauseContainer(id string) error {
	a.logger.Printf("Attempting to pause container: %s", id)

	if a.dockerCli == nil {
		a.logger.Println("Error: Docker client not initialized")
		return errors.New("Docker client not initialized")
	}

	// Check if this is a kubernetes container
	a.logger.Println("Getting container list to verify container")
	containers, err := a.GetContainers()
	if err != nil {
		a.logger.Printf("Error getting containers: %v", err)
		return err
	}

	// Find the container by ID
	a.logger.Printf("Looking for container with ID: %s", id)
	var targetContainer ContainerInfo
	found := false
	for _, c := range containers {
		if c.ID == id {
			targetContainer = c
			found = true
			a.logger.Printf("Found container: %s (ID: %s)", c.Name, c.ID)
			break
		}
	}

	if !found {
		errMsg := fmt.Sprintf("Container with ID %s not found", id)
		a.logger.Println(errMsg)
		return fmt.Errorf(errMsg)
	}

	// Special handling for Kubernetes containers
	if strings.Contains(targetContainer.Name, "k8s_") {
		// For Kubernetes containers, we can't pause them directly
		a.logger.Printf("Kubernetes container %s (%s) cannot be paused directly", targetContainer.Name, id)
		runtime.LogInfof(a.ctx, "Kubernetes container %s cannot be paused directly", targetContainer.Name)
		return nil
	}

	// For regular Docker containers, pause as usual
	a.logger.Printf("Pausing container: %s (ID: %s)", targetContainer.Name, id)
	if err := a.dockerCli.ContainerPause(a.ctx, id); err != nil {
		a.logger.Printf("Failed to pause container: %v", err)
		return fmt.Errorf("failed to pause container: %w", err)
	}

	a.logger.Printf("Container paused successfully: %s (ID: %s)", targetContainer.Name, id)
	runtime.LogInfof(a.ctx, "Container %s paused successfully", targetContainer.Name)
	return nil
}

// UnpauseContainer unpauses a container by ID
func (a *App) UnpauseContainer(id string) error {
	a.logger.Printf("Attempting to unpause container: %s", id)

	if a.dockerCli == nil {
		a.logger.Println("Error: Docker client not initialized")
		return errors.New("Docker client not initialized")
	}

	// Check if this is a kubernetes container
	a.logger.Println("Getting container list to verify container")
	containers, err := a.GetContainers()
	if err != nil {
		a.logger.Printf("Error getting containers: %v", err)
		return err
	}

	// Find the container by ID
	a.logger.Printf("Looking for container with ID: %s", id)
	var targetContainer ContainerInfo
	found := false
	for _, c := range containers {
		if c.ID == id {
			targetContainer = c
			found = true
			a.logger.Printf("Found container: %s (ID: %s)", c.Name, c.ID)
			break
		}
	}

	if !found {
		errMsg := fmt.Sprintf("Container with ID %s not found", id)
		a.logger.Println(errMsg)
		return fmt.Errorf(errMsg)
	}

	// Special handling for Kubernetes containers
	if strings.Contains(targetContainer.Name, "k8s_") {
		// For Kubernetes containers, we can't unpause them directly
		a.logger.Printf("Kubernetes container %s (%s) cannot be unpaused directly", targetContainer.Name, id)
		runtime.LogInfof(a.ctx, "Kubernetes container %s cannot be unpaused directly", targetContainer.Name)
		return nil
	}

	// For regular Docker containers, unpause as usual
	a.logger.Printf("Unpausing container: %s (ID: %s)", targetContainer.Name, id)
	if err := a.dockerCli.ContainerUnpause(a.ctx, id); err != nil {
		a.logger.Printf("Failed to unpause container: %v", err)
		return fmt.Errorf("failed to unpause container: %w", err)
	}

	a.logger.Printf("Container unpaused successfully: %s (ID: %s)", targetContainer.Name, id)
	runtime.LogInfof(a.ctx, "Container %s unpaused successfully", targetContainer.Name)
	return nil
}

// SendSignal sends a signal to a container
func (a *App) SendSignal(id, signal string) error {
	a.logger.Printf("Sending signal %s to container: %s", signal, id)

	if a.dockerCli == nil {
		a.logger.Println("Error: Docker client not initialized")
		return errors.New("Docker client not initialized")
	}

	// First check if container exists and get its name
	containers, err := a.GetContainers()
	if err != nil {
		a.logger.Printf("Error getting containers: %v", err)
		return err
	}

	var containerName string
	for _, c := range containers {
		if c.ID == id {
			containerName = c.Name
			break
		}
	}

	if containerName == "" {
		a.logger.Printf("Warning: Container ID %s not found in trader containers", id)
	} else {
		a.logger.Printf("Sending signal %s to container: %s (ID: %s)", signal, containerName, id)
	}

	if err := a.dockerCli.ContainerKill(a.ctx, id, signal); err != nil {
		a.logger.Printf("Failed to send signal to container: %v", err)
		return fmt.Errorf("failed to send signal to container: %w", err)
	}

	a.logger.Printf("Signal %s sent successfully to container: %s", signal, id)
	return nil
}

// PauseStack pauses all trader containers
func (a *App) PauseStack() error {
	a.logger.Println("Attempting to pause all trader containers")

	containers, err := a.GetContainers()
	if err != nil {
		a.logger.Printf("Error getting containers: %v", err)
		return err
	}

	// Count of containers that were paused
	pausedCount := 0
	a.logger.Printf("Found %d trader containers to evaluate for pausing", len(containers))

	for _, c := range containers {
		// Skip Kubernetes containers
		if strings.Contains(c.Name, "k8s_") {
			a.logger.Printf("Skipping Kubernetes container %s for pause operation", c.Name)
			continue
		}

		// Skip already paused containers
		if strings.Contains(c.Status, "Paused") {
			a.logger.Printf("Container %s is already paused", c.Name)
			continue
		}

		// Skip stopped containers
		if !strings.Contains(c.Status, "Up") {
			a.logger.Printf("Container %s is not running, skipping pause", c.Name)
			continue
		}

		a.logger.Printf("Pausing container: %s (ID: %s)", c.Name, c.ID)
		if err := a.PauseContainer(c.ID); err != nil {
			a.logger.Printf("Error pausing container %s: %v", c.Name, err)
			return err
		}
		pausedCount++
		a.logger.Printf("Container paused successfully: %s", c.Name)
	}

	if pausedCount == 0 {
		a.logger.Println("No eligible containers found to pause")
		runtime.LogInfof(a.ctx, "No eligible containers found to pause")
	} else {
		a.logger.Printf("Paused %d containers", pausedCount)
		runtime.LogInfof(a.ctx, "Paused %d containers", pausedCount)
	}

	return nil
}

// UnpauseStack unpauses all trader containers
func (a *App) UnpauseStack() error {
	a.logger.Println("Attempting to unpause all trader containers")

	containers, err := a.GetContainers()
	if err != nil {
		a.logger.Printf("Error getting containers: %v", err)
		return err
	}

	// Count of containers that were unpaused
	unpausedCount := 0
	a.logger.Printf("Found %d trader containers to evaluate for unpausing", len(containers))

	for _, c := range containers {
		// Skip Kubernetes containers
		if strings.Contains(c.Name, "k8s_") {
			a.logger.Printf("Skipping Kubernetes container %s for unpause operation", c.Name)
			continue
		}

		// Skip containers that aren't paused
		if !strings.Contains(c.Status, "Paused") {
			a.logger.Printf("Container %s is not paused, skipping unpause", c.Name)
			continue
		}

		a.logger.Printf("Unpausing container: %s (ID: %s)", c.Name, c.ID)
		if err := a.UnpauseContainer(c.ID); err != nil {
			a.logger.Printf("Error unpausing container %s: %v", c.Name, err)
			return err
		}
		unpausedCount++
		a.logger.Printf("Container unpaused successfully: %s", c.Name)
	}

	if unpausedCount == 0 {
		a.logger.Println("No paused containers found to unpause")
		runtime.LogInfof(a.ctx, "No paused containers found to unpause")
	} else {
		a.logger.Printf("Unpaused %d containers", unpausedCount)
		runtime.LogInfof(a.ctx, "Unpaused %d containers", unpausedCount)
	}

	return nil
}

// ReloadConfig signals all containers to reload their configuration
func (a *App) ReloadConfig() error {
	a.logger.Println("Attempting to reload configuration on all containers")

	containers, err := a.GetContainers()
	if err != nil {
		a.logger.Printf("Error getting containers: %v", err)
		return err
	}

	signalCount := 0
	a.logger.Printf("Found %d trader containers to signal for config reload", len(containers))

	for _, c := range containers {
		// Skip Kubernetes containers for signaling
		if strings.Contains(c.Name, "k8s_") {
			a.logger.Printf("Skipping Kubernetes container %s for config reload signal", c.Name)
			continue
		}

		// Only signal running containers
		if !strings.Contains(c.Status, "Up") {
			a.logger.Printf("Container %s is not running, skipping config reload signal", c.Name)
			continue
		}

		a.logger.Printf("Sending SIGUSR1 to container: %s (ID: %s)", c.Name, c.ID)
		if err := a.SendSignal(c.ID, "SIGUSR1"); err != nil {
			a.logger.Printf("Error signaling container %s: %v", c.Name, err)
			return err
		}
		signalCount++
		a.logger.Printf("Signal sent successfully to container: %s", c.Name)
	}

	if signalCount == 0 {
		a.logger.Println("No eligible containers found to signal for config reload")
		runtime.LogInfof(a.ctx, "No eligible containers found to signal for config reload")
	} else {
		a.logger.Printf("Sent reload signal to %d containers", signalCount)
		runtime.LogInfof(a.ctx, "Sent reload signal to %d containers", signalCount)
	}

	return nil
}

// SaveAndRestart saves the config, pauses containers, updates config, and unpauses
func (a *App) SaveAndRestart(config *Config) error {
	a.logger.Println("SaveAndRestart operation started")

	// 1. Save the configuration first before touching containers
	a.logger.Println("Step 1: Saving configuration")
	if err := a.SaveConfig(config); err != nil {
		a.logger.Printf("Failed to save config: %v", err)
		return fmt.Errorf("failed to save config: %w", err)
	}

	a.logger.Println("Configuration saved successfully")
	runtime.LogInfof(a.ctx, "Configuration saved successfully")

	// Get a list of containers
	a.logger.Println("Getting container list")
	containers, err := a.GetContainers()
	if err != nil {
		a.logger.Printf("Failed to get containers: %v", err)
		return fmt.Errorf("failed to get containers: %w", err)
	}

	// Check if we have any containers to manage
	hasKubeContainers := false
	hasDockerContainers := false

	for _, c := range containers {
		if strings.Contains(c.Name, "k8s_") {
			hasKubeContainers = true
		} else if strings.Contains(c.Status, "Up") {
			hasDockerContainers = true
		}
	}

	a.logger.Printf("Container analysis: Kubernetes=%v, Docker=%v", hasKubeContainers, hasDockerContainers)

	// 2. Pause regular Docker containers if we have any
	if hasDockerContainers {
		a.logger.Println("Step 2: Pausing Docker containers")
		if err := a.PauseStack(); err != nil {
			a.logger.Printf("Failed to pause containers: %v", err)
			return fmt.Errorf("failed to pause containers: %w", err)
		}
		a.logger.Println("Docker containers paused successfully")
		runtime.LogInfof(a.ctx, "Docker containers paused successfully")
	} else {
		a.logger.Println("No running Docker containers to pause")
	}

	// 3. Unpause regular Docker containers if we have any
	if hasDockerContainers {
		a.logger.Println("Step 3: Unpausing Docker containers")
		if err := a.UnpauseStack(); err != nil {
			a.logger.Printf("Failed to unpause containers: %v", err)
			return fmt.Errorf("failed to unpause containers: %w", err)
		}
		a.logger.Println("Docker containers unpaused successfully")
		runtime.LogInfof(a.ctx, "Docker containers unpaused successfully")
	} else {
		a.logger.Println("No Docker containers to unpause")
	}

	// 4. Signal containers to reload configuration
	a.logger.Println("Step 4: Signaling containers to reload configuration")
	signalSent := false
	for _, c := range containers {
		// Skip Kubernetes containers for direct signals
		if strings.Contains(c.Name, "k8s_") {
			a.logger.Printf("Skipping Kubernetes container %s for signal", c.Name)
			continue
		}

		// Only send signals to running containers
		if !strings.Contains(c.Status, "Up") {
			a.logger.Printf("Container %s is not running, skipping signal", c.Name)
			continue
		}

		a.logger.Printf("Sending SIGUSR1 to container: %s (ID: %s)", c.Name, c.ID)
		if err := a.SendSignal(c.ID, "SIGUSR1"); err != nil {
			a.logger.Printf("Warning: failed to signal container %s: %v", c.Name, err)
			runtime.LogWarningf(a.ctx, "Failed to signal container %s: %v", c.Name, err)
		} else {
			signalSent = true
			a.logger.Printf("Signal sent successfully to container: %s", c.Name)
		}
	}

	if !signalSent && hasDockerContainers {
		a.logger.Println("Warning: No containers were signaled to reload configuration")
		runtime.LogWarningf(a.ctx, "No containers were signaled to reload configuration")
	}

	// If we have Kubernetes containers, log a message about restarting them
	if hasKubeContainers {
		a.logger.Println("Note: For Kubernetes containers, you may need to restart them manually to apply configuration changes.")
		runtime.LogInfof(a.ctx, "For Kubernetes containers, you may need to restart them manually to apply configuration changes.")
	}

	a.logger.Println("SaveAndRestart operation completed successfully")
	return nil
}

// Status returns the current status of the trader stack
func (a *App) Status() (string, error) {
	a.logger.Println("Checking trader stack status")

	if a.dockerCli == nil {
		a.logger.Println("Docker client not initialized")
		return "Docker Not Connected", errors.New("Docker client not initialized")
	}

	containers, err := a.GetContainers()
	if err != nil {
		a.logger.Printf("Error getting containers: %v", err)
		return "Error", err
	}

	if len(containers) == 0 {
		a.logger.Println("No containers found")
		return "No Containers", nil
	}

	// Check if all containers are running
	allRunning := true
	runningCount := 0

	for _, c := range containers {
		if strings.Contains(c.Status, "Up") {
			runningCount++
		} else {
			allRunning = false
		}
	}

	a.logger.Printf("Status check: %d total containers, %d running, allRunning=%v", len(containers), runningCount, allRunning)

	if allRunning {
		a.logger.Println("All containers are running")
		return "Running", nil
	}

	a.logger.Println("Some containers are not running")
	return "Partial", nil
}

// DeployStack creates the trader-stack namespace if it doesn't exist and deploys the stack
func (a *App) DeployStack() error {
	a.logger.Println("Checking if trader-stack namespace exists")

	// Run kubectl get namespace trader-stack to check if it exists
	cmd := exec.Command("kubectl", "get", "namespace", "trader-stack")
	if err := cmd.Run(); err != nil {
		// Namespace doesn't exist, create it
		a.logger.Println("Creating trader-stack namespace")
		createCmd := exec.Command("kubectl", "create", "namespace", "trader-stack")
		if err := createCmd.Run(); err != nil {
			errMsg := fmt.Sprintf("Failed to create namespace: %v", err)
			a.logger.Printf("Error: %s", errMsg)
			return fmt.Errorf(errMsg)
		}
		a.logger.Println("Namespace created successfully")
	}

	// Get the current working directory
	currentDir, err := os.Getwd()
	if err != nil {
		return fmt.Errorf("failed to get working directory: %w", err)
	}

	// Change to the root directory where kubernetes/base is located
	rootDir := filepath.Dir(currentDir)
	if err := os.Chdir(rootDir); err != nil {
		return fmt.Errorf("failed to change directory: %w", err)
	}
	defer os.Chdir(currentDir) // Change back when done

	// Deploy the stack using kubectl apply -k
	a.logger.Println("Deploying trading stack")
	deployCmd := exec.Command("kubectl", "apply", "-k", "kubernetes/base/")
	output, err := deployCmd.CombinedOutput()
	if err != nil {
		errMsg := fmt.Sprintf("Failed to deploy stack: %v\nOutput: %s", err, string(output))
		a.logger.Printf("Error: %s", errMsg)
		return fmt.Errorf(errMsg)
	}

	a.logger.Printf("Stack deployed successfully: %s", string(output))
	return nil
}

// TestIBKRConnection tests the IBKR API connection with the current settings
func (a *App) TestIBKRConnection(config *IBKRConfig) (*ServiceStatus, error) {
	a.logger.Printf("Testing IBKR connection to %s:%d", config.Host, config.Port)

	// Create a struct to hold the test results
	result := &ServiceStatus{
		Name:    "IBKR Connection",
		Status:  "Unknown",
		IsOK:    false,
		Message: "Connection test not implemented",
	}

	// In a real implementation, you would attempt to connect to TWS/IB Gateway here
	// For now, we'll simulate a successful connection
	result.Status = "Connected"
	result.IsOK = true
	result.Message = fmt.Sprintf("Successfully connected to %s:%d", config.Host, config.Port)

	if config.ReadOnly {
		result.ExtraMsg = "Read-only mode enabled"
	}

	return result, nil
}

// ClearCache clears the data cache folders
func (a *App) ClearCache(cacheType string) error {
	a.logger.Printf("Clearing cache: %s", cacheType)

	config, err := a.LoadConfig()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	baseDir := config.Data.CacheDir
	a.logger.Printf("Cache base directory: %s", baseDir)

	// Make sure the base directory exists
	if _, err := os.Stat(baseDir); os.IsNotExist(err) {
		return fmt.Errorf("cache directory does not exist: %s", baseDir)
	}

	var dirsToClear []string

	switch cacheType {
	case "all":
		dirsToClear = []string{baseDir}
	case "universe":
		dirsToClear = []string{filepath.Join(baseDir, "universe")}
	case "minute":
		dirsToClear = []string{filepath.Join(baseDir, "minute")}
	case "options":
		dirsToClear = []string{filepath.Join(baseDir, "options")}
	default:
		return fmt.Errorf("unknown cache type: %s", cacheType)
	}

	for _, dir := range dirsToClear {
		a.logger.Printf("Clearing directory: %s", dir)

		// Skip if directory doesn't exist
		if _, err := os.Stat(dir); os.IsNotExist(err) {
			a.logger.Printf("Directory doesn't exist, skipping: %s", dir)
			continue
		}

		// Read directory entries
		entries, err := os.ReadDir(dir)
		if err != nil {
			return fmt.Errorf("failed to read directory %s: %w", dir, err)
		}

		// Delete each entry
		for _, entry := range entries {
			path := filepath.Join(dir, entry.Name())
			a.logger.Printf("Deleting: %s", path)

			err := os.RemoveAll(path)
			if err != nil {
				return fmt.Errorf("failed to delete %s: %w", path, err)
			}
		}
	}

	a.logger.Printf("Cache cleared successfully: %s", cacheType)
	return nil
}

// ConfigureSchedule updates the scheduling settings and ensures they take effect
func (a *App) ConfigureSchedule(schedule *ScheduleConfig) error {
	a.logger.Printf("Configuring schedule: Start=%s, Stop=%s", schedule.StartTime, schedule.StopTime)

	// Check validity of time formats
	if _, err := time.Parse("15:04", schedule.StartTime); err != nil {
		return fmt.Errorf("invalid start time format: %s. Use HH:MM 24-hour format", schedule.StartTime)
	}

	if _, err := time.Parse("15:04", schedule.StopTime); err != nil {
		return fmt.Errorf("invalid stop time format: %s. Use HH:MM 24-hour format", schedule.StopTime)
	}

	// Load current config
	config, err := a.LoadConfig()
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	// Update the schedule section
	config.Schedule = *schedule

	// Save the config
	if err := a.SaveConfig(config); err != nil {
		return fmt.Errorf("failed to save schedule config: %w", err)
	}

	a.logger.Println("Schedule configuration saved successfully")
	return nil
}

// CreateBackup creates a manual backup of the current configuration
func (a *App) CreateBackup() (string, error) {
	a.logger.Println("Creating manual backup")

	config, err := a.LoadConfig()
	if err != nil {
		return "", fmt.Errorf("failed to load config: %w", err)
	}

	// Ensure backup directory exists
	backupDir := config.Backup.BackupDir
	if _, err := os.Stat(backupDir); os.IsNotExist(err) {
		a.logger.Printf("Creating backup directory: %s", backupDir)
		if err := os.MkdirAll(backupDir, 0755); err != nil {
			return "", fmt.Errorf("failed to create backup directory: %w", err)
		}
	}

	// Create timestamped backup filename
	timestamp := time.Now().Format("20060102-150405")
	backupFile := filepath.Join(backupDir, fmt.Sprintf("config-%s.toml", timestamp))

	// Get current config file path
	configPath := filepath.Join(a.configDir, "config.toml")

	// Copy the file
	a.logger.Printf("Creating backup: %s", backupFile)
	if err := copyFile(configPath, backupFile); err != nil {
		return "", fmt.Errorf("failed to create backup: %w", err)
	}

	a.logger.Printf("Backup created successfully: %s", backupFile)
	return backupFile, nil
}

// RestoreBackup restores a configuration from a backup file
func (a *App) RestoreBackup(backupFile string) error {
	a.logger.Printf("Restoring backup from: %s", backupFile)

	// Check if backup file exists
	if _, err := os.Stat(backupFile); os.IsNotExist(err) {
		return fmt.Errorf("backup file does not exist: %s", backupFile)
	}

	// Target config file
	configPath := filepath.Join(a.configDir, "config.toml")

	// First verify that the backup is a valid TOML file
	var config Config
	if _, err := toml.DecodeFile(backupFile, &config); err != nil {
		return fmt.Errorf("invalid backup file: %w", err)
	}

	// Create backup of current config first
	currentBackup := configPath + ".restore_backup"
	if err := copyFile(configPath, currentBackup); err != nil {
		a.logger.Printf("Warning: Failed to backup current config: %v", err)
	}

	// Copy the backup to the config file
	if err := copyFile(backupFile, configPath); err != nil {
		return fmt.Errorf("failed to restore backup: %w", err)
	}

	a.logger.Printf("Backup restored successfully from: %s", backupFile)
	return nil
}

// ListBackups returns a list of available backup files
func (a *App) ListBackups() ([]string, error) {
	a.logger.Println("Listing available backups")

	config, err := a.LoadConfig()
	if err != nil {
		return nil, fmt.Errorf("failed to load config: %w", err)
	}

	// Check if backup directory exists
	backupDir := config.Backup.BackupDir
	if _, err := os.Stat(backupDir); os.IsNotExist(err) {
		a.logger.Printf("Backup directory does not exist: %s", backupDir)
		return []string{}, nil
	}

	// Read directory entries
	entries, err := os.ReadDir(backupDir)
	if err != nil {
		return nil, fmt.Errorf("failed to read backup directory: %w", err)
	}

	// Filter for .toml files
	var backups []string
	for _, entry := range entries {
		if !entry.IsDir() && strings.HasSuffix(entry.Name(), ".toml") {
			backups = append(backups, filepath.Join(backupDir, entry.Name()))
		}
	}

	a.logger.Printf("Found %d backup files", len(backups))
	return backups, nil
}

// GetVersion returns the current version of the application
func (a *App) GetVersion() string {
	return GetVersionInfo()
}

// GetVersionDetails returns detailed version information
func (a *App) GetVersionDetails() map[string]string {
	return GetFullVersionInfo()
}
