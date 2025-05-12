export namespace main {

	export class AlertsConfig {
	    EnableEmail: boolean;
	    EmailTo: string;
	    EnableSlack: boolean;
	    SlackWebhookURL: string;
	    AlertOnErrors: boolean;
	    AlertOnTrades: boolean;

	    static createFrom(source: any = {}) {
	        return new AlertsConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.EnableEmail = source["EnableEmail"];
	        this.EmailTo = source["EmailTo"];
	        this.EnableSlack = source["EnableSlack"];
	        this.SlackWebhookURL = source["SlackWebhookURL"];
	        this.AlertOnErrors = source["AlertOnErrors"];
	        this.AlertOnTrades = source["AlertOnTrades"];
	    }
	}
	export class BackupConfig {
	    AutoBackup: boolean;
	    BackupIntervalHours: number;
	    BackupDir: string;
	    KeepBackups: number;

	    static createFrom(source: any = {}) {
	        return new BackupConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.AutoBackup = source["AutoBackup"];
	        this.BackupIntervalHours = source["BackupIntervalHours"];
	        this.BackupDir = source["BackupDir"];
	        this.KeepBackups = source["KeepBackups"];
	    }
	}
	export class KubernetesConfig {
	    Namespace: string;
	    ConfigMapName: string;
	    OrchestratorDeployment: string;
	    ScannerDeployment: string;

	    static createFrom(source: any = {}) {
	        return new KubernetesConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Namespace = source["Namespace"];
	        this.ConfigMapName = source["ConfigMapName"];
	        this.OrchestratorDeployment = source["OrchestratorDeployment"];
	        this.ScannerDeployment = source["ScannerDeployment"];
	    }
	}
	export class MonitoringConfig {
	    PrometheusPort: number;
	    MetricsIntervalSeconds: number;
	    HealthCheckURL: string;

	    static createFrom(source: any = {}) {
	        return new MonitoringConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.PrometheusPort = source["PrometheusPort"];
	        this.MetricsIntervalSeconds = source["MetricsIntervalSeconds"];
	        this.HealthCheckURL = source["HealthCheckURL"];
	    }
	}
	export class SchedulingConfig {
	    TradingStartTime: string;
	    TradingEndTime: string;
	    Timezone: string;
	    TradingDays: string[];
	    MaintenanceWindow: string;

	    static createFrom(source: any = {}) {
	        return new SchedulingConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.TradingStartTime = source["TradingStartTime"];
	        this.TradingEndTime = source["TradingEndTime"];
	        this.Timezone = source["Timezone"];
	        this.TradingDays = source["TradingDays"];
	        this.MaintenanceWindow = source["MaintenanceWindow"];
	    }
	}
	export class LoggingConfig {
	    Level: string;
	    File: string;
	    MaxSizeMB: number;
	    MaxBackups: number;
	    MaxAgeDays: number;

	    static createFrom(source: any = {}) {
	        return new LoggingConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Level = source["Level"];
	        this.File = source["File"];
	        this.MaxSizeMB = source["MaxSizeMB"];
	        this.MaxBackups = source["MaxBackups"];
	        this.MaxAgeDays = source["MaxAgeDays"];
	    }
	}
	export class DataManagementConfig {
	    CacheDir: string;
	    DataRetentionDays: number;
	    EnableDailyCleanup: boolean;

	    static createFrom(source: any = {}) {
	        return new DataManagementConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.CacheDir = source["CacheDir"];
	        this.DataRetentionDays = source["DataRetentionDays"];
	        this.EnableDailyCleanup = source["EnableDailyCleanup"];
	    }
	}
	export class ScannerConfig {
	    ScanIntervalSeconds: number;
	    LookbackDays: number;
	    MinVolume: number;
	    UsePremarketData: boolean;

	    static createFrom(source: any = {}) {
	        return new ScannerConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.ScanIntervalSeconds = source["ScanIntervalSeconds"];
	        this.LookbackDays = source["LookbackDays"];
	        this.MinVolume = source["MinVolume"];
	        this.UsePremarketData = source["UsePremarketData"];
	    }
	}
	export class UniverseConfig {
	    Symbols: string[];
	    MinMarketCap: number;
	    MaxVolatility: number;
	    Sectors: string[];

	    static createFrom(source: any = {}) {
	        return new UniverseConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Symbols = source["Symbols"];
	        this.MinMarketCap = source["MinMarketCap"];
	        this.MaxVolatility = source["MaxVolatility"];
	        this.Sectors = source["Sectors"];
	    }
	}
	export class DTEConfig {
	    Dynamic: boolean;
	    DTECoefficient: number;

	    static createFrom(source: any = {}) {
	        return new DTEConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Dynamic = source["Dynamic"];
	        this.DTECoefficient = source["DTECoefficient"];
	    }
	}
	export class EventsConfig {
	    SkipEarningsDays: number;
	    SkipExDivDays: number;

	    static createFrom(source: any = {}) {
	        return new EventsConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.SkipEarningsDays = source["SkipEarningsDays"];
	        this.SkipExDivDays = source["SkipExDivDays"];
	    }
	}
	export class ProbabilityConfig {
	    MinPOP: number;
	    MaxWidthVsMovePct: number;

	    static createFrom(source: any = {}) {
	        return new ProbabilityConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.MinPOP = source["MinPOP"];
	        this.MaxWidthVsMovePct = source["MaxWidthVsMovePct"];
	    }
	}
	export class GreeksConfig {
	    MaxThetaPerDay: number;
	    MaxVegaExposure: number;
	    MaxGammaExposure: number;

	    static createFrom(source: any = {}) {
	        return new GreeksConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.MaxThetaPerDay = source["MaxThetaPerDay"];
	        this.MaxVegaExposure = source["MaxVegaExposure"];
	        this.MaxGammaExposure = source["MaxGammaExposure"];
	    }
	}
	export class OptionsConfig {
	    MinOpenInterest: number;
	    MaxBidAskSpreadPct: number;
	    PreferredExpirationDays: number[];
	    StrikePriceIncrement: number;
	    MinIVRank: number;
	    MaxIVRank: number;
	    MinCallPutSkewPct: number;

	    static createFrom(source: any = {}) {
	        return new OptionsConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.MinOpenInterest = source["MinOpenInterest"];
	        this.MaxBidAskSpreadPct = source["MaxBidAskSpreadPct"];
	        this.PreferredExpirationDays = source["PreferredExpirationDays"];
	        this.StrikePriceIncrement = source["StrikePriceIncrement"];
	        this.MinIVRank = source["MinIVRank"];
	        this.MaxIVRank = source["MaxIVRank"];
	        this.MinCallPutSkewPct = source["MinCallPutSkewPct"];
	    }
	}
	export class StrategyConfig {
	    Active: boolean;
	    MinRSI: number;
	    MaxATRRatio: number;
	    MinIVRank: number;
	    MaxDelta: number;
	    MinDaysToExpiry: number;
	    MaxDaysToExpiry: number;
	    TargetProfitPct: number;
	    StopLossPct: number;

	    static createFrom(source: any = {}) {
	        return new StrategyConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Active = source["Active"];
	        this.MinRSI = source["MinRSI"];
	        this.MaxATRRatio = source["MaxATRRatio"];
	        this.MinIVRank = source["MinIVRank"];
	        this.MaxDelta = source["MaxDelta"];
	        this.MinDaysToExpiry = source["MinDaysToExpiry"];
	        this.MaxDaysToExpiry = source["MaxDaysToExpiry"];
	        this.TargetProfitPct = source["TargetProfitPct"];
	        this.StopLossPct = source["StopLossPct"];
	    }
	}
	export class TradingConfig {
	    Mode: string;
	    MaxPositions: number;
	    RiskPerTradePct: number;
	    MaxLossPct: number;

	    static createFrom(source: any = {}) {
	        return new TradingConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Mode = source["Mode"];
	        this.MaxPositions = source["MaxPositions"];
	        this.RiskPerTradePct = source["RiskPerTradePct"];
	        this.MaxLossPct = source["MaxLossPct"];
	    }
	}
	export class IBKRConfig {
	    Host: string;
	    Port: number;
	    ClientID: number;
	    ReadOnly: boolean;

	    static createFrom(source: any = {}) {
	        return new IBKRConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Host = source["Host"];
	        this.Port = source["Port"];
	        this.ClientID = source["ClientID"];
	        this.ReadOnly = source["ReadOnly"];
	    }
	}
	export class Config {
	    IBKR: IBKRConfig;
	    Trading: TradingConfig;
	    Strategies: Record<string, StrategyConfig>;
	    Options: OptionsConfig;
	    Greeks: GreeksConfig;
	    Probability: ProbabilityConfig;
	    Events: EventsConfig;
	    DTE: DTEConfig;
	    Universe: UniverseConfig;
	    Scanner: ScannerConfig;
	    DataManagement: DataManagementConfig;
	    Logging: LoggingConfig;
	    Scheduling: SchedulingConfig;
	    Monitoring: MonitoringConfig;
	    Alerts: AlertsConfig;
	    Backup: BackupConfig;
	    Kubernetes: KubernetesConfig;

	    static createFrom(source: any = {}) {
	        return new Config(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.IBKR = this.convertValues(source["IBKR"], IBKRConfig);
	        this.Trading = this.convertValues(source["Trading"], TradingConfig);
	        this.Strategies = this.convertValues(source["Strategies"], StrategyConfig, true);
	        this.Options = this.convertValues(source["Options"], OptionsConfig);
	        this.Greeks = this.convertValues(source["Greeks"], GreeksConfig);
	        this.Probability = this.convertValues(source["Probability"], ProbabilityConfig);
	        this.Events = this.convertValues(source["Events"], EventsConfig);
	        this.DTE = this.convertValues(source["DTE"], DTEConfig);
	        this.Universe = this.convertValues(source["Universe"], UniverseConfig);
	        this.Scanner = this.convertValues(source["Scanner"], ScannerConfig);
	        this.DataManagement = this.convertValues(source["DataManagement"], DataManagementConfig);
	        this.Logging = this.convertValues(source["Logging"], LoggingConfig);
	        this.Scheduling = this.convertValues(source["Scheduling"], SchedulingConfig);
	        this.Monitoring = this.convertValues(source["Monitoring"], MonitoringConfig);
	        this.Alerts = this.convertValues(source["Alerts"], AlertsConfig);
	        this.Backup = this.convertValues(source["Backup"], BackupConfig);
	        this.Kubernetes = this.convertValues(source["Kubernetes"], KubernetesConfig);
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
	export class ContainerStatusInfo {
	    name: string;
	    state: string;

	    static createFrom(source: any = {}) {
	        return new ContainerStatusInfo(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.name = source["name"];
	        this.state = source["state"];
	    }
	}







	export class PositionInfo {
	    symbol: string;
	    quantity: number;
	    entryPrice: number;
	    currentPrice: number;
	    pnl: number;
	    strategy: string;

	    static createFrom(source: any = {}) {
	        return new PositionInfo(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.symbol = source["symbol"];
	        this.quantity = source["quantity"];
	        this.entryPrice = source["entryPrice"];
	        this.currentPrice = source["currentPrice"];
	        this.pnl = source["pnl"];
	        this.strategy = source["strategy"];
	    }
	}
	export class TradeMetrics {
	    timestamp: number;
	    equity: number;
	    dailyPnL: number;
	    tradesExecuted: number;
	    winCount: number;
	    lossCount: number;
	    maxLatencyMs: number;
	    avgLatencyMs: number;
	    errorCount: number;
	    errorsByType: string[];

	    static createFrom(source: any = {}) {
	        return new TradeMetrics(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.timestamp = source["timestamp"];
	        this.equity = source["equity"];
	        this.dailyPnL = source["dailyPnL"];
	        this.tradesExecuted = source["tradesExecuted"];
	        this.winCount = source["winCount"];
	        this.lossCount = source["lossCount"];
	        this.maxLatencyMs = source["maxLatencyMs"];
	        this.avgLatencyMs = source["avgLatencyMs"];
	        this.errorCount = source["errorCount"];
	        this.errorsByType = source["errorsByType"];
	    }
	}
	export class MetricsPayload {
	    metrics: TradeMetrics;
	    positions: PositionInfo[];
	    timePoints: number[];
	    equityPoints: number[];

	    static createFrom(source: any = {}) {
	        return new MetricsPayload(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.metrics = this.convertValues(source["metrics"], TradeMetrics);
	        this.positions = this.convertValues(source["positions"], PositionInfo);
	        this.timePoints = source["timePoints"];
	        this.equityPoints = source["equityPoints"];
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

	export class OptionContract {
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

	    static createFrom(source: any = {}) {
	        return new OptionContract(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.expiry = source["expiry"];
	        this.strike = source["strike"];
	        this.type = source["type"];
	        this.bid = source["bid"];
	        this.ask = source["ask"];
	        this.iv = source["iv"];
	        this.ivRank = source["ivRank"];
	        this.delta = source["delta"];
	        this.gamma = source["gamma"];
	        this.theta = source["theta"];
	        this.vega = source["vega"];
	        this.openInterest = source["openInterest"];
	        this.volume = source["volume"];
	        this.bidAskSpreadPct = source["bidAskSpreadPct"];
	        this.probabilityOTM = source["probabilityOTM"];
	    }
	}





	export class StatusInfo {
	    ibkrConnected: boolean;
	    ibkrError?: string;
	    containers: ContainerStatusInfo[];

	    static createFrom(source: any = {}) {
	        return new StatusInfo(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.ibkrConnected = source["ibkrConnected"];
	        this.ibkrError = source["ibkrError"];
	        this.containers = this.convertValues(source["containers"], ContainerStatusInfo);
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
