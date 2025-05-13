export namespace main {

	export class Configuration {
	    // Go type: struct { LogLevel string "toml:\"log_level\" json:\"log_level\" jsonschema:\"description=Logging level for the application,enum=DEBUG,enum=INFO,enum=WARNING,enum=ERROR,enum=CRITICAL,default=INFO\"" }
	    General: any;
	    // Go type: struct { Host string "toml:\"host\" json:\"Host\" jsonschema:\"description=IBKR TWS/Gateway host address,default=localhost\""; Port int "toml:\"port\" json:\"Port\" jsonschema:\"description=IBKR TWS/Gateway port,minimum=1,maximum=65535,default=7497\""; ClientIDTrading int "toml:\"client_id_trading\" json:\"ClientIDTrading\" jsonschema:\"description=Client ID for trading connection,minimum=1,default=1\""; ClientIDData int "toml:\"client_id_data\" json:\"ClientIDData\" jsonschema:\"description=Client ID for data connection,minimum=1,default=2\""; AccountCode string "toml:\"account_code\" json:\"AccountCode\" jsonschema:\"description=IBKR account code\""; ReadOnlyAPI bool "toml:\"read_only_api\" json:\"ReadOnlyAPI\" jsonschema:\"description=Whether to use read-only API mode,default=false\"" }
	    IBKRConnection: any;
	    TradingParameters: struct { GlobalMaxConcurrentPositions int "toml:\"global_max_concurrent_positions\" json:\"GlobalMaxConcurrentPositions\" jsonschema:\"description=Maximum number of concurrent positions,minimum=1,default=10\""; DefaultRiskPerTradePercentage float64 "toml:\"default_risk_per_trade_percentage\" json:\"DefaultRiskPerTradePercentage\" jsonschema:\"description=Percentage of account to risk per trade,minimum=0.;
	    OptionsFilters: struct { MinOpenInterest int "toml:\"min_open_interest\" json:\"MinOpenInterest\" jsonschema:\"description=Minimum open interest for an option contract,minimum=0,default=500\""; MaxBidAskSpreadPercentage float64 "toml:\"max_bid_ask_spread_percentage\" json:\"MaxBidAskSpreadPercentage\" jsonschema:\"description=Maximum bid-ask spread as a percentage of mark price,minimum=0.;
	    GreekLimits: struct { UseGreekLimits bool "toml:\"use_greek_limits\" json:\"UseGreekLimits\" jsonschema:\"description=Whether to apply Greek limits to positions,default=true\""; MaxAbsPositionDelta float64 "toml:\"max_abs_position_delta\" json:\"MaxAbsPositionDelta\" jsonschema:\"description=Maximum absolute delta exposure per position,minimum=0.;
	    TradeTiming: struct { UseDynamicDTE bool "toml:\"use_dynamic_dte\" json:\"UseDynamicDTE\" jsonschema:\"description=Whether to use dynamic DTE calculation,default=true\""; TargetDTEMode string "toml:\"target_dte_mode\" json:\"TargetDTEMode\" jsonschema:\"description=Mode for calculating target DTE,enum=FIXED,enum=ATR_MULTIPLE,enum=VOLATILITY_INDEX,default=ATR_MULTIPLE\""; DTEAtrPeriod int "toml:\"dte_atr_period\" json:\"DTEAtrPeriod\" jsonschema:\"description=ATR period for DTE calculation,minimum=1,maximum=100,default=14\""; DTEAtrCoefficient float64 "toml:\"dte_atr_coefficient\" json:\"DTEAtrCoefficient\" jsonschema:\"description=Coefficient to multiply ATR by for DTE calculation,minimum=0.;
	    StrategyDefaults: Record<string, any>;
	    // Go type: struct { Namespace string "toml:\"namespace\" json:\"Namespace\" jsonschema:\"description=Kubernetes namespace for services,default=traderadmin\""; ConfigMapName string "toml:\"config_map_name\" json:\"ConfigMapName\" jsonschema:\"description=Name of the ConfigMap for configuration,default=traderadmin-config\""; OrchestratorDeploymentName string "toml:\"orchestrator_deployment_name\" json:\"OrchestratorDeploymentName\" jsonschema:\"description=Name of the Orchestrator deployment,default=traderadmin-orchestrator\"" }
	    Kubernetes: any;
	    // Go type: struct { TradingStartTime string "toml:\"trading_start_time\" json:\"TradingStartTime\" jsonschema:\"description=Trading start time (Eastern Time),default=09:30\""; TradingEndTime string "toml:\"trading_end_time\" json:\"TradingEndTime\" jsonschema:\"description=Trading end time (Eastern Time),default=16:00\""; WeekendTrading bool "toml:\"weekend_trading\" json:\"WeekendTrading\" jsonschema:\"description=Whether to allow trading on weekends,default=false\"" }
	    Schedule: any;
	    // Go type: struct { Enabled bool "toml:\"enabled\" json:\"Enabled\" jsonschema:\"description=Master switch for the scheduler,default=true\""; StartTimeUTC string "toml:\"start_time_utc\" json:\"StartTimeUTC\" jsonschema:\"description=Trading start time in HH:MM format (UTC),default=13:30\""; StopTimeUTC string "toml:\"stop_time_utc\" json:\"StopTimeUTC\" jsonschema:\"description=Trading stop time in HH:MM format (UTC),default=20:00\""; DaysOfWeek []string "toml:\"days_of_week\" json:\"DaysOfWeek\" jsonschema:\"description=Days of the week when trading is allowed,enum=Mon,enum=Tue,enum=Wed,enum=Thu,enum=Fri,enum=Sat,enum=Sun\"" }
	    TradingSchedule: any;
	    // Go type: struct { Enabled bool "toml:\"enabled\" json:\"Enabled\" jsonschema:\"description=Enable the alerting system,default=true\""; Thresholds struct { MaxOrderLatencyMs float64 "toml:\"max_order_latency_ms\" json:\"MaxOrderLatencyMs\" jsonschema:\"description=Maximum acceptable order latency in milliseconds,minimum=0,default=1000\""; MinDailyRealizedPnl float64 "toml:\"min_daily_realized_pnl\" json:\"MinDailyRealizedPnl\" jsonschema:\"description=Minimum acceptable daily realized P&L,default=-500
	    AlertsConfig: any;

	    static createFrom(source: any = {}) {
	        return new Configuration(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.General = this.convertValues(source["General"], Object);
	        this.IBKRConnection = this.convertValues(source["IBKRConnection"], Object);
	        this.TradingParameters = this.convertValues(source["TradingParameters"], Object);
	        this.OptionsFilters = this.convertValues(source["OptionsFilters"], Object);
	        this.GreekLimits = this.convertValues(source["GreekLimits"], Object);
	        this.TradeTiming = this.convertValues(source["TradeTiming"], Object);
	        this.StrategyDefaults = source["StrategyDefaults"];
	        this.Kubernetes = this.convertValues(source["Kubernetes"], Object);
	        this.Schedule = this.convertValues(source["Schedule"], Object);
	        this.TradingSchedule = this.convertValues(source["TradingSchedule"], Object);
	        this.AlertsConfig = this.convertValues(source["AlertsConfig"], Object);
	    }

		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}
	export class StatusInfo {
	    ibkr: struct { Connected bool "json:\"connected\""; LastConnected time.;
	    services: struct { Name string "json:\"name\""; Running bool "json:\"running\""; Health string "json:\"health\""; LastChecked time.Time "json:\"lastChecked\""; Message string "json:\"message,omitempty\"" }[];
	    activePositions: number;
	    tradingActive: boolean;
	    isTradingHours: boolean;
	    // Go type: time
	    lastUpdated: any;

	    static createFrom(source: any = {}) {
	        return new StatusInfo(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.ibkr = this.convertValues(source["ibkr"], Object);
	        this.services = this.convertValues(source["services"], struct { Name string "json:\"name\""; Running bool "json:\"running\""; Health string "json:\"health\""; LastChecked time.Time "json:\"lastChecked\""; Message string "json:\"message,omitempty\"" });
	        this.activePositions = source["activePositions"];
	        this.tradingActive = source["tradingActive"];
	        this.isTradingHours = source["isTradingHours"];
	        this.lastUpdated = this.convertValues(source["lastUpdated"], null);
	    }

		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}

}

export namespace models {

	export class Position {
	    symbol: string;
	    quantity: number;
	    entryPrice: number;
	    currentPrice: number;
	    unrealizedPl: number;
	    strategy: string;
	    openTime: string;

	    static createFrom(source: any = {}) {
	        return new Position(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.symbol = source["symbol"];
	        this.quantity = source["quantity"];
	        this.entryPrice = source["entryPrice"];
	        this.currentPrice = source["currentPrice"];
	        this.unrealizedPl = source["unrealizedPl"];
	        this.strategy = source["strategy"];
	        this.openTime = source["openTime"];
	    }
	}
	export class SystemHealthMetrics {
	    avgOrderLatencyMs: number;
	    apiErrorCount: number;
	    // Go type: time
	    lastDataSync: any;

	    static createFrom(source: any = {}) {
	        return new SystemHealthMetrics(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.avgOrderLatencyMs = source["avgOrderLatencyMs"];
	        this.apiErrorCount = source["apiErrorCount"];
	        this.lastDataSync = this.convertValues(source["lastDataSync"], null);
	    }

		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}
	export class TradeStatsToday {
	    executedCount: number;
	    winCount: number;
	    lossCount: number;
	    winRate: number;
	    avgWinAmount: number;
	    avgLossAmount: number;

	    static createFrom(source: any = {}) {
	        return new TradeStatsToday(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.executedCount = source["executedCount"];
	        this.winCount = source["winCount"];
	        this.lossCount = source["lossCount"];
	        this.winRate = source["winRate"];
	        this.avgWinAmount = source["avgWinAmount"];
	        this.avgLossAmount = source["avgLossAmount"];
	    }
	}
	export class PortfolioMetrics {
	    // Go type: time
	    timestamp: any;
	    equity: number;
	    realizedPnlToday: number;
	    unrealizedPnl: number;
	    openPositionsCount: number;
	    buyingPower: number;

	    static createFrom(source: any = {}) {
	        return new PortfolioMetrics(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.timestamp = this.convertValues(source["timestamp"], null);
	        this.equity = source["equity"];
	        this.realizedPnlToday = source["realizedPnlToday"];
	        this.unrealizedPnl = source["unrealizedPnl"];
	        this.openPositionsCount = source["openPositionsCount"];
	        this.buyingPower = source["buyingPower"];
	    }

		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}
	export class AllMetrics {
	    portfolio: PortfolioMetrics;
	    trades: TradeStatsToday;
	    system: SystemHealthMetrics;
	    openPositions: Position[];

	    static createFrom(source: any = {}) {
	        return new AllMetrics(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.portfolio = this.convertValues(source["portfolio"], PortfolioMetrics);
	        this.trades = this.convertValues(source["trades"], TradeStatsToday);
	        this.system = this.convertValues(source["system"], SystemHealthMetrics);
	        this.openPositions = this.convertValues(source["openPositions"], Position);
	    }

		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}




}

export namespace struct { Connected bool "json:\"connected\""; LastConnected time {

	export class  {
	    connected: boolean;
	    // Go type: time
	    lastConnected?: any;
	    error?: string;

	    static createFrom(source: any = {}) {
	        return new (source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.connected = source["connected"];
	        this.lastConnected = this.convertValues(source["lastConnected"], null);
	        this.error = source["error"];
	    }

		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}

}

export namespace struct { Enabled bool "toml:\"enabled\" json:\"Enabled\" jsonschema:\"description=Enable the alerting system,default=true\""; Thresholds struct { MaxOrderLatencyMs float64 "toml:\"max_order_latency_ms\" json:\"MaxOrderLatencyMs\" jsonschema:\"description=Maximum acceptable order latency in milliseconds,minimum=0,default=1000\""; MinDailyRealizedPnl float64 "toml:\"min_daily_realized_pnl\" json:\"MinDailyRealizedPnl\" jsonschema:\"description=Minimum acceptable daily realized P&L,default=-500 {

	export class  {
	    Enabled: boolean;
	    Thresholds: struct { MaxOrderLatencyMs float64 "toml:\"max_order_latency_ms\" json:\"MaxOrderLatencyMs\" jsonschema:\"description=Maximum acceptable order latency in milliseconds,minimum=0,default=1000\""; MinDailyRealizedPnl float64 "toml:\"min_daily_realized_pnl\" json:\"MinDailyRealizedPnl\" jsonschema:\"description=Minimum acceptable daily realized P&L,default=-500.;
	    // Go type: struct { Email struct { Enabled bool "toml:\"enabled\" json:\"Enabled\" jsonschema:\"description=Enable email notifications,default=false\""; Recipients []string "toml:\"recipients\" json:\"Recipients\" jsonschema:\"description=List of email recipients\""; SmtpHost string "toml:\"smtp_host\" json:\"SmtpHost\" jsonschema:\"description=SMTP server hostname\""; SmtpPort int "toml:\"smtp_port\" json:\"SmtpPort\" jsonschema:\"description=SMTP server port,minimum=1,maximum=65535,default=587\""; SmtpUser string "toml:\"smtp_user\" json:\"SmtpUser\" jsonschema:\"description=SMTP server username\""; SmtpPass string "toml:\"smtp_pass\" json:\"SmtpPass\" jsonschema:\"description=SMTP server password (or environment variable name)\"" } "toml:\"email\" json:\"Email\""; Slack struct { Enabled bool "toml:\"enabled\" json:\"Enabled\" jsonschema:\"description=Enable Slack notifications,default=false\""; WebhookUrl string "toml:\"webhook_url\" json:\"WebhookUrl\" jsonschema:\"description=Slack webhook URL (or environment variable name)\"" } "toml:\"slack\" json:\"Slack\"" }
	    Notifications: any;

	    static createFrom(source: any = {}) {
	        return new (source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Enabled = source["Enabled"];
	        this.Thresholds = this.convertValues(source["Thresholds"], Object);
	        this.Notifications = this.convertValues(source["Notifications"], Object);
	    }

		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}

}

export namespace struct { GlobalMaxConcurrentPositions int "toml:\"global_max_concurrent_positions\" json:\"GlobalMaxConcurrentPositions\" jsonschema:\"description=Maximum number of concurrent positions,minimum=1,default=10\""; DefaultRiskPerTradePercentage float64 "toml:\"default_risk_per_trade_percentage\" json:\"DefaultRiskPerTradePercentage\" jsonschema:\"description=Percentage of account to risk per trade,minimum=0 {

	export class  {
	    GlobalMaxConcurrentPositions: number;
	    DefaultRiskPerTradePercentage: number;
	    EmergencyStopLossPercentage: number;

	    static createFrom(source: any = {}) {
	        return new (source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.GlobalMaxConcurrentPositions = source["GlobalMaxConcurrentPositions"];
	        this.DefaultRiskPerTradePercentage = source["DefaultRiskPerTradePercentage"];
	        this.EmergencyStopLossPercentage = source["EmergencyStopLossPercentage"];
	    }
	}

}

export namespace struct { MaxOrderLatencyMs float64 "toml:\"max_order_latency_ms\" json:\"MaxOrderLatencyMs\" jsonschema:\"description=Maximum acceptable order latency in milliseconds,minimum=0,default=1000\""; MinDailyRealizedPnl float64 "toml:\"min_daily_realized_pnl\" json:\"MinDailyRealizedPnl\" jsonschema:\"description=Minimum acceptable daily realized P&L,default=-500 {

	export class  {
	    MaxOrderLatencyMs: number;
	    MinDailyRealizedPnl: number;
	    MaxPortfolioDrawdownPercentageToday: number;
	    MaxApiErrorsPerHour: number;

	    static createFrom(source: any = {}) {
	        return new (source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.MaxOrderLatencyMs = source["MaxOrderLatencyMs"];
	        this.MinDailyRealizedPnl = source["MinDailyRealizedPnl"];
	        this.MaxPortfolioDrawdownPercentageToday = source["MaxPortfolioDrawdownPercentageToday"];
	        this.MaxApiErrorsPerHour = source["MaxApiErrorsPerHour"];
	    }
	}

}

export namespace struct { MinOpenInterest int "toml:\"min_open_interest\" json:\"MinOpenInterest\" jsonschema:\"description=Minimum open interest for an option contract,minimum=0,default=500\""; MaxBidAskSpreadPercentage float64 "toml:\"max_bid_ask_spread_percentage\" json:\"MaxBidAskSpreadPercentage\" jsonschema:\"description=Maximum bid-ask spread as a percentage of mark price,minimum=0 {

	export class  {
	    MinOpenInterest: number;
	    MaxBidAskSpreadPercentage: number;
	    UseIVRankFilter: boolean;
	    MinIVRank: number;
	    MaxIVRank: number;
	    UseIVSkewFilter: boolean;
	    MinPutCallIVSkewPercentage: number;
	    MaxPutCallIVSkewPercentage: number;
	    UsePOPFilter: boolean;
	    MinProbabilityOfProfitPercentage: number;
	    UseWidthVsExpectedMoveFilter: boolean;
	    MaxSpreadWidthVsExpectedMovePercentage: number;

	    static createFrom(source: any = {}) {
	        return new (source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.MinOpenInterest = source["MinOpenInterest"];
	        this.MaxBidAskSpreadPercentage = source["MaxBidAskSpreadPercentage"];
	        this.UseIVRankFilter = source["UseIVRankFilter"];
	        this.MinIVRank = source["MinIVRank"];
	        this.MaxIVRank = source["MaxIVRank"];
	        this.UseIVSkewFilter = source["UseIVSkewFilter"];
	        this.MinPutCallIVSkewPercentage = source["MinPutCallIVSkewPercentage"];
	        this.MaxPutCallIVSkewPercentage = source["MaxPutCallIVSkewPercentage"];
	        this.UsePOPFilter = source["UsePOPFilter"];
	        this.MinProbabilityOfProfitPercentage = source["MinProbabilityOfProfitPercentage"];
	        this.UseWidthVsExpectedMoveFilter = source["UseWidthVsExpectedMoveFilter"];
	        this.MaxSpreadWidthVsExpectedMovePercentage = source["MaxSpreadWidthVsExpectedMovePercentage"];
	    }
	}

}

export namespace struct { Name string "json:\"name\""; Running bool "json:\"running\""; Health string "json:\"health\""; LastChecked time {

	export class  {
	    name: string;
	    running: boolean;
	    health: string;
	    // Go type: time
	    lastChecked: any;
	    message?: string;

	    static createFrom(source: any = {}) {
	        return new (source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.name = source["name"];
	        this.running = source["running"];
	        this.health = source["health"];
	        this.lastChecked = this.convertValues(source["lastChecked"], null);
	        this.message = source["message"];
	    }

		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}

}

export namespace struct { UseDynamicDTE bool "toml:\"use_dynamic_dte\" json:\"UseDynamicDTE\" jsonschema:\"description=Whether to use dynamic DTE calculation,default=true\""; TargetDTEMode string "toml:\"target_dte_mode\" json:\"TargetDTEMode\" jsonschema:\"description=Mode for calculating target DTE,enum=FIXED,enum=ATR_MULTIPLE,enum=VOLATILITY_INDEX,default=ATR_MULTIPLE\""; DTEAtrPeriod int "toml:\"dte_atr_period\" json:\"DTEAtrPeriod\" jsonschema:\"description=ATR period for DTE calculation,minimum=1,maximum=100,default=14\""; DTEAtrCoefficient float64 "toml:\"dte_atr_coefficient\" json:\"DTEAtrCoefficient\" jsonschema:\"description=Coefficient to multiply ATR by for DTE calculation,minimum=0 {

	export class  {
	    UseDynamicDTE: boolean;
	    TargetDTEMode: string;
	    DTEAtrPeriod: number;
	    DTEAtrCoefficient: number;
	    FixedTargetDTE: number;
	    MinDTE: number;
	    MaxDTE: number;
	    AvoidEarningsDaysBefore: number;
	    AvoidEarningsDaysAfter: number;
	    AvoidExDividendDaysBefore: number;

	    static createFrom(source: any = {}) {
	        return new (source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.UseDynamicDTE = source["UseDynamicDTE"];
	        this.TargetDTEMode = source["TargetDTEMode"];
	        this.DTEAtrPeriod = source["DTEAtrPeriod"];
	        this.DTEAtrCoefficient = source["DTEAtrCoefficient"];
	        this.FixedTargetDTE = source["FixedTargetDTE"];
	        this.MinDTE = source["MinDTE"];
	        this.MaxDTE = source["MaxDTE"];
	        this.AvoidEarningsDaysBefore = source["AvoidEarningsDaysBefore"];
	        this.AvoidEarningsDaysAfter = source["AvoidEarningsDaysAfter"];
	        this.AvoidExDividendDaysBefore = source["AvoidExDividendDaysBefore"];
	    }
	}

}

export namespace struct { UseGreekLimits bool "toml:\"use_greek_limits\" json:\"UseGreekLimits\" jsonschema:\"description=Whether to apply Greek limits to positions,default=true\""; MaxAbsPositionDelta float64 "toml:\"max_abs_position_delta\" json:\"MaxAbsPositionDelta\" jsonschema:\"description=Maximum absolute delta exposure per position,minimum=0 {

	export class  {
	    UseGreekLimits: boolean;
	    MaxAbsPositionDelta: number;
	    MaxAbsPositionGamma: number;
	    MaxAbsPositionVega: number;
	    MinPositionTheta: number;

	    static createFrom(source: any = {}) {
	        return new (source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.UseGreekLimits = source["UseGreekLimits"];
	        this.MaxAbsPositionDelta = source["MaxAbsPositionDelta"];
	        this.MaxAbsPositionGamma = source["MaxAbsPositionGamma"];
	        this.MaxAbsPositionVega = source["MaxAbsPositionVega"];
	        this.MinPositionTheta = source["MinPositionTheta"];
	    }
	}

}
