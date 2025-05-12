// Configuration interfaces matching the Go structs

export interface Config {
  ibkr: IBKRConfig;
  trading: TradingConfig;
  strategies: Record<string, StrategyConfig>;
  options: OptionsConfig;
  greeks: GreeksConfig;
  probability: ProbabilityConfig;
  events: EventsConfig;
  dte: DTEConfig;
  universe: UniverseConfig;
  scanner: ScannerConfig;
  data_management: DataManagementConfig;
  logging: LoggingConfig;
  scheduling: SchedulingConfig;
  monitoring: MonitoringConfig;
  alerts: AlertsConfig;
  backup: BackupConfig;
  kubernetes: KubernetesConfig;
}

export interface IBKRConfig {
  host: string;
  port: number;
  client_id: number;
  read_only: boolean;
}

export interface TradingConfig {
  mode: string;
  max_positions: number;
  risk_per_trade_pct: number;
  max_loss_pct: number;
}

export interface StrategyConfig {
  active: boolean;
  min_rsi: number;
  max_atr_ratio: number;
  min_iv_rank: number;
  max_delta: number;
  min_days_to_expiry: number;
  max_days_to_expiry: number;
  target_profit_pct: number;
  stop_loss_pct: number;
}

export interface OptionsConfig {
  min_open_interest: number;
  max_bid_ask_spread_pct: number;
  preferred_expiration_days: number[];
  strike_price_increment: number;
  min_iv_rank: number;
  max_iv_rank: number;
  min_call_put_skew_pct: number;
}

export interface GreeksConfig {
  max_theta_per_day: number;
  max_vega_exposure: number;
  max_gamma_exposure: number;
}

export interface ProbabilityConfig {
  min_pop: number;
  max_width_vs_move_pct: number;
}

export interface EventsConfig {
  skip_earnings_days: number;
  skip_exdiv_days: number;
}

export interface DTEConfig {
  dynamic: boolean;
  dte_coefficient: number;
}

export interface UniverseConfig {
  symbols: string[];
  min_market_cap: number;
  max_volatility: number;
  sectors: string[];
}

export interface ScannerConfig {
  scan_interval_seconds: number;
  lookback_days: number;
  min_volume: number;
  use_premarket_data: boolean;
}

export interface DataManagementConfig {
  cache_dir: string;
  data_retention_days: number;
  enable_daily_cleanup: boolean;
}

export interface LoggingConfig {
  level: string;
  file: string;
  max_size_mb: number;
  max_backups: number;
  max_age_days: number;
}

export interface SchedulingConfig {
  trading_start_time: string;
  trading_end_time: string;
  timezone: string;
  trading_days: string[];
  maintenance_window: string;
}

export interface MonitoringConfig {
  prometheus_port: number;
  metrics_interval_seconds: number;
  health_check_url: string;
}

export interface AlertsConfig {
  enable_email: boolean;
  email_to: string;
  enable_slack: boolean;
  slack_webhook_url: string;
  alert_on_errors: boolean;
  alert_on_trades: boolean;
}

export interface BackupConfig {
  auto_backup: boolean;
  backup_interval_hours: number;
  backup_dir: string;
  keep_backups: number;
}

export interface KubernetesConfig {
  namespace: string;
  config_map_name: string;
  orchestrator_deployment: string;
  scanner_deployment: string;
}

export interface OptionContract {
  expiry: string;
  strike: number;
  type: string;
  bid: number;
  ask: number;
  iv: number;
  ivRank: number;
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  openInterest: number;
  volume: number;
  bidAskSpreadPct: number;
  probabilityOTM: number;
}

// Status interfaces
export interface StatusInfo {
  ibkrConnected: boolean;
  ibkrError?: string;
  containers: ContainerStatusInfo[];
}

export interface ContainerStatusInfo {
  name: string;
  state: string;
}
