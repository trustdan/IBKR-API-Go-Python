**Creating a roadmap with Gherkin syntax**

The user wants a phased implementation roadmap, incorporating key tasks and deliverables over about four weeks. The roadmap will include phases like prerequisites and feature builds, such as UI tab implementation, scheduling, and others. Key workflows, such as connection test, cache clearing, and live monitoring will be highlighted with Gherkin syntax scenarios. I'll tailor it to the specific requirements and reference relevant documents, ensuring the plan aligns with the models.ts file and other details provided.


Thought for 24 seconds


Here’s a **6-week implementation roadmap**, broken into clear phases, with key deliverables and representative Cucumber/Gherkin scenarios to guide your test-driven development.

---

## Phase 0 — Prerequisites & Foundations (Week 1)

**Goals**

* Centralize *all* tunable parameters into a single `config.toml`
* Add live-reload handlers in both services (Python & Go)
* Verify existing pause/edit/unpause flow still works end-to-end

**Tasks**

1. **Config consolidation**

   * Pull every parameter out of code and into `config.toml`
   * Update `models.ts` → `Config` schema matches&#x20;
2. **Signal handlers**

   * Python: `signal.signal(SIGUSR1, reload_cfg)` to re-load TOML in memory&#x20;
   * Go: `fsnotify` watcher on `/config/config.toml` to hot-swap config&#x20;
3. **Smoke test**

   * Pause → edit a simple field → unpause → observe “Config reloaded” in logs (see README.md)&#x20;

```gherkin
Feature: Config Reload Foundations
  Scenario: Live reload on SIGUSR1 in Python
    Given python-orchestrator is running
    When I send SIGUSR1 to its container
    Then the orchestrator logs "Config reloaded"
```

---

## Phase 1 — Wails Backend & API Contract (Week 2)

**Goals**

* Scaffold the Wails service
* Define backend methods for container control and config I/O

**Tasks**

1. **Init Wails project**

   ```bash
   wails init -n TraderAdmin -t svelte-ts
   go get github.com/docker/docker/client@v25
   go get github.com/BurntSushi/toml
   ```
2. **Backend API surface**

   ```go
   func (a *API) LoadConfig() (Config, error)
   func (a *API) SaveConfig(cfg Config) error
   func (a *API) PauseStack() error
   func (a *API) UnpauseStack() error
   func (a *API) StackState() ([]ContainerInfo, error)
   ```
3. **Docker SDK integration**

   * Pause/unpause targets `["python-orchestrator","go-scanner"]`
   * On unpause, also send `SIGUSR1`&#x20;

```gherkin
Feature: Pause/Unpause API
  Scenario: Pause then unpause containers
    Given python-orchestrator and go-scanner are running
    When the GUI calls PauseStack
    Then both containers should be paused
    When the GUI calls UnpauseStack
    Then both containers resume and receive SIGUSR1
```

---

## Phase 2 — Config Model & Form Generation (Week 2–3)

**Goals**

* Mirror every field in `models.ts` as JSON Schema for auto-generated forms&#x20;
* Enable real-time validation on the front end

**Tasks**

1. **Generate JSON Schema**

   ```go
   schema := jsonschema.Reflect(&main.Config{}) // from models.ts
   ```
2. **Form generation**

   * Use Svelte to loop over schema properties
   * Render sliders, toggles, numeric inputs based on type/format

```gherkin
Feature: Config Form Validation
  Scenario: Reject invalid RSI threshold
    Given the RSIThreshold field is of type number
    When I enter "-5" into BullPullback.RSIThreshold
    Then the form shows "Value must be ≥ 0"
```

---

## Phase 3 — Configuration Tabs & UI Layout (Week 3–4)

**Goals**

* Build out the **tabs** and input controls for each settings category

| Tab             | Contents                                       |
| --------------- | ---------------------------------------------- |
| IBKR Connection | Host, Port, ClientID, Read-only toggle, Test   |
| Data Management | Cache directory, expiry sliders, Clear cache   |
| Trading & Risk  | Mode toggle, MaxPositions, RiskPerTrade, etc.  |
| Strategies      | High Base, Low Base, Bull Pullback, Bear Rally |
| Options         | DTE range, Delta range, Spread cost, R\:R      |
| Universe        | MinMarketCap, MinPrice, MinVolume              |
| Scanner         | Host/Port, MaxConcurrency, Scan now button     |
| Logging         | Level, Path, MaxSize, Backup count, Format     |
| Schedule        | Auto-start/stop times, manual Start/Stop       |
| Monitoring      | Container status, TWS connection, metrics      |
| Alerts          | Email/SMS/Webhook configuration                |
| Backup/Restore  | Manual backup, auto-backup schedule            |
| Help            | Quick links, FAQs                              |

**Tasks**

1. **Tab scaffolding** in Svelte
2. **Inputs** bound to form state
3. **Container status panel** via `StackState()` API

```gherkin
Feature: Tab Navigation
  Scenario: Navigate to Strategies tab
    Given the GUI is open
    When I click on "Strategies"
    Then I see four collapsible strategy panels
```

---

## Phase 4 — Save & Restart Workflow (Week 4)

**Goals**

* Wire the **Save & Restart** button to Pause → SaveConfig → Unpause

**Tasks**

1. **Button logic** in Svelte

   ```ts
   async function saveAndRestart(cfg) {
     await api.PauseStack()
     await api.SaveConfig(cfg)
     await api.UnpauseStack()
   }
   ```
2. **Loading/error states** and toast notifications

```gherkin
Feature: Save and Restart
  Scenario: Successful config apply
    Given valid config in all tabs
    When I click "Save & Restart"
    Then containers pause
    And config.toml is updated
    And containers unpause
    And UI shows "Configuration applied"
```

---

## Phase 5 — Scheduling & Manual Control (Week 5)

**Goals**

* Implement **time-of-day scheduler** and manual Start/Stop

**Tasks**

1. **Scheduler UI**

   * Two time pickers: “Start at” & “Stop at”
   * Cron expression → store in config
2. **Backend runner**

   * Light scheduler thread in Python orchestrator to pause/resume trading logic
3. **Manual overrides**

```gherkin
Feature: Trading Schedule
  Scenario: Auto-stop at market close
    Given StopAt = "16:00"
    When current time is "16:00"
    Then trading activities pause automatically
```

---

## Phase 6 — Monitoring, Alerts & Backtesting (Week 6)

**Goals**

* Real-time performance dashboard, backtest triggers, and alert management

**Tasks**

1. **Metrics panel**: equity curve, P\&L, win rate charts
2. **Quick backtest** button that calls Python backtester API and streams results
3. **Alert config**: enable/disable per-event alerts

```gherkin
Feature: Quick Backtest
  Scenario: Run backtest for AAPL
    Given symbols = ["AAPL"]
    When I click "Run Backtest"
    Then the UI shows progress
    And a results table appears when done
```

---

### Next Steps & CI/CD

* **E2E tests**: spin up a Kind cluster in GitHub Actions and run these scenarios
* **Documentation**: update USAGE\_GUIDE.md with screenshots & workflows
* **Rollout**: deliver to alpha users for feedback

This roadmap ensures a **test-driven**, **incremental** build of your fully featured TraderAdmin GUI—tying every major feature back to concrete Gherkin scenarios.
