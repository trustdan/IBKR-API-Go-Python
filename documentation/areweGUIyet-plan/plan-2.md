### Plan 2: Core GUI Components

**Timeline:** ~2 weeks
 **Objective:** Flesh out a polished, user-friendly desktop interface that lets traders view status, edit every setting, and interact with the backend seamlessly.

------

#### 2.1 UI Architecture & Scaffold

1. **Component Layout**

   ```
   src/
   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ App.svelte               # Main shell + tab selector
   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ components/
   Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ StatusBar.svelte     # Top-right connection & container status
   Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ NavTabs.svelte       # Side or top tab navigator
   Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ OverviewTab.svelte
   Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ConnectionTab.svelte
   Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ TradingRiskTab.svelte
   Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ StrategiesTab.svelte
   Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ OptionsTab.svelte
   Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ UniverseTab.svelte
   Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ScannerTab.svelte
   Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ DataTab.svelte
   Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ LoggingTab.svelte
   Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ ScheduleTab.svelte
   Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ AlertsTab.svelte
   Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ BackupTab.svelte
   Ã¢â€â€š   Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ DevToolsTab.svelte
   Ã¢â€â€š   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ HelpTab.svelte
   Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ store/
       Ã¢â€Å“Ã¢â€â‚¬Ã¢â€â‚¬ config.js           # Writable store for all settings
       Ã¢â€â€Ã¢â€â‚¬Ã¢â€â‚¬ status.js           # Real-time status flags
   ```

2. **Routing-less Tabs**

   - Maintain a Svelte store `activeTab` (string).
   - `NavTabs.svelte` emits clicks to change `activeTab`.
   - `App.svelte` renders `<OverviewTab />`Ã¢â‚¬Â¦ based on `activeTab`.

------

#### 2.2 Dynamic Form Generation

1. **Generate JSON Schema**
    In Go backend, reflect the `Config` struct to JSON Schema:

   ```go
   import "github.com/alecthomas/jsonschema"

   func BuildSchema() ([]byte, error) {
     reflector := jsonschema.Reflector{ExpandedStruct: true}
     schema := reflector.Reflect(&Config{})
     return json.MarshalIndent(schema, "", "  ")
   }
   ```

2. **Expose Schema via Wails**

   ```go
   func (a *API) GetConfigSchema() (string, error) {
     raw, _ := BuildSchema()
     return string(raw), nil
   }
   ```

3. **Form Renderer in Svelte**

   - On startup, load schema:

     ```ts
     import { writable } from 'svelte/store';
     export const schema = writable<any>(null);
     async function loadSchema() {
       const raw = await api.GetConfigSchema();
       schema.set(JSON.parse(raw));
     }
     loadSchema();
     ```

   - Create a `<DynamicForm {schema} bind:data />` component that:

     - Loops `Object.entries(schema.properties)`
     - Chooses input type (slider, checkbox, number) based on `type`, `minimum`, `maximum`, `enum`
     - Binds each field to `data[fieldName]`
     - Shows inline validation using `schema.required` and `schema.properties[field].minimum`/`maximum`

------

#### 2.3 Config Store & API Integration

1. **`config.js` Store**

   ```ts
   import { writable } from 'svelte/store';
   import { LoadConfig, SaveConfig } from '../../wailsjs/go/main/App';

   export const configStore = writable<Record<string, any>>(null);

   export async function loadConfig() {
     const cfg = await LoadConfig();
     configStore.set(cfg);
   }
   export async function saveConfig(newCfg) {
     await SaveConfig(newCfg);
     configStore.set(newCfg);
   }
   ```

2. **Lifecycle**

   - On app mount: `loadSchema()` Ã¢â€ â€™ `loadConfig()`
   - Pass `configStore` as `data` into each tabÃ¢â‚¬â„¢s form
   - Disable Ã¢â‚¬Å“SaveÃ¢â‚¬Â until `schema` & `configStore` both loaded

------

#### 2.4 Status Bar & Container Panel

1. **`status.js` Store**

   ```ts
   import { writable } from 'svelte/store';
   export const status = writable({
     ibkrConnected: false,
     containers: [] as { name: string; state: string }[],
   });

   // Poll every 5s:
   setInterval(async () => {
     const s = await api.GetStatus();
     status.set(s);
   }, 5000);
   ```

2. **`StatusBar.svelte`**

   - Shows IBKR icon (green/red) and tooltip with error
   - Lists container names with colored dots (Ã°Å¸Å¸Â¢ Running, Ã°Å¸Å¸Â¡ Paused, Ã°Å¸â€Â´ Stopped)

------

#### 2.5 Tab-Specific Enhancements

- **Connection Tab**
  - Fields: host, port, clientID, read-only toggle
  - Ã¢â‚¬Å“Test ConnectionÃ¢â‚¬Â button Ã¢â€ â€™ calls `api.TestConnection()` Ã¢â€ â€™ toast success/error
- **Trading & Risk Tab**
  - Inputs: mode toggle, max positions, risk % slider
  - Ã¢â‚¬Å“Quick BacktestÃ¢â‚¬Â button Ã¢â€ â€™ calls `api.RunQuickBacktest()` Ã¢â€ â€™ show chart/modal
- **Strategies Tab**
  - Four collapsible sections (High Base, Low Base, Ã¢â‚¬Â¦)
  - Each with its own subset of TOML fields bound via `data.strategies.high_base`
- **Options Tab**
  - Min/max DTE, delta sliders, max cost, min R:R
  - Live Option Chain viewer component (calls `api.FetchOptionChain(symbol)`)
- **Scheduler Tab**
  - Time pickers bound to `config.schedule.start` & `.stop`
  - Cron preview string computed client-side

------

#### 2.6 Testing & Validation

```gherkin
Feature: Form Loading & Validation
Scenario: Load and render dynamic form
  Given the JSON schema from backend
  When the GUI initializes
  Then each schema property has a corresponding input control

Scenario: Reject invalid field entry
  Given RSIThreshold field with minimum = 0
  When user enters Ã¢â‚¬Å“-10Ã¢â‚¬Â
  Then the input shows Ã¢â‚¬Å“Value must be Ã¢â€°Â¥ 0Ã¢â‚¬Â and Save is disabled
```

------

#### 2.7 Deliverables

- Fully scaffolded `src/` folder with all tab components
- JSON-schemaÃ¢â‚¬â€œdriven `<DynamicForm>` component integrated in each tab
- `configStore` and `statusStore` wired to Wails backend
- Basic Ã¢â‚¬Å“Test ConnectionÃ¢â‚¬Â and Ã¢â‚¬Å“Quick BacktestÃ¢â‚¬Â prototypes
- Gherkin smoke tests for form rendering & validation

------

> **Next up:** Plan 3 will dive into **Advanced Trading Features & Enhancements**, layering in IV filters, Greeks, dynamic DTE logic, and real-time option-chain visualizations. Ready when you are!

