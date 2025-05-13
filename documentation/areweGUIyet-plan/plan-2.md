### Revised Plan 2: Core GUI Components

**Timeline:** ~1.5 - 2 weeks

**Preamble:** Building on the foundation from Phase 1, this phase focuses on creating the interactive user interface within the Wails application. We will implement the main application shell, establish core UI components, dynamically generate forms from our centralized configuration schema, and set up state management for configuration and real-time status.

**Objective:** Develop a functional and user-friendly GUI shell that allows users to view application status, load existing configurations, edit settings through dynamically generated forms, and save changes back to the backend.

------

#### 2.1 UI Architecture & Core Components

1.  **Refined Component Layout:**
    Organize the frontend Svelte code within the `TraderAdmin/frontend/src/` directory.

    ```
    TraderAdmin/frontend/src/
    ├── App.svelte             # Main application shell, orchestrates tabs and status bar
    ├── main.ts                # Entry point
    ├── components/            # General reusable UI elements
    │   ├── NavTabs.svelte     # Tab navigation (e.g., sidebar or top bar)
    │   ├── StatusBar.svelte   # Displays connection & system status
    │   └── DynamicForm.svelte # Core component for rendering forms from schema
    ├── tabs/                  # Components representing main content areas/tabs
    │   ├── OverviewTab.svelte
    │   ├── ConnectionTab.svelte
    │   ├── TradingRiskTab.svelte
    │   ├── StrategiesTab.svelte # Potentially using sub-components per strategy type
    │   ├── OptionsTab.svelte
    │   ├── MonitoringTab.svelte # Basic logs/status display for now
    │   └── SettingsTab.svelte   # Combined settings (e.g., Schedule, Alerts)
    └── stores/                # Svelte stores for state management
        ├── activeTab.ts       # Store to manage the currently visible tab
        ├── configStore.ts     # Writable store holding the application configuration
        ├── statusStore.ts     # Store for real-time status updates (connections, etc.)
        └── schemaStore.ts     # Store to hold the loaded JSON configuration schema
    ```
    *Note: This is a suggested starting set of tabs. More can be added later.*

2.  **Tab Navigation:**
    * Implement a simple, routing-less tab switching mechanism.
    * `NavTabs.svelte` will list available tabs and update the `activeTab` store when a tab is clicked.
    * `App.svelte` will conditionally render the component from the `tabs/` directory based on the value of the `activeTab` store.

------

#### 2.2 Configuration Handling: Schema & Store

1.  **Backend: Generate JSON Schema:**
    * In the Go backend, create a function that uses reflection (e.g., with `[github.com/alecthomas/jsonschema](https://github.com/alecthomas/jsonschema)`) on the main `Config` struct (defined based on `config.toml`) to generate a JSON Schema representation.
    * Ensure the schema includes metadata useful for form generation (e.g., descriptions, types, constraints like min/max, enums).

2.  **Backend: Expose Schema via Wails:**
    * Create a Wails Go function callable from the frontend (e.g., `GetConfigSchema() string`).
    * This function calls the schema generation logic and returns the JSON schema as a string.

3.  **Frontend: Schema Store (`schemaStore.ts`):**
    * Create a Svelte store (e.g., `schemaStore`) to hold the fetched schema.
    * On application startup, call the `GetConfigSchema()` Wails function and populate this store.

4.  **Frontend: Configuration Store (`configStore.ts`):**
    * Create a writable Svelte store (`configStore`) to hold the application's configuration data, mirroring the structure of `config.toml`.
    * Implement functions within the store module to interact with the backend:
        * `loadConfig()`: Calls a Wails backend function `LoadConfig() map[string]interface{}` to fetch the current configuration and updates the store.
        * `saveConfig()`: Takes the current state of the `configStore`, calls a Wails backend function `SaveConfig(config map[string]interface{}) error`, and potentially reloads the config on success.

5.  **Backend: Config Load/Save API:**
    * Implement the corresponding Go functions (`LoadConfig`, `SaveConfig`) in the Wails backend.
    * `LoadConfig`: Reads `config.toml` (from the PVC mount path), parses it, and returns it as a map or struct suitable for the frontend.
    * `SaveConfig`: Takes the configuration map from the frontend, performs validation (essential!), backs up the old `config.toml`, writes the new configuration, and triggers the live-reload mechanism established in Phase 1.

------

#### 2.3 Dynamic Form Implementation (`DynamicForm.svelte`)

* Develop a reusable Svelte component (`<DynamicForm />`) that accepts:
    * A portion of the JSON schema (`subSchema`).
    * A corresponding portion of the configuration data from `configStore` (`subData`).
* The component should iterate through the `properties` defined in the `subSchema`.
* For each property, it should dynamically render an appropriate HTML input element based on the schema's `type` (e.g., `string` -> `<input type="text">`, `integer`/`number` -> `<input type="number">`, `boolean` -> `<input type="checkbox">`, `enum` -> `<select>`).
* Use schema details like `description` for tooltips or labels, and `minimum`/`maximum`/`required` for basic client-side validation feedback (though primary validation remains on the backend during `SaveConfig`).
* Utilize Svelte's two-way binding (`bind:value`) to link the input elements directly to the `subData` object passed into the component. This ensures the `configStore` is updated as the user types.

------

#### 2.4 Status Monitoring

1.  **Backend: Status API:**
    * Implement a Wails Go function (e.g., `GetStatus() StatusInfo`) that gathers real-time status information (e.g., IBKR connection status, state of managed containers/services). Define a `StatusInfo` struct in Go.

2.  **Frontend: Status Store (`statusStore.ts`):**
    * Create a Svelte store (`statusStore`) to hold the data returned by `GetStatus()`.
    * Implement a mechanism to periodically call `GetStatus()` (e.g., using `setInterval`) and update the `statusStore`.

3.  **Frontend: Status Bar (`StatusBar.svelte`):**
    * Create a component that subscribes to the `statusStore`.
    * Display key status indicators visually (e.g., connection icons with green/red status, list of services and their states).

------

#### 2.5 Initial Tab Implementations

* Integrate the `<DynamicForm />` component into the primary configuration tabs (`ConnectionTab`, `TradingRiskTab`, `StrategiesTab`, `OptionsTab`, `SettingsTab`).
* Each tab component will:
    * Subscribe to the `configStore` and `schemaStore`.
    * Pass the relevant slices of the configuration data and schema definition down to one or more `<DynamicForm />` instances.
    * Example: `ConnectionTab` would pass `config.ibkr_connection` and the corresponding part of the schema to `<DynamicForm />`.
* Implement basic functionality buttons where appropriate (e.g., "Test Connection" in `ConnectionTab` calling a dedicated `TestConnection()` Wails backend function).

------

#### 2.6 Testing & Validation (Behavior Defined with Gherkin)

```gherkin
Feature: Core GUI Component Functionality

  Scenario: Application Initialization and Schema Loading
    Given the TraderAdmin application is started
    When the frontend initializes
    Then the application calls the backend 'GetConfigSchema' function
    And the 'schemaStore' in the frontend is populated with a valid JSON schema structure

  Scenario: Configuration Loading and Display
    Given the 'schemaStore' is populated
    When the frontend calls the backend 'LoadConfig' function
    Then the 'configStore' is populated with data matching the config.toml structure
    And the 'OverviewTab' (or default tab) is displayed
    And the input fields within the active tab reflect the values from the 'configStore'

  Scenario: Dynamic Form Rendering based on Schema
    Given the 'schemaStore' and 'configStore' are populated
    And the 'ConnectionTab' is active
    Then a form is rendered containing input elements corresponding to properties in the 'ibkr_connection' section of the schema
    And the input types (text, number, checkbox) match the schema types

  Scenario: Editing Configuration via Dynamic Form
    Given the 'ConnectionTab' is active and displaying loaded configuration
    When the user changes the value in the 'host' input field
    Then the corresponding 'ibkr_connection.host' value in the 'configStore' is updated immediately

  Scenario: Basic Input Validation Feedback
    Given the 'TradingRiskTab' is active
    And the schema defines 'default_risk_per_trade_percentage' with a minimum value of 0.1 and maximum of 5.0
    When the user enters '0.05' into the corresponding input field
    Then visual feedback indicates the value is below the minimum (e.g., red border, tooltip)
    # Note: Actual prevention of saving invalid data is handled by backend SaveConfig validation

  Scenario: Saving Configuration Changes
    Given the user has made valid changes to the configuration via the forms
    When the user clicks the 'Save Configuration' button
    Then the frontend calls the backend 'SaveConfig' function with the current data from 'configStore'
    And the backend validates the received configuration
    And the backend saves the validated configuration to 'config.toml'
    And the backend triggers the live-reload mechanism for relevant services
    And the frontend receives confirmation of success or failure

  Scenario: Status Bar Updates
    Given the TraderAdmin application is running
    When the 'statusStore' is updated (e.g., IBKR connection drops)
    Then the 'StatusBar.svelte' component visually reflects the new status (e.g., connection icon turns red)
```

------

#### 2.7 Deliverables for Phase 2

- Scaffolded `TraderAdmin/frontend/src/` directory with core components (`App`, `NavTabs`, `StatusBar`), initial tab components, and Svelte stores.
- A functional, reusable `<DynamicForm />` component capable of rendering inputs based on a JSON schema.
- Implemented Wails backend functions: `GetConfigSchema`, `LoadConfig`, `SaveConfig`, `GetStatus`, and potentially `TestConnection`.
- Integration of the dynamic form into key configuration tabs, bound to the `configStore`.
- A functional `StatusBar` displaying basic real-time status information fetched from the backend.
- Passing Gherkin scenarios demonstrating the core load-edit-save configuration workflow and status updates.

------

> **Next:** Phase 3 will focus on **Advanced Trading Features & Enhancements**, including implementing more complex UI elements like option chain viewers, integrating real-time data streams (if applicable beyond polling), refining strategy configuration interfaces, and potentially adding basic charting or visualization components.
