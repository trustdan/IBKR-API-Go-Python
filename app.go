package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net"
	"os"
	"path/filepath"
	"time"

	"github.com/BurntSushi/toml"
	"github.com/fsnotify/fsnotify"
	"github.com/rs/zerolog/log"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"

	"traderadmin/backend/models" // Using the correct module path from go.mod
)

// Configuration holds all settings loaded from config.toml
type Configuration struct {
	General struct {
		LogLevel string `toml:"log_level" json:"log_level" jsonschema:"description=Logging level for the application,enum=DEBUG,enum=INFO,enum=WARNING,enum=ERROR,enum=CRITICAL,default=INFO"`
	} `toml:"general" json:"General"`

	IBKRConnection struct {
		Host            string `toml:"host" json:"Host" jsonschema:"description=IBKR TWS/Gateway host address,default=localhost"`
		Port            int    `toml:"port" json:"Port" jsonschema:"description=IBKR TWS/Gateway port,minimum=1,maximum=65535,default=7497"`
		ClientIDTrading int    `toml:"client_id_trading" json:"ClientIDTrading" jsonschema:"description=Client ID for trading connection,minimum=1,default=1"`
		ClientIDData    int    `toml:"client_id_data" json:"ClientIDData" jsonschema:"description=Client ID for data connection,minimum=1,default=2"`
		AccountCode     string `toml:"account_code" json:"AccountCode" jsonschema:"description=IBKR account code"`
		ReadOnlyAPI     bool   `toml:"read_only_api" json:"ReadOnlyAPI" jsonschema:"description=Whether to use read-only API mode,default=false"`
	} `toml:"ibkr_connection" json:"IBKRConnection"`

	TradingParameters struct {
		GlobalMaxConcurrentPositions  int     `toml:"global_max_concurrent_positions" json:"GlobalMaxConcurrentPositions" jsonschema:"description=Maximum number of concurrent positions,minimum=1,default=10"`
		DefaultRiskPerTradePercentage float64 `toml:"default_risk_per_trade_percentage" json:"DefaultRiskPerTradePercentage" jsonschema:"description=Percentage of account to risk per trade,minimum=0.1,maximum=5.0,default=1.0"`
		EmergencyStopLossPercentage   float64 `toml:"emergency_stop_loss_percentage" json:"EmergencyStopLossPercentage" jsonschema:"description=Emergency stop loss percentage for the portfolio,minimum=1.0,maximum=20.0,default=5.0"`
	} `toml:"trading_parameters" json:"TradingParameters"`

	OptionsFilters struct {
		// Liquidity
		MinOpenInterest           int     `toml:"min_open_interest" json:"MinOpenInterest" jsonschema:"description=Minimum open interest for an option contract,minimum=0,default=500"`
		MaxBidAskSpreadPercentage float64 `toml:"max_bid_ask_spread_percentage" json:"MaxBidAskSpreadPercentage" jsonschema:"description=Maximum bid-ask spread as a percentage of mark price,minimum=0.0,maximum=5.0,default=0.6"`

		// Volatility
		UseIVRankFilter            bool    `toml:"use_iv_rank_filter" json:"UseIVRankFilter" jsonschema:"description=Whether to filter based on IV rank,default=true"`
		MinIVRank                  float64 `toml:"min_iv_rank" json:"MinIVRank" jsonschema:"description=Minimum IV rank percentile,minimum=0.0,maximum=100.0,default=25.0"`
		MaxIVRank                  float64 `toml:"max_iv_rank" json:"MaxIVRank" jsonschema:"description=Maximum IV rank percentile,minimum=0.0,maximum=100.0,default=75.0"`
		UseIVSkewFilter            bool    `toml:"use_iv_skew_filter" json:"UseIVSkewFilter" jsonschema:"description=Whether to filter based on IV skew,default=false"`
		MinPutCallIVSkewPercentage float64 `toml:"min_put_call_iv_skew_percentage" json:"MinPutCallIVSkewPercentage" jsonschema:"description=Minimum put-call IV skew percentage,minimum=-50.0,maximum=100.0,default=-10.0"`
		MaxPutCallIVSkewPercentage float64 `toml:"max_put_call_iv_skew_percentage" json:"MaxPutCallIVSkewPercentage" jsonschema:"description=Maximum put-call IV skew percentage,minimum=-50.0,maximum=100.0,default=20.0"`

		// Probability & Risk/Reward
		UsePOPFilter                           bool    `toml:"use_pop_filter" json:"UsePOPFilter" jsonschema:"description=Whether to filter based on probability of profit,default=true"`
		MinProbabilityOfProfitPercentage       float64 `toml:"min_probability_of_profit_percentage" json:"MinProbabilityOfProfitPercentage" jsonschema:"description=Minimum probability of profit percentage,minimum=0.0,maximum=100.0,default=55.0"`
		UseWidthVsExpectedMoveFilter           bool    `toml:"use_width_vs_expected_move_filter" json:"UseWidthVsExpectedMoveFilter" jsonschema:"description=Whether to filter based on spread width vs expected move,default=true"`
		MaxSpreadWidthVsExpectedMovePercentage float64 `toml:"max_spread_width_vs_expected_move_percentage" json:"MaxSpreadWidthVsExpectedMovePercentage" jsonschema:"description=Maximum spread width as a percentage of expected move,minimum=0.0,maximum=300.0,default=120.0"`
	} `toml:"options_filters" json:"OptionsFilters"`

	GreekLimits struct {
		UseGreekLimits      bool    `toml:"use_greek_limits" json:"UseGreekLimits" jsonschema:"description=Whether to apply Greek limits to positions,default=true"`
		MaxAbsPositionDelta float64 `toml:"max_abs_position_delta" json:"MaxAbsPositionDelta" jsonschema:"description=Maximum absolute delta exposure per position,minimum=0.0,maximum=1.0,default=0.50"`
		MaxAbsPositionGamma float64 `toml:"max_abs_position_gamma" json:"MaxAbsPositionGamma" jsonschema:"description=Maximum absolute gamma exposure per position,minimum=0.0,maximum=0.2,default=0.05"`
		MaxAbsPositionVega  float64 `toml:"max_abs_position_vega" json:"MaxAbsPositionVega" jsonschema:"description=Maximum absolute vega exposure per position,minimum=0.0,maximum=50.0,default=10.0"`
		MinPositionTheta    float64 `toml:"min_position_theta" json:"MinPositionTheta" jsonschema:"description=Minimum positive theta decay per day per position,minimum=0.0,maximum=10.0,default=0.10"`
	} `toml:"greek_limits" json:"GreekLimits"`

	TradeTiming struct {
		// Dynamic DTE Calculation
		UseDynamicDTE     bool    `toml:"use_dynamic_dte" json:"UseDynamicDTE" jsonschema:"description=Whether to use dynamic DTE calculation,default=true"`
		TargetDTEMode     string  `toml:"target_dte_mode" json:"TargetDTEMode" jsonschema:"description=Mode for calculating target DTE,enum=FIXED,enum=ATR_MULTIPLE,enum=VOLATILITY_INDEX,default=ATR_MULTIPLE"`
		DTEAtrPeriod      int     `toml:"dte_atr_period" json:"DTEAtrPeriod" jsonschema:"description=ATR period for DTE calculation,minimum=1,maximum=100,default=14"`
		DTEAtrCoefficient float64 `toml:"dte_atr_coefficient" json:"DTEAtrCoefficient" jsonschema:"description=Coefficient to multiply ATR by for DTE calculation,minimum=0.1,maximum=5.0,default=1.2"`
		FixedTargetDTE    int     `toml:"fixed_target_dte" json:"FixedTargetDTE" jsonschema:"description=Fixed target DTE to use if not using dynamic calculation,minimum=1,maximum=365,default=45"`
		MinDTE            int     `toml:"min_dte" json:"MinDTE" jsonschema:"description=Minimum days to expiration,minimum=0,maximum=365,default=7"`
		MaxDTE            int     `toml:"max_dte" json:"MaxDTE" jsonschema:"description=Maximum days to expiration,minimum=1,maximum=365,default=90"`

		// Event Avoidance
		AvoidEarningsDaysBefore   int `toml:"avoid_earnings_days_before" json:"AvoidEarningsDaysBefore" jsonschema:"description=Number of days before earnings to avoid,minimum=0,maximum=30,default=3"`
		AvoidEarningsDaysAfter    int `toml:"avoid_earnings_days_after" json:"AvoidEarningsDaysAfter" jsonschema:"description=Number of days after earnings to avoid,minimum=0,maximum=30,default=1"`
		AvoidExDividendDaysBefore int `toml:"avoid_ex_dividend_days_before" json:"AvoidExDividendDaysBefore" jsonschema:"description=Number of days before ex-dividend date to avoid,minimum=0,maximum=30,default=2"`
	} `toml:"trade_timing" json:"TradeTiming"`

	StrategyDefaults map[string]map[string]interface{} `toml:"strategy_defaults" json:"StrategyDefaults"`

	Kubernetes struct {
		Namespace                  string `toml:"namespace" json:"Namespace" jsonschema:"description=Kubernetes namespace for services,default=traderadmin"`
		ConfigMapName              string `toml:"config_map_name" json:"ConfigMapName" jsonschema:"description=Name of the ConfigMap for configuration,default=traderadmin-config"`
		OrchestratorDeploymentName string `toml:"orchestrator_deployment_name" json:"OrchestratorDeploymentName" jsonschema:"description=Name of the Orchestrator deployment,default=traderadmin-orchestrator"`
	} `toml:"kubernetes" json:"Kubernetes"`

	Schedule struct {
		TradingStartTime string `toml:"trading_start_time" json:"TradingStartTime" jsonschema:"description=Trading start time (Eastern Time),default=09:30"`
		TradingEndTime   string `toml:"trading_end_time" json:"TradingEndTime" jsonschema:"description=Trading end time (Eastern Time),default=16:00"`
		WeekendTrading   bool   `toml:"weekend_trading" json:"WeekendTrading" jsonschema:"description=Whether to allow trading on weekends,default=false"`
	} `toml:"schedule" json:"Schedule"`

	TradingSchedule struct {
		Enabled      bool     `toml:"enabled" json:"Enabled" jsonschema:"description=Master switch for the scheduler,default=true"`
		StartTimeUTC string   `toml:"start_time_utc" json:"StartTimeUTC" jsonschema:"description=Trading start time in HH:MM format (UTC),default=13:30"`
		StopTimeUTC  string   `toml:"stop_time_utc" json:"StopTimeUTC" jsonschema:"description=Trading stop time in HH:MM format (UTC),default=20:00"`
		DaysOfWeek   []string `toml:"days_of_week" json:"DaysOfWeek" jsonschema:"description=Days of the week when trading is allowed,enum=Mon,enum=Tue,enum=Wed,enum=Thu,enum=Fri,enum=Sat,enum=Sun"`
	} `toml:"trading_schedule" json:"TradingSchedule"`

	AlertsConfig struct {
		Enabled    bool `toml:"enabled" json:"Enabled" jsonschema:"description=Enable the alerting system,default=true"`
		Thresholds struct {
			MaxOrderLatencyMs                   float64 `toml:"max_order_latency_ms" json:"MaxOrderLatencyMs" jsonschema:"description=Maximum acceptable order latency in milliseconds,minimum=0,default=1000"`
			MinDailyRealizedPnl                 float64 `toml:"min_daily_realized_pnl" json:"MinDailyRealizedPnl" jsonschema:"description=Minimum acceptable daily realized P&L,default=-500.0"`
			MaxPortfolioDrawdownPercentageToday float64 `toml:"max_portfolio_drawdown_percentage_today" json:"MaxPortfolioDrawdownPercentageToday" jsonschema:"description=Maximum acceptable portfolio drawdown percentage for the day,minimum=0,maximum=100,default=5.0"`
			MaxApiErrorsPerHour                 int     `toml:"max_api_errors_per_hour" json:"MaxApiErrorsPerHour" jsonschema:"description=Maximum acceptable API errors per hour,minimum=0,default=10"`
		} `toml:"thresholds" json:"Thresholds"`
		Notifications struct {
			Email struct {
				Enabled    bool     `toml:"enabled" json:"Enabled" jsonschema:"description=Enable email notifications,default=false"`
				Recipients []string `toml:"recipients" json:"Recipients" jsonschema:"description=List of email recipients"`
				SmtpHost   string   `toml:"smtp_host" json:"SmtpHost" jsonschema:"description=SMTP server hostname"`
				SmtpPort   int      `toml:"smtp_port" json:"SmtpPort" jsonschema:"description=SMTP server port,minimum=1,maximum=65535,default=587"`
				SmtpUser   string   `toml:"smtp_user" json:"SmtpUser" jsonschema:"description=SMTP server username"`
				SmtpPass   string   `toml:"smtp_pass" json:"SmtpPass" jsonschema:"description=SMTP server password (or environment variable name)"`
			} `toml:"email" json:"Email"`
			Slack struct {
				Enabled    bool   `toml:"enabled" json:"Enabled" jsonschema:"description=Enable Slack notifications,default=false"`
				WebhookUrl string `toml:"webhook_url" json:"WebhookUrl" jsonschema:"description=Slack webhook URL (or environment variable name)"`
			} `toml:"slack" json:"Slack"`
		} `toml:"notifications" json:"Notifications"`
	} `toml:"alerts_config" json:"AlertsConfig"`
}

// StatusInfo represents the current status of the application
type StatusInfo struct {
	IBKR struct {
		Connected     bool      `json:"connected"`
		LastConnected time.Time `json:"lastConnected,omitempty"`
		Error         string    `json:"error,omitempty"`
	} `json:"ibkr"`
	Services []struct {
		Name        string    `json:"name"`
		Running     bool      `json:"running"`
		Health      string    `json:"health"` // "healthy", "unhealthy", "unknown"
		LastChecked time.Time `json:"lastChecked"`
		Message     string    `json:"message,omitempty"`
	} `json:"services"`
	ActivePositions int       `json:"activePositions"`
	TradingActive   bool      `json:"tradingActive"`
	IsTradingHours  bool      `json:"isTradingHours"`
	LastUpdated     time.Time `json:"lastUpdated"`
}

// App struct
type App struct {
	ctx            context.Context
	config         Configuration
	configPath     string
	watcher        *fsnotify.Watcher
	configLoaded   bool
	status         StatusInfo
	lastUpdated    time.Time
	k8sClient      *kubernetes.Clientset
	k8sConfig      *rest.Config
	servicesPaused bool
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{
		configPath:     "config/config.toml", // Default path relative to executable
		servicesPaused: false,
	}
}

// Initializes Kubernetes client
func (a *App) initKubernetesClient() error {
	var k8sConfig *rest.Config
	var err error

	// Try to use in-cluster config first (for when running inside Kubernetes)
	k8sConfig, err = rest.InClusterConfig()
	if err != nil {
		// If that fails, try to use local kubeconfig
		kubeconfig := os.Getenv("KUBECONFIG")
		if kubeconfig == "" {
			// If KUBECONFIG is not set, use default location
			home, err := os.UserHomeDir()
			if err != nil {
				return fmt.Errorf("failed to find home directory: %w", err)
			}
			kubeconfig = filepath.Join(home, ".kube", "config")
		}

		k8sConfig, err = clientcmd.BuildConfigFromFlags("", kubeconfig)
		if err != nil {
			return fmt.Errorf("failed to build kubeconfig: %w", err)
		}
	}

	// Create the clientset
	clientset, err := kubernetes.NewForConfig(k8sConfig)
	if err != nil {
		return fmt.Errorf("failed to create Kubernetes client: %w", err)
	}

	a.k8sClient = clientset
	a.k8sConfig = k8sConfig
	return nil
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx

	// Initialize config watcher
	var err error
	a.watcher, err = fsnotify.NewWatcher()
	if err != nil {
		log.Error().Err(err).Msg("Failed to create config watcher")
		return
	}

	// Load initial configuration
	if err := a.LoadConfig(); err != nil {
		log.Error().Err(err).Msg("Failed to load initial configuration")
	}

	// Initialize status
	a.initializeStatus()

	// Initialize Kubernetes client (can be used later for service management)
	if err := a.initKubernetesClient(); err != nil {
		log.Warn().Err(err).Msg("Failed to initialize Kubernetes client, service management may not work")
	}

	// Start watching config file for changes
	go a.watchConfig()
}

// initializeStatus initializes the status info with default values
func (a *App) initializeStatus() {
	now := time.Now()
	a.status = StatusInfo{
		IBKR: struct {
			Connected     bool      `json:"connected"`
			LastConnected time.Time `json:"lastConnected,omitempty"`
			Error         string    `json:"error,omitempty"`
		}{
			Connected: false,
		},
		Services: []struct {
			Name        string    `json:"name"`
			Running     bool      `json:"running"`
			Health      string    `json:"health"`
			LastChecked time.Time `json:"lastChecked"`
			Message     string    `json:"message,omitempty"`
		}{
			{
				Name:        "Orchestrator",
				Running:     false,
				Health:      "unknown",
				LastChecked: now,
			},
			{
				Name:        "Scanner",
				Running:     false,
				Health:      "unknown",
				LastChecked: now,
			},
		},
		ActivePositions: 0,
		TradingActive:   false,
		IsTradingHours:  a.isTradingHours(),
		LastUpdated:     now,
	}
	a.lastUpdated = now
}

// isTradingHours checks if the current time is within trading hours
func (a *App) isTradingHours() bool {
	now := time.Now()

	// Check if it's a weekend (Saturday=6, Sunday=0)
	if now.Weekday() == time.Saturday || now.Weekday() == time.Sunday {
		if !a.config.Schedule.WeekendTrading {
			return false
		}
	}

	// Simple implementation - assuming times are in the format "HH:MM" and in Eastern Time
	// In a real implementation, would need to handle time zones properly
	hour, minute := now.Hour(), now.Minute()
	currentTimeMinutes := hour*60 + minute

	// Parse trading start time
	var startHour, startMinute int
	fmt.Sscanf(a.config.Schedule.TradingStartTime, "%d:%d", &startHour, &startMinute)
	startTimeMinutes := startHour*60 + startMinute

	// Parse trading end time
	var endHour, endMinute int
	fmt.Sscanf(a.config.Schedule.TradingEndTime, "%d:%d", &endHour, &endMinute)
	endTimeMinutes := endHour*60 + endMinute

	return currentTimeMinutes >= startTimeMinutes && currentTimeMinutes <= endTimeMinutes
}

// LoadConfig loads the configuration from the config file
func (a *App) LoadConfig() error {
	absPath, err := filepath.Abs(a.configPath)
	if err != nil {
		return fmt.Errorf("failed to get absolute path: %w", err)
	}

	_, err = os.Stat(absPath)
	if os.IsNotExist(err) {
		return fmt.Errorf("config file not found at %s", absPath)
	}

	_, err = toml.DecodeFile(absPath, &a.config)
	if err != nil {
		return fmt.Errorf("failed to decode config file: %w", err)
	}

	// Start watching the config file directory
	configDir := filepath.Dir(absPath)
	if err := a.watcher.Add(configDir); err != nil {
		log.Error().Err(err).Str("dir", configDir).Msg("Failed to watch config directory")
	}

	a.configLoaded = true
	log.Info().Str("path", absPath).Msg("Configuration loaded successfully")

	return nil
}

// SaveConfig saves the current configuration to the config file
func (a *App) SaveConfig() error {
	// Create a backup of the current config file
	if _, err := os.Stat(a.configPath); err == nil {
		backupPath := a.configPath + ".bak"
		if err := os.Rename(a.configPath, backupPath); err != nil {
			log.Warn().Err(err).Msg("Failed to create backup of config file")
			// Continue anyway - we'll try to write the new file
		}
	}

	// Create the config file
	file, err := os.Create(a.configPath)
	if err != nil {
		return fmt.Errorf("failed to create config file: %w", err)
	}
	defer file.Close()

	encoder := toml.NewEncoder(file)
	if err := encoder.Encode(a.config); err != nil {
		return fmt.Errorf("failed to encode config: %w", err)
	}

	log.Info().Str("path", a.configPath).Msg("Configuration saved successfully")
	return nil
}

// watchConfig watches for changes to the config file and reloads it when changed
func (a *App) watchConfig() {
	defer a.watcher.Close()

	for {
		select {
		case event, ok := <-a.watcher.Events:
			if !ok {
				return
			}

			if event.Op&fsnotify.Write == fsnotify.Write || event.Op&fsnotify.Create == fsnotify.Create {
				if filepath.Base(event.Name) == filepath.Base(a.configPath) {
					log.Info().Msg("Config file changed, reloading...")
					if err := a.LoadConfig(); err != nil {
						log.Error().Err(err).Msg("Failed to reload configuration")
					}
				}
			}
		case err, ok := <-a.watcher.Errors:
			if !ok {
				return
			}
			log.Error().Err(err).Msg("Config watcher error")
		}
	}
}

// GetConfig returns the current configuration (for frontend)
func (a *App) GetConfig() Configuration {
	log.Debug().Interface("config", a.config).Msg("Returning config data to frontend")
	return a.config
}

// UpdateConfig updates the configuration and saves it
func (a *App) UpdateConfig(newConfig Configuration) error {
	a.config = newConfig
	return a.SaveConfig()
}

// IsConfigLoaded returns whether the configuration has been loaded
func (a *App) IsConfigLoaded() bool {
	return a.configLoaded
}

// GetConfigSchema generates a JSONSchema from the Configuration struct
func (a *App) GetConfigSchema() (string, error) {
	// Use reflection to generate a JSONSchema from the Configuration struct
	// In a real implementation, this would use a proper JSONSchema generator

	// Create a basic schema structure
	schema := map[string]interface{}{
		"$schema": "http://json-schema.org/draft-07/schema#",
		"title":   "TraderAdmin Configuration",
		"type":    "object",
		"properties": map[string]interface{}{
			"General": map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"LogLevel": map[string]interface{}{
						"type":        "string",
						"enum":        []string{"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"},
						"default":     "INFO",
						"description": "Logging level for the application",
					},
				},
			},
			"IBKRConnection": map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"Host": map[string]interface{}{
						"type":        "string",
						"default":     "localhost",
						"description": "IBKR TWS/Gateway host address",
					},
					"Port": map[string]interface{}{
						"type":        "integer",
						"minimum":     1,
						"maximum":     65535,
						"default":     7497,
						"description": "IBKR TWS/Gateway port",
					},
					"ClientIDTrading": map[string]interface{}{
						"type":        "integer",
						"minimum":     1,
						"default":     1,
						"description": "Client ID for trading connection",
					},
					"ClientIDData": map[string]interface{}{
						"type":        "integer",
						"minimum":     1,
						"default":     2,
						"description": "Client ID for data connection",
					},
					"AccountCode": map[string]interface{}{
						"type":        "string",
						"description": "IBKR account code",
					},
					"ReadOnlyAPI": map[string]interface{}{
						"type":        "boolean",
						"default":     false,
						"description": "Whether to use read-only API mode",
					},
				},
				"required": []string{"Host", "Port", "ClientIDTrading", "AccountCode"},
			},
			"TradingParameters": map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"GlobalMaxConcurrentPositions": map[string]interface{}{
						"type":        "integer",
						"minimum":     1,
						"default":     10,
						"description": "Maximum number of concurrent positions",
					},
					"DefaultRiskPerTradePercentage": map[string]interface{}{
						"type":        "number",
						"minimum":     0.1,
						"maximum":     5.0,
						"default":     1.0,
						"description": "Percentage of account to risk per trade",
					},
					"EmergencyStopLossPercentage": map[string]interface{}{
						"type":        "number",
						"minimum":     1.0,
						"maximum":     20.0,
						"default":     5.0,
						"description": "Emergency stop loss percentage for the portfolio",
					},
				},
			},
		},
	}

	// Convert the schema to JSON
	schemaJSON, err := json.MarshalIndent(schema, "", "  ")
	if err != nil {
		return "", fmt.Errorf("failed to marshal schema to JSON: %w", err)
	}

	return string(schemaJSON), nil
}

// GetStatus returns the current status of the application
func (a *App) GetStatus() StatusInfo {
	// First check if we're connected to IBKR
	ibkrConnected := a.TestIBKRConnection()

	now := time.Now()
	a.lastUpdated = now

	// Update status with real information
	a.status.IBKR.Connected = ibkrConnected
	if ibkrConnected {
		a.status.IBKR.LastConnected = now
		a.status.IBKR.Error = ""
	} else {
		a.status.IBKR.Error = "Unable to connect to Interactive Brokers TWS/Gateway"
	}

	// Update trading hours status
	a.status.IsTradingHours = a.isTradingHours()

	// Get active positions count - TODO: implement real count from IBKR position data
	// For now just return the placeholder

	// Update services status - when we have real k8s integration
	if a.k8sClient != nil {
		a.updateServicesStatus()
	}

	a.status.LastUpdated = now
	return a.status
}

// updateServicesStatus checks the status of trading services in Kubernetes
func (a *App) updateServicesStatus() {
	if a.k8sClient == nil {
		return
	}

	namespace := a.config.Kubernetes.Namespace
	if namespace == "" {
		namespace = "traderadmin"
	}

	// List deployments to check service status
	deployments, err := a.k8sClient.AppsV1().Deployments(namespace).List(context.Background(), metav1.ListOptions{})
	if err != nil {
		log.Error().Err(err).Msg("Failed to list deployments")
		return
	}

	// Clear existing services array
	a.status.Services = make([]struct {
		Name        string    `json:"name"`
		Running     bool      `json:"running"`
		Health      string    `json:"health"`
		LastChecked time.Time `json:"lastChecked"`
		Message     string    `json:"message,omitempty"`
	}, 0)

	for _, deployment := range deployments.Items {
		if deployment.Labels["app"] == "traderadmin" {
			serviceStatus := struct {
				Name        string    `json:"name"`
				Running     bool      `json:"running"`
				Health      string    `json:"health"`
				LastChecked time.Time `json:"lastChecked"`
				Message     string    `json:"message,omitempty"`
			}{
				Name:        deployment.Name,
				LastChecked: time.Now(),
			}

			// Check if deployment is available
			if deployment.Status.AvailableReplicas > 0 {
				serviceStatus.Running = true
				serviceStatus.Health = "healthy"
			} else {
				serviceStatus.Running = false
				serviceStatus.Health = "unhealthy"
				serviceStatus.Message = fmt.Sprintf("Deployment has %d/%d replicas available",
					deployment.Status.AvailableReplicas, *deployment.Spec.Replicas)
			}

			a.status.Services = append(a.status.Services, serviceStatus)
		}
	}
}

// TestIBKRConnection tests the connection to IBKR
func (a *App) TestIBKRConnection() bool {
	// Try to connect to the IBKR TWS/Gateway API
	host := a.config.IBKRConnection.Host
	port := a.config.IBKRConnection.Port

	// Simple TCP connection test to see if TWS/Gateway is running
	address := fmt.Sprintf("%s:%d", host, port)
	conn, err := net.DialTimeout("tcp", address, 2*time.Second)

	if err != nil {
		log.Warn().Err(err).Str("address", address).Msg("Failed to connect to IBKR TWS/Gateway")
		return false
	}

	// Successfully connected
	conn.Close()
	log.Info().Str("address", address).Msg("Successfully connected to IBKR TWS/Gateway")
	return true
}

// shutdown is called when the app is about to quit
func (a *App) shutdown(ctx context.Context) {
	if a.watcher != nil {
		a.watcher.Close()
	}
}

// PauseTradingServices pauses all trading services by scaling down their Kubernetes deployments
func (a *App) PauseTradingServices() error {
	if a.k8sClient == nil {
		return fmt.Errorf("Kubernetes client not initialized")
	}

	namespace := a.config.Kubernetes.Namespace
	log.Info().Str("namespace", namespace).Msg("Pausing trading services")

	// Get deployments to pause (e.g., orchestrator, scanner)
	deploymentsToScale := []string{
		a.config.Kubernetes.OrchestratorDeploymentName,
		// Add other deployments as needed
	}

	// Scale down each deployment to 0 replicas
	for _, deploymentName := range deploymentsToScale {
		scale, err := a.k8sClient.AppsV1().Deployments(namespace).GetScale(a.ctx, deploymentName, metav1.GetOptions{})
		if err != nil {
			log.Error().Err(err).Str("deployment", deploymentName).Msg("Failed to get deployment scale")
			continue
		}

		// Record original scale for later
		log.Info().Str("deployment", deploymentName).Int32("replicas", scale.Spec.Replicas).Msg("Current deployment scale")

		// Set replicas to 0
		scale.Spec.Replicas = 0
		_, err = a.k8sClient.AppsV1().Deployments(namespace).UpdateScale(a.ctx, deploymentName, scale, metav1.UpdateOptions{})
		if err != nil {
			return fmt.Errorf("failed to scale down deployment %s: %w", deploymentName, err)
		}

		log.Info().Str("deployment", deploymentName).Msg("Successfully scaled down deployment")
	}

	a.servicesPaused = true
	return nil
}

// ResumeTradingServices resumes all trading services by scaling up their Kubernetes deployments
func (a *App) ResumeTradingServices() error {
	if a.k8sClient == nil {
		return fmt.Errorf("Kubernetes client not initialized")
	}

	namespace := a.config.Kubernetes.Namespace
	log.Info().Str("namespace", namespace).Msg("Resuming trading services")

	// Get deployments to resume
	deploymentsToScale := []string{
		a.config.Kubernetes.OrchestratorDeploymentName,
		// Add other deployments as needed
	}

	// Scale up each deployment to 1 replica (or original replica count)
	for _, deploymentName := range deploymentsToScale {
		scale, err := a.k8sClient.AppsV1().Deployments(namespace).GetScale(a.ctx, deploymentName, metav1.GetOptions{})
		if err != nil {
			log.Error().Err(err).Str("deployment", deploymentName).Msg("Failed to get deployment scale")
			continue
		}

		// Set replicas to 1 (or the original value if you kept track of it)
		scale.Spec.Replicas = 1
		_, err = a.k8sClient.AppsV1().Deployments(namespace).UpdateScale(a.ctx, deploymentName, scale, metav1.UpdateOptions{})
		if err != nil {
			return fmt.Errorf("failed to scale up deployment %s: %w", deploymentName, err)
		}

		log.Info().Str("deployment", deploymentName).Msg("Successfully scaled up deployment")
	}

	a.servicesPaused = false
	return nil
}

// SaveConfigurationAndRestart saves the configuration and restarts the services
func (a *App) SaveConfigurationAndRestart(configData map[string]interface{}) error {
	var err error

	// Step 1: Pause trading services
	if !a.servicesPaused {
		err = a.PauseTradingServices()
		if err != nil {
			return fmt.Errorf("failed to pause trading services: %w", err)
		}
	}

	// Step 2: Validate & Save configuration
	// Create a JSON string from the map
	jsonBytes, err := json.Marshal(configData)
	if err != nil {
		return fmt.Errorf("failed to marshal config data: %w", err)
	}

	// Create a new Configuration object
	var newConfig Configuration
	err = json.Unmarshal(jsonBytes, &newConfig)
	if err != nil {
		return fmt.Errorf("failed to unmarshal config data: %w", err)
	}

	// Create a backup of the current config file
	if _, err := os.Stat(a.configPath); err == nil {
		timestamp := time.Now().Format("20060102_150405")
		backupPath := fmt.Sprintf("%s.bak.%s", a.configPath, timestamp)
		if err := copyFile(a.configPath, backupPath); err != nil {
			log.Warn().Err(err).Msg("Failed to create backup of config file")
			// Continue anyway - we'll try to write the new file
		} else {
			log.Info().Str("backup", backupPath).Msg("Created backup of config file")
		}
	}

	// Update the app's configuration
	a.config = newConfig

	// Save the new configuration
	err = a.SaveConfig()
	if err != nil {
		return fmt.Errorf("failed to save configuration: %w", err)
	}

	// Step 3: Resume trading services
	err = a.ResumeTradingServices()
	if err != nil {
		log.Error().Err(err).Msg("Failed to resume trading services, but configuration was saved")
		return fmt.Errorf("configuration saved, but failed to resume services: %w", err)
	}

	log.Info().Msg("Successfully saved configuration and restarted services")
	return nil
}

// Helper function to copy a file
func copyFile(src, dst string) error {
	// Read the source file
	data, err := os.ReadFile(src)
	if err != nil {
		return fmt.Errorf("failed to read source file: %w", err)
	}

	// Write to the destination file
	err = os.WriteFile(dst, data, 0644)
	if err != nil {
		return fmt.Errorf("failed to write destination file: %w", err)
	}

	return nil
}

// GetLatestMetrics returns the latest metrics for the system
func (a *App) GetLatestMetrics() (models.AllMetrics, error) {
	now := time.Now()

	// Create a metrics object with realistic initial values as fallback
	metrics := models.AllMetrics{
		Portfolio: models.PortfolioMetrics{
			Timestamp:          now,
			Equity:             0.00, // Will be filled with real data if possible
			RealizedPNLToday:   0.00,
			UnrealizedPNL:      0.00,
			OpenPositionsCount: 0,
			BuyingPower:        0.00,
		},
		Trades: models.TradeStatsToday{
			ExecutedCount: 0,
			WinCount:      0,
			LossCount:     0,
			WinRate:       0.0,
			AvgWinAmount:  0.00,
			AvgLossAmount: 0.00,
		},
		System: models.SystemHealthMetrics{
			AvgOrderLatencyMs: 120.5,
			ApiErrorCount:     0,
			LastDataSync:      now,
		},
		OpenPositions: []models.Position{},
	}

	// If connected to IBKR, try to fetch real account data
	if a.status.IBKR.Connected {
		log.Info().Msg("Attempting to fetch real account data from IBKR")

		// Direct socket API check (simple implementation)
		// This just verifies we can establish communication
		host := a.config.IBKRConnection.Host
		port := a.config.IBKRConnection.Port
		address := fmt.Sprintf("%s:%d", host, port)

		conn, err := net.DialTimeout("tcp", address, 2*time.Second)
		if err != nil {
			log.Error().Err(err).Msg("Failed to connect to IBKR for metrics")
			return metrics, nil // Return placeholder metrics
		}
		defer conn.Close()

		// In a future implementation, this would be replaced with full TWS API calls
		// For now we'll try to send a minimal request to see if we can get account data
		// Note: For real implementation, you would use the official IBKR API client

		// While we don't have full API integration, at least show zeros instead of placeholders
		// to indicate we're connected but not showing mock data
		metrics.Portfolio.Equity = 0.00
		metrics.Portfolio.BuyingPower = 0.00
		metrics.Portfolio.RealizedPNLToday = 0.00
		metrics.Portfolio.UnrealizedPNL = 0.00

		// Set last data sync to now since we've checked connection
		metrics.System.LastDataSync = now
	} else {
		log.Warn().Msg("Not connected to IBKR, using placeholder metrics")
	}

	return metrics, nil
}

// TestAlertNotification sends a test alert to the specified channel
func (a *App) TestAlertNotification(channelType string, message string) error {
	log.Info().Str("channel", channelType).Str("message", message).Msg("Sending test alert notification")

	// In a real implementation, this would actually send the notification
	// through the specified channel (email, Slack, etc.)

	switch channelType {
	case "email":
		if !a.config.AlertsConfig.Notifications.Email.Enabled {
			return fmt.Errorf("email notifications are not enabled")
		}

		// Here we would use a library like gomail to send actual emails
		recipientCount := len(a.config.AlertsConfig.Notifications.Email.Recipients)
		if recipientCount == 0 {
			return fmt.Errorf("no email recipients configured")
		}

		log.Info().Int("recipient_count", recipientCount).Msg("Would send email notification")

	case "slack":
		if !a.config.AlertsConfig.Notifications.Slack.Enabled {
			return fmt.Errorf("slack notifications are not enabled")
		}

		webhookUrl := a.config.AlertsConfig.Notifications.Slack.WebhookUrl
		if webhookUrl == "" {
			return fmt.Errorf("slack webhook URL not configured")
		}

		log.Info().Str("webhook_url", webhookUrl).Msg("Would send Slack notification")

	default:
		return fmt.Errorf("unsupported notification channel: %s", channelType)
	}

	// Simulate a successful notification
	time.Sleep(500 * time.Millisecond)

	return nil
}
