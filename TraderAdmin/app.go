package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"math"
	"os"
	"path/filepath"
	"sync/atomic"
	"time"

	"github.com/BurntSushi/toml"
	"github.com/alecthomas/jsonschema"
	"github.com/fsnotify/fsnotify"
)

// Config struct to hold the configuration
type Config struct {
	IBKR           IBKRConfig                `toml:"ibkr"`
	Trading        TradingConfig             `toml:"trading"`
	Strategies     map[string]StrategyConfig `toml:"strategies"`
	Options        OptionsConfig             `toml:"options"`
	Greeks         GreeksConfig              `toml:"greeks"`
	Probability    ProbabilityConfig         `toml:"probability"`
	Events         EventsConfig              `toml:"events"`
	DTE            DTEConfig                 `toml:"dte"`
	Universe       UniverseConfig            `toml:"universe"`
	Scanner        ScannerConfig             `toml:"scanner"`
	DataManagement DataManagementConfig      `toml:"data_management"`
	Logging        LoggingConfig             `toml:"logging"`
	Scheduling     SchedulingConfig          `toml:"scheduling"`
	Monitoring     MonitoringConfig          `toml:"monitoring"`
	Alerts         AlertsConfig              `toml:"alerts"`
	Backup         BackupConfig              `toml:"backup"`
	Kubernetes     KubernetesConfig          `toml:"kubernetes"`
}

// IBKRConfig holds IBKR connection settings
type IBKRConfig struct {
	Host     string `toml:"host"`
	Port     int    `toml:"port"`
	ClientID int    `toml:"client_id"`
	ReadOnly bool   `toml:"read_only"`
}

// TradingConfig holds trading settings
type TradingConfig struct {
	Mode            string  `toml:"mode"`
	MaxPositions    int     `toml:"max_positions"`
	RiskPerTradePct float64 `toml:"risk_per_trade_pct"`
	MaxLossPct      float64 `toml:"max_loss_pct"`
}

// StrategyConfig holds strategy settings
type StrategyConfig struct {
	Active          bool    `toml:"active"`
	MinRSI          float64 `toml:"min_rsi"`
	MaxATRRatio     float64 `toml:"max_atr_ratio"`
	MinIVRank       float64 `toml:"min_iv_rank"`
	MaxDelta        float64 `toml:"max_delta"`
	MinDaysToExpiry int     `toml:"min_days_to_expiry"`
	MaxDaysToExpiry int     `toml:"max_days_to_expiry"`
	TargetProfitPct float64 `toml:"target_profit_pct"`
	StopLossPct     float64 `toml:"stop_loss_pct"`
}

// OptionsConfig holds options settings
type OptionsConfig struct {
	MinOpenInterest         int     `toml:"min_open_interest"`
	MaxBidAskSpreadPct      float64 `toml:"max_bid_ask_spread_pct"`
	PreferredExpirationDays []int   `toml:"preferred_expiration_days"`
	StrikePriceIncrement    float64 `toml:"strike_price_increment"`
	MinIVRank               float64 `toml:"min_iv_rank"`
	MaxIVRank               float64 `toml:"max_iv_rank"`
	MinCallPutSkewPct       float64 `toml:"min_call_put_skew_pct"`
}

// GreeksConfig holds options Greek limits
type GreeksConfig struct {
	MaxThetaPerDay   float64 `toml:"max_theta_per_day"`
	MaxVegaExposure  float64 `toml:"max_vega_exposure"`
	MaxGammaExposure float64 `toml:"max_gamma_exposure"`
}

// ProbabilityConfig holds probability metrics settings
type ProbabilityConfig struct {
	MinPOP            float64 `toml:"min_pop"`
	MaxWidthVsMovePct float64 `toml:"max_width_vs_move_pct"`
}

// EventsConfig holds event-based filtering settings
type EventsConfig struct {
	SkipEarningsDays int `toml:"skip_earnings_days"`
	SkipExDivDays    int `toml:"skip_exdiv_days"`
}

// DTEConfig holds dynamic days-to-expiry settings
type DTEConfig struct {
	Dynamic        bool    `toml:"dynamic"`
	DTECoefficient float64 `toml:"dte_coefficient"`
}

// UniverseConfig holds universe settings
type UniverseConfig struct {
	Symbols       []string `toml:"symbols"`
	MinMarketCap  int64    `toml:"min_market_cap"`
	MaxVolatility float64  `toml:"max_volatility"`
	Sectors       []string `toml:"sectors"`
}

// ScannerConfig holds scanner settings
type ScannerConfig struct {
	ScanIntervalSeconds int  `toml:"scan_interval_seconds"`
	LookbackDays        int  `toml:"lookback_days"`
	MinVolume           int  `toml:"min_volume"`
	UsePremarketData    bool `toml:"use_premarket_data"`
}

// DataManagementConfig holds data management settings
type DataManagementConfig struct {
	CacheDir           string `toml:"cache_dir"`
	DataRetentionDays  int    `toml:"data_retention_days"`
	EnableDailyCleanup bool   `toml:"enable_daily_cleanup"`
}

// LoggingConfig holds logging settings
type LoggingConfig struct {
	Level      string `toml:"level"`
	File       string `toml:"file"`
	MaxSizeMB  int    `toml:"max_size_mb"`
	MaxBackups int    `toml:"max_backups"`
	MaxAgeDays int    `toml:"max_age_days"`
}

// SchedulingConfig holds scheduling settings
type SchedulingConfig struct {
	TradingStartTime  string   `toml:"trading_start_time"`
	TradingEndTime    string   `toml:"trading_end_time"`
	Timezone          string   `toml:"timezone"`
	TradingDays       []string `toml:"trading_days"`
	MaintenanceWindow string   `toml:"maintenance_window"`
}

// MonitoringConfig holds monitoring settings
type MonitoringConfig struct {
	PrometheusPort         int    `toml:"prometheus_port"`
	MetricsIntervalSeconds int    `toml:"metrics_interval_seconds"`
	HealthCheckURL         string `toml:"health_check_url"`
}

// AlertsConfig holds alert settings
type AlertsConfig struct {
	EnableEmail     bool   `toml:"enable_email"`
	EmailTo         string `toml:"email_to"`
	EnableSlack     bool   `toml:"enable_slack"`
	SlackWebhookURL string `toml:"slack_webhook_url"`
	AlertOnErrors   bool   `toml:"alert_on_errors"`
	AlertOnTrades   bool   `toml:"alert_on_trades"`
}

// BackupConfig holds backup settings
type BackupConfig struct {
	AutoBackup          bool   `toml:"auto_backup"`
	BackupIntervalHours int    `toml:"backup_interval_hours"`
	BackupDir           string `toml:"backup_dir"`
	KeepBackups         int    `toml:"keep_backups"`
}

// KubernetesConfig holds Kubernetes settings
type KubernetesConfig struct {
	Namespace              string `toml:"namespace"`
	ConfigMapName          string `toml:"config_map_name"`
	OrchestratorDeployment string `toml:"orchestrator_deployment"`
	ScannerDeployment      string `toml:"scanner_deployment"`
}

// StatusInfo represents the application's status information
type StatusInfo struct {
	IBKRConnected bool                  `json:"ibkrConnected"`
	IBKRError     string                `json:"ibkrError,omitempty"`
	Containers    []ContainerStatusInfo `json:"containers"`
}

// ContainerStatusInfo represents a container's status
type ContainerStatusInfo struct {
	Name  string `json:"name"`
	State string `json:"state"`
}

// App struct
type App struct {
	ctx        context.Context
	configPath string
	config     atomic.Value // *Config
	watcher    *fsnotify.Watcher
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{
		configPath: "config/config.toml",
	}
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx

	// Load the initial configuration
	config, err := a.loadConfig()
	if err != nil {
		fmt.Printf("Error loading config: %v\n", err)
	} else {
		a.config.Store(config)
	}

	// Setup config file watcher for live reload
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		fmt.Printf("Error creating file watcher: %v\n", err)
		return
	}

	a.watcher = watcher

	// Watch the config file for changes
	err = watcher.Add(filepath.Dir(a.configPath))
	if err != nil {
		fmt.Printf("Error watching config file: %v\n", err)
		return
	}

	// Start watching for changes
	go a.watchConfig()
}

// shutdown is called when the app is closing
func (a *App) shutdown(ctx context.Context) {
	if a.watcher != nil {
		a.watcher.Close()
	}
}

// GetConfig returns the current configuration
func (a *App) GetConfig() *Config {
	if cfg, ok := a.config.Load().(*Config); ok {
		return cfg
	}
	return nil
}

// SaveConfig saves the configuration to file
func (a *App) SaveConfig(config *Config) error {
	// Create a backup of the current config
	err := a.backupConfig()
	if err != nil {
		return fmt.Errorf("error backing up config: %w", err)
	}

	// Save the new config
	file, err := os.Create(a.configPath)
	if err != nil {
		return fmt.Errorf("error creating config file: %w", err)
	}
	defer file.Close()

	encoder := toml.NewEncoder(file)
	err = encoder.Encode(config)
	if err != nil {
		return fmt.Errorf("error encoding config: %w", err)
	}

	// Update the current config
	a.config.Store(config)

	return nil
}

// backupConfig creates a backup of the current config file
func (a *App) backupConfig() error {
	// Check if config file exists
	_, err := os.Stat(a.configPath)
	if os.IsNotExist(err) {
		return nil // Nothing to backup
	}

	// Create backup file
	backupPath := a.configPath + ".bak"
	source, err := os.Open(a.configPath)
	if err != nil {
		return err
	}
	defer source.Close()

	destination, err := os.Create(backupPath)
	if err != nil {
		return err
	}
	defer destination.Close()

	_, err = io.Copy(destination, source)
	return err
}

// loadConfig loads the configuration from file
func (a *App) loadConfig() (*Config, error) {
	var config Config
	_, err := toml.DecodeFile(a.configPath, &config)
	if err != nil {
		return nil, err
	}
	return &config, nil
}

// watchConfig watches for changes to the config file
func (a *App) watchConfig() {
	for {
		select {
		case event, ok := <-a.watcher.Events:
			if !ok {
				return
			}

			// Check if the config file was modified
			if event.Name == a.configPath && (event.Has(fsnotify.Write) || event.Has(fsnotify.Create)) {
				// Wait a bit to ensure the file is fully written
				time.Sleep(100 * time.Millisecond)

				// Reload the config
				config, err := a.loadConfig()
				if err != nil {
					fmt.Printf("Error reloading config: %v\n", err)
					continue
				}

				// Update the current config
				a.config.Store(config)
				fmt.Println("Config reloaded")
			}
		case err, ok := <-a.watcher.Errors:
			if !ok {
				return
			}
			fmt.Printf("Error watching config: %v\n", err)
		}
	}
}

// PauseStack pauses all services in the stack
func (a *App) PauseStack() string {
	config := a.GetConfig()
	if config == nil {
		return "Error: Configuration not loaded"
	}

	// If using Kubernetes
	if config.Kubernetes.Namespace != "" {
		// Here we would use the Kubernetes client-go library to scale deployments
		// For demonstration, just show what would happen
		msg := fmt.Sprintf("Pausing Kubernetes deployments in namespace %s:\n", config.Kubernetes.Namespace)
		msg += fmt.Sprintf("- Scaling %s to 0 replicas\n", config.Kubernetes.OrchestratorDeployment)
		msg += fmt.Sprintf("- Scaling %s to 0 replicas\n", config.Kubernetes.ScannerDeployment)

		// In a real implementation:
		// clientset, err := kubernetes.NewForConfig(kubeConfig)
		// deployment, err := clientset.AppsV1().Deployments(namespace).Get(ctx, deploymentName, metav1.GetOptions{})
		// deployment.Spec.Replicas = pointer.Int32Ptr(0)
		// _, err = clientset.AppsV1().Deployments(namespace).Update(ctx, deployment, metav1.UpdateOptions{})

		return msg
	} else {
		// If using Docker
		// Here we would use the Docker API to pause containers
		// For demonstration, just show what would happen
		msg := "Pausing Docker containers:\n"
		msg += "- Pausing python-orchestrator container\n"
		msg += "- Pausing go-scanner container\n"

		// In a real implementation:
		// cli, err := client.NewClientWithOpts(client.FromEnv)
		// err = cli.ContainerPause(ctx, "python-orchestrator")
		// err = cli.ContainerPause(ctx, "go-scanner")

		return msg
	}
}

// UnpauseStack unpauses all services in the stack
func (a *App) UnpauseStack() string {
	config := a.GetConfig()
	if config == nil {
		return "Error: Configuration not loaded"
	}

	// If using Kubernetes
	if config.Kubernetes.Namespace != "" {
		// Here we would use the Kubernetes client-go library to scale deployments
		// For demonstration, just show what would happen
		msg := fmt.Sprintf("Unpausing Kubernetes deployments in namespace %s:\n", config.Kubernetes.Namespace)
		msg += fmt.Sprintf("- Scaling %s to 1 replica\n", config.Kubernetes.OrchestratorDeployment)
		msg += fmt.Sprintf("- Scaling %s to 1 replica\n", config.Kubernetes.ScannerDeployment)

		// In a real implementation:
		// clientset, err := kubernetes.NewForConfig(kubeConfig)
		// deployment, err := clientset.AppsV1().Deployments(namespace).Get(ctx, deploymentName, metav1.GetOptions{})
		// deployment.Spec.Replicas = pointer.Int32Ptr(1)
		// _, err = clientset.AppsV1().Deployments(namespace).Update(ctx, deployment, metav1.UpdateOptions{})

		// After unpausing, we would send a signal to the services to reload config
		// This could be done via sending a SIGUSR1 signal to the process or using another mechanism
		msg += "- Sending reload signal to services\n"

		return msg
	} else {
		// If using Docker
		// Here we would use the Docker API to unpause containers
		// For demonstration, just show what would happen
		msg := "Unpausing Docker containers:\n"
		msg += "- Unpausing python-orchestrator container\n"
		msg += "- Unpausing go-scanner container\n"

		// In a real implementation:
		// cli, err := client.NewClientWithOpts(client.FromEnv)
		// err = cli.ContainerUnpause(ctx, "python-orchestrator")
		// err = cli.ContainerUnpause(ctx, "go-scanner")

		// After unpausing, we would send a signal to the services to reload config
		msg += "- Sending reload signal to services\n"

		return msg
	}
}

// SaveAndRestartStack saves the configuration and restarts all services
func (a *App) SaveAndRestartStack(config *Config) string {
	// Save the configuration
	err := a.SaveConfig(config)
	if err != nil {
		return fmt.Sprintf("Error saving config: %v", err)
	}

	// Pause the stack
	pauseMsg := a.PauseStack()

	// Give services a moment to pause
	time.Sleep(1 * time.Second)

	// Unpause the stack
	unpauseMsg := a.UnpauseStack()

	return fmt.Sprintf("Configuration saved and stack restarted:\n%s\n%s", pauseMsg, unpauseMsg)
}

// Greet returns a greeting for the given name
func (a *App) Greet(name string) string {
	return fmt.Sprintf("Hello %s, TraderAdmin is ready!", name)
}

// GetConfigSchema returns the JSON schema for the Config struct
func (a *App) GetConfigSchema() (string, error) {
	reflector := jsonschema.Reflector{
		ExpandedStruct: true,
		DoNotReference: true,
	}
	schema := reflector.Reflect(&Config{})

	schemaJSON, err := json.MarshalIndent(schema, "", "  ")
	if err != nil {
		return "", fmt.Errorf("error encoding schema: %w", err)
	}

	return string(schemaJSON), nil
}

// LoadConfig returns the current configuration
func (a *App) LoadConfig() (*Config, error) {
	return a.GetConfig(), nil
}

// GetStatus returns the current status of the application
func (a *App) GetStatus() (*StatusInfo, error) {
	// This is a placeholder - you'll need to implement the actual status checks
	// for IBKR connection and container statuses

	status := &StatusInfo{
		IBKRConnected: false, // Replace with actual IBKR connection check
		Containers: []ContainerStatusInfo{
			{Name: "orchestrator", State: "Running"}, // Replace with actual container status
			{Name: "scanner", State: "Running"},      // Replace with actual container status
		},
	}

	// TODO: Implement actual IBKR connection check
	// TODO: Implement actual container status checks using Docker/Kubernetes APIs

	return status, nil
}

// TestConnection tests the connection to IBKR
func (a *App) TestConnection() (bool, error) {
	// This is a placeholder - you'll need to implement the actual connection test
	// using the IBKR API client

	config := a.GetConfig()
	if config == nil {
		return false, fmt.Errorf("configuration not loaded")
	}

	// TODO: Implement actual IBKR connection test using configuration
	// For now, just return a simulated result
	connected := true // Simulated success

	return connected, nil
}

// OptionContract represents a single option contract
type OptionContract struct {
	Expiry          string  `json:"expiry"`
	Strike          float64 `json:"strike"`
	Type            string  `json:"type"` // "C" or "P"
	Bid             float64 `json:"bid"`
	Ask             float64 `json:"ask"`
	IV              float64 `json:"iv"`
	IVRank          float64 `json:"ivRank"`
	Delta           float64 `json:"delta"`
	Gamma           float64 `json:"gamma"`
	Theta           float64 `json:"theta"`
	Vega            float64 `json:"vega"`
	OpenInterest    int     `json:"openInterest"`
	Volume          int     `json:"volume"`
	BidAskSpreadPct float64 `json:"bidAskSpreadPct"`
	ProbabilityOTM  float64 `json:"probabilityOTM"`
}

// FetchOptionChain fetches the options chain for a given symbol
// In a real implementation, this would connect to IBKR API
func (a *App) FetchOptionChain(symbol string) ([]OptionContract, error) {
	// This is a mock implementation that returns sample data
	// In a real app, you would connect to IBKR API or another data source

	if symbol == "" {
		return nil, fmt.Errorf("symbol is required")
	}

	// For demonstration, return some mock data
	expirations := []string{"2023-06-16", "2023-06-30", "2023-07-21"}
	strikes := []float64{150.0, 155.0, 160.0, 165.0, 170.0}
	types := []string{"C", "P"}

	var contracts []OptionContract

	// Generate mock data
	for _, exp := range expirations {
		for _, strike := range strikes {
			for _, optType := range types {
				// Create logical values based on strike and type
				delta := 0.0
				if optType == "C" {
					delta = 0.5 - (strike-160.0)/40.0
				} else {
					delta = -0.5 + (strike-160.0)/40.0
				}

				// Keep delta in reasonable range
				if delta > 1.0 {
					delta = 0.95
				} else if delta < -1.0 {
					delta = -0.95
				}

				// IV is higher for options further from the money
				iv := 30.0 + math.Abs(delta-0.5)*20.0

				// Calculate bid and ask
				mid := 0.0
				if optType == "C" {
					mid = math.Max(0, (160.0-strike)*0.8+5.0*math.Abs(delta))
				} else {
					mid = math.Max(0, (strike-160.0)*0.8+5.0*math.Abs(delta))
				}

				bid := mid * 0.95
				ask := mid * 1.05

				// Option volume generally correlates with delta (ATM options have more volume)
				oi := int(1000 * (1.0 - math.Abs(delta-0.5)))

				// Calculate other greeks
				gamma := 0.05 * (1.0 - math.Abs(delta*2.0-1.0))
				theta := -mid * 0.01 * (1.0 - math.Abs(delta-0.5))
				vega := mid * 0.1 * (1.0 - math.Abs(delta-0.5))

				// Probability OTM calculation (simplified)
				probOTM := 0.0
				if optType == "C" {
					probOTM = 100.0 * (1.0 - delta)
				} else {
					probOTM = 100.0 * (1.0 + delta)
				}

				// Bid-ask spread as percentage
				spreadPct := 0.0
				if mid > 0 {
					spreadPct = 100.0 * (ask - bid) / mid
				}

				contracts = append(contracts, OptionContract{
					Expiry:          exp,
					Strike:          strike,
					Type:            optType,
					Bid:             math.Round(bid*100) / 100,
					Ask:             math.Round(ask*100) / 100,
					IV:              math.Round(iv*100) / 100,
					IVRank:          math.Round(iv/50.0*100) / 100, // Simplified IV rank
					Delta:           math.Round(delta*100) / 100,
					Gamma:           math.Round(gamma*10000) / 10000,
					Theta:           math.Round(theta*100) / 100,
					Vega:            math.Round(vega*100) / 100,
					OpenInterest:    oi,
					Volume:          oi / 2,
					BidAskSpreadPct: math.Round(spreadPct*100) / 100,
					ProbabilityOTM:  math.Round(probOTM*10) / 10,
				})
			}
		}
	}

	return contracts, nil
}
