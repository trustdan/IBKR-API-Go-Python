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
	export class OptionsConfig {
	    MinOpenInterest: number;
	    MaxBidAskSpreadPct: number;
	    PreferredExpirationDays: number[];
	    StrikePriceIncrement: number;

	    static createFrom(source: any = {}) {
	        return new OptionsConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.MinOpenInterest = source["MinOpenInterest"];
	        this.MaxBidAskSpreadPct = source["MaxBidAskSpreadPct"];
	        this.PreferredExpirationDays = source["PreferredExpirationDays"];
	        this.StrikePriceIncrement = source["StrikePriceIncrement"];
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
