export namespace main {

	export class BearRallyConfig {
	    RSIThreshold: number;

	    static createFrom(source: any = {}) {
	        return new BearRallyConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.RSIThreshold = source["RSIThreshold"];
	    }
	}
	export class BullPullbackConfig {
	    RSIThreshold: number;

	    static createFrom(source: any = {}) {
	        return new BullPullbackConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.RSIThreshold = source["RSIThreshold"];
	    }
	}
	export class LoggingConfig {
	    Level: string;
	    File: string;
	    MaxSizeMB: number;
	    BackupCount: number;
	    Format: string;

	    static createFrom(source: any = {}) {
	        return new LoggingConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Level = source["Level"];
	        this.File = source["File"];
	        this.MaxSizeMB = source["MaxSizeMB"];
	        this.BackupCount = source["BackupCount"];
	        this.Format = source["Format"];
	    }
	}
	export class ScannerConfig {
	    Host: string;
	    Port: number;
	    MaxConcurrency: number;

	    static createFrom(source: any = {}) {
	        return new ScannerConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Host = source["Host"];
	        this.Port = source["Port"];
	        this.MaxConcurrency = source["MaxConcurrency"];
	    }
	}
	export class UniverseConfig {
	    MinMarketCap: number;
	    MinPrice: number;
	    MinVolume: number;

	    static createFrom(source: any = {}) {
	        return new UniverseConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.MinMarketCap = source["MinMarketCap"];
	        this.MinPrice = source["MinPrice"];
	        this.MinVolume = source["MinVolume"];
	    }
	}
	export class OptionsConfig {
	    MinDTE: number;
	    MaxDTE: number;
	    MinDelta: number;
	    MaxDelta: number;
	    MaxSpreadCost: number;
	    MinRewardRisk: number;

	    static createFrom(source: any = {}) {
	        return new OptionsConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.MinDTE = source["MinDTE"];
	        this.MaxDTE = source["MaxDTE"];
	        this.MinDelta = source["MinDelta"];
	        this.MaxDelta = source["MaxDelta"];
	        this.MaxSpreadCost = source["MaxSpreadCost"];
	        this.MinRewardRisk = source["MinRewardRisk"];
	    }
	}
	export class LowBaseConfig {
	    MinATRRatio: number;
	    MaxRSI: number;

	    static createFrom(source: any = {}) {
	        return new LowBaseConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.MinATRRatio = source["MinATRRatio"];
	        this.MaxRSI = source["MaxRSI"];
	    }
	}
	export class HighBaseConfig {
	    MaxATRRatio: number;
	    MinRSI: number;

	    static createFrom(source: any = {}) {
	        return new HighBaseConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.MaxATRRatio = source["MaxATRRatio"];
	        this.MinRSI = source["MinRSI"];
	    }
	}
	export class StrategyConfig {
	    HighBase: HighBaseConfig;
	    LowBase: LowBaseConfig;
	    BullPullback: BullPullbackConfig;
	    BearRally: BearRallyConfig;

	    static createFrom(source: any = {}) {
	        return new StrategyConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.HighBase = this.convertValues(source["HighBase"], HighBaseConfig);
	        this.LowBase = this.convertValues(source["LowBase"], LowBaseConfig);
	        this.BullPullback = this.convertValues(source["BullPullback"], BullPullbackConfig);
	        this.BearRally = this.convertValues(source["BearRally"], BearRallyConfig);
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
	export class TradingConfig {
	    Mode: string;
	    MaxPositions: number;
	    MaxDailyTrades: number;
	    RiskPerTrade: number;
	    PriceImprovementFactor: number;
	    AllowLateDayEntry: boolean;

	    static createFrom(source: any = {}) {
	        return new TradingConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Mode = source["Mode"];
	        this.MaxPositions = source["MaxPositions"];
	        this.MaxDailyTrades = source["MaxDailyTrades"];
	        this.RiskPerTrade = source["RiskPerTrade"];
	        this.PriceImprovementFactor = source["PriceImprovementFactor"];
	        this.AllowLateDayEntry = source["AllowLateDayEntry"];
	    }
	}
	export class DataConfig {
	    CacheDir: string;
	    UniverseCacheExpiry: number;
	    MinuteDataCacheExpiry: number;
	    OptionsCacheExpiry: number;

	    static createFrom(source: any = {}) {
	        return new DataConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.CacheDir = source["CacheDir"];
	        this.UniverseCacheExpiry = source["UniverseCacheExpiry"];
	        this.MinuteDataCacheExpiry = source["MinuteDataCacheExpiry"];
	        this.OptionsCacheExpiry = source["OptionsCacheExpiry"];
	    }
	}
	export class IBKRConfig {
	    Host: string;
	    Port: number;
	    ClientID: number;
	    ReadOnly: boolean;
	    Account: string;

	    static createFrom(source: any = {}) {
	        return new IBKRConfig(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Host = source["Host"];
	        this.Port = source["Port"];
	        this.ClientID = source["ClientID"];
	        this.ReadOnly = source["ReadOnly"];
	        this.Account = source["Account"];
	    }
	}
	export class Config {
	    IBKR: IBKRConfig;
	    Data: DataConfig;
	    Trading: TradingConfig;
	    Strategy: StrategyConfig;
	    Options: OptionsConfig;
	    Universe: UniverseConfig;
	    Scanner: ScannerConfig;
	    Logging: LoggingConfig;

	    static createFrom(source: any = {}) {
	        return new Config(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.IBKR = this.convertValues(source["IBKR"], IBKRConfig);
	        this.Data = this.convertValues(source["Data"], DataConfig);
	        this.Trading = this.convertValues(source["Trading"], TradingConfig);
	        this.Strategy = this.convertValues(source["Strategy"], StrategyConfig);
	        this.Options = this.convertValues(source["Options"], OptionsConfig);
	        this.Universe = this.convertValues(source["Universe"], UniverseConfig);
	        this.Scanner = this.convertValues(source["Scanner"], ScannerConfig);
	        this.Logging = this.convertValues(source["Logging"], LoggingConfig);
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
	export class ContainerInfo {
	    ID: string;
	    Name: string;
	    Status: string;
	    Created: string;

	    static createFrom(source: any = {}) {
	        return new ContainerInfo(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.ID = source["ID"];
	        this.Name = source["Name"];
	        this.Status = source["Status"];
	        this.Created = source["Created"];
	    }
	}

	export class ServiceStatus {
	    name: string;
	    status: string;
	    isOk: boolean;
	    message: string;
	    extraMsg?: string;

	    static createFrom(source: any = {}) {
	        return new ServiceStatus(source);
	    }

	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.name = source["name"];
	        this.status = source["status"];
	        this.isOk = source["isOk"];
	        this.message = source["message"];
	        this.extraMsg = source["extraMsg"];
	    }
	}
}
