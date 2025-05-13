# Optimized Comprehensive TraderAdmin GUI Roadmap

## Overview and Goals

Create a robust trading platform combining a Wails GUI with Svelte/TypeScript frontend, Docker/Kubernetes backend (for server-side components), and IBKR integration to support advanced trading and risk management. The GUI will feature real-time monitoring, comprehensive strategy configuration, smooth pause-edit-unpause workflows, and user-friendly packaging.

## Project Structure

TraderAdmin/

├── backend/              # Go code for Wails backend

│   ├── api/              # Wails API methods callable from frontend

│   ├── config/           # Config struct definitions, schema generation

│   ├── services/         # Core logic (e.g., K8s interaction, metrics aggregation)

│   └── models/           # Data structures (e.g., for config, metrics)

├── frontend/             # Svelte components for Wails GUI

│   ├── src/

│   │   ├── components/   # Reusable UI elements (DynamicForm, StatusBar, etc.)

│   │   ├── tabs/         # Main application tabs (ConnectionTab, MonitoringTab, etc.)

│   │   └── stores/       # Svelte stores (configStore, statusStore, etc.)

│   └── public/           # Static assets (icons, etc.)

├── deploy/               # Kubernetes manifests for server-side components

├── build_scripts/        # Scripts for building (e.g., windows_installer.nsi)

└── config.toml           # Central configuration file (template)

# (Python orchestrator and other potential server-side services would live in their own directories,

# managed within the same Git repository but potentially built and containerized separately)

---

## Phase 1: Foundation & Backend Setup

* **Timeline:** ~1 week
* **Core Goals:**
    1.  Initialize the Wails/Svelte-TS project (`TraderAdmin` GUI) within the existing Git repo.
    2.  Establish Docker and Kubernetes-based runtime environment for backend services (Python orchestrator, Go scanner if separate).
    3.  Centralize all tunable parameters into a single `config.toml` (used by GUI and backend services).
    4.  Implement illustrative live-reload mechanisms for backend services.
* **Key Tasks:**
    * Scaffold Wails application (`TraderAdmin` directory).
    * Define Go module dependencies for Wails backend.
    * Setup Python orchestrator dependencies.
    * Create `config.toml` structure and `.gitignore`.
    * Develop Kubernetes PVC and example Deployment manifests for backend services.
    * Implement conceptual live-reload handlers (e.g., `fsnotify` for Go, `watchdog` or signal-based for Python).
* **Representative Gherkin Scenario:**
    ```gherkin
    Scenario: Configuration File Hot-Reload in Python Orchestrator
      Given the Python orchestrator service is running in Kubernetes
      And it is configured to watch "/app/config/config.toml" for changes
      When the content of "/app/config/config.toml" (on the PVC) is updated
      Then the Python orchestrator service detects the change
      And logs a message indicating that the configuration has been reloaded
    ```

---

## Phase 2: Core GUI Components

* **Timeline:** ~1.5 - 2 weeks
* **Core Goals:**
    1.  Develop the main GUI shell, tab navigation, and status bar.
    2.  Implement dynamic form generation from a JSON schema derived from `config.toml`.
    3.  Establish Svelte stores for managing configuration, schema, and application status.
    4.  Integrate Wails backend functions for loading/saving configuration and fetching status.
* **Key Tasks:**
    * Define UI component structure (`App.svelte`, `NavTabs.svelte`, `StatusBar.svelte`, tab components).
    * Backend: Generate JSON schema from Go `Config` struct; expose via Wails.
    * Frontend: Create `schemaStore`, `configStore`, `statusStore`.
    * Implement `DynamicForm.svelte` to render inputs based on schema.
    * Integrate `DynamicForm` into initial configuration tabs.
    * Backend: Implement `LoadConfig`, `SaveConfig`, `GetStatus` Wails functions.
* **Representative Gherkin Scenario:**
    ```gherkin
    Scenario: Editing Configuration via Dynamic Form
      Given the 'ConnectionTab' is active and displaying loaded configuration
      When the user changes the value in the 'host' input field
      Then the corresponding 'ibkr_connection.host' value in the 'configStore' is updated immediately
    ```

---

## Phase 3: Advanced Trading Features & Enhancements

* **Timeline:** ~1.5 - 2 weeks
* **Core Goals:**
    1.  Extend `config.toml` and its corresponding Go struct/JSON schema with advanced trading parameters.
    2.  Enhance backend trading logic (Python orchestrator/Go services) to utilize these advanced filters.
    3.  Integrate new configuration fields into the GUI using the `DynamicForm`.
* **Key Tasks:**
    * Add parameters for liquidity, IV, Greeks, probability, DTE, event avoidance to `config.toml` and Go `Config` struct.
    * Regenerate and expose updated JSON schema.
    * Modify backend option selection/filtering logic to apply new criteria.
    * Ensure `DynamicForm.svelte` correctly renders inputs for new advanced parameters.
    * Update relevant GUI tabs (`OptionsTab`, `TradingRiskTab`) to display new fields.
* **Representative Gherkin Scenario:**
    ```gherkin
    Scenario: Filtering Spreads by Greek Limits
      Given the configuration specifies UseGreekLimits=true and MaxAbsPositionDelta=0.50
      And a potential candidate spread is constructed with a calculated position delta of 0.65
      When the backend filters constructed spreads
      Then this spread is rejected due to exceeding the MaxAbsPositionDelta limit
    ```

---

## Phase 4: Configuration Management Workflow & Scheduling

* **Timeline:** ~1 week
* **Core Goals:**
    1.  Implement a robust "Apply Configuration" workflow (pause services, save config, resume services).
    2.  Enable time-based scheduling of trading operations controlled via `config.toml`.
* **Key Tasks:**
    * Backend: Implement Wails Go functions `PauseTradingServices`, `SaveConfigurationAndRestart`, `ResumeTradingServices` (interacting with Kubernetes).
    * Python Orchestrator: Implement scheduling logic based on `config.toml` (e.g., using `schedule` library) to manage an `is_trading_session_active` flag.
    * GUI: Add "Apply Configuration" button, integrate with backend workflow, provide user feedback.
    * GUI: Implement UI in `SettingsTab` or `ScheduleTab` for schedule parameters.
* **Representative Gherkin Scenario:**
    ```gherkin
    Scenario: Successfully Applying Configuration Changes
      Given the trading services (orchestrator, scanner) are running
      And the user has made valid modifications to the configuration in the GUI
      When the user clicks the "Apply Configuration" button
      Then the GUI calls the 'SaveConfigurationAndRestart' backend function
      And services are paused, config saved, services resumed and reloaded.
    ```

---

## Phase 5: Real-Time Monitoring & Alerts

* **Timeline:** ~1 - 1.5 weeks
* **Core Goals:**
    1.  Develop a monitoring dashboard in the GUI for real-time insights into portfolio and system health.
    2.  Implement an alert system configurable via `config.toml` to notify users of predefined conditions.
* **Key Tasks:**
    * Define key metrics (portfolio, trade stats, system health).
    * Backend: Implement Wails Go function `GetLatestMetrics()`.
    * Backend (Python orchestrator or Go): Implement alert evaluation logic based on `config.toml` thresholds and notification dispatch (Email, Slack).
    * Backend: Implement Wails Go function `TestAlertNotification()`.
    * GUI: Create `MonitoringTab.svelte` to display metrics and charts.
    * GUI: Create `AlertsConfigurationTab.svelte` to manage alert settings and test notifications.
* **Representative Gherkin Scenario:**
    ```gherkin
    Scenario: Triggering a High Order Latency Alert
      Given the alert configuration 'max_order_latency_ms' is set to 200
      And an order execution takes 250ms
      And the alert system evaluates metrics
      Then an alert notification is triggered and sent via enabled channels
    ```

---

## Phase 6: Testing, Documentation & Polish

* **Timeline:** ~1 - 2 weeks
* **Core Goals:**
    1.  Ensure application quality and stability through comprehensive testing.
    2.  Create essential user and developer documentation.
    3.  Perform general code cleanup and UI/UX polish.
* **Key Tasks:**
    * Implement unit tests (Go, Python, Svelte), integration tests (service interactions, backend-K8s), and E2E tests for critical workflows.
    * Write User Documentation (README, Configuration Guide, GUI Guide).
    * Write Developer Documentation (Code Structure, API Docs, Setup Guide).
    * Refactor code, improve error handling, address UI inconsistencies.
* **Representative Gherkin Scenario:**
    ```gherkin
    Scenario: Executing End-to-End Test for Configuration Workflow
      Given an automated E2E test environment is set up
      When the E2E test script simulates loading the app, changing a config value, and applying the configuration
      Then the test verifies that services are paused, config is saved, services resume, and the change is reflected.
    ```

---

## Phase 7: Deployment Preparation, Packaging & Windows Installer

* **Timeline:** ~1 week
* **Core Goals:**
    1.  Package the Wails application for target platforms, including a Windows installer.
    2.  Optimize container images and finalize Kubernetes deployment configurations for server-side components.
    3.  Implement health checks for services.
    4.  Document deployment procedures.
* **Key Tasks:**
    * Wails: `wails build` for production executables.
    * Windows Installer: Develop NSIS script (`.nsi`) to create `TraderAdmin_Setup.exe`.
    * Docker: Refine Dockerfiles (multi-stage builds, non-root users).
    * Kubernetes: Finalize manifests (namespaces, resource requests/limits, readiness/liveness probes).
    * Implement basic HTTP health check endpoints in backend services.
    * Create `DEPLOYMENT.md` and update user docs with installation instructions.
* **Representative Gherkin Scenario:**
    ```gherkin
    Scenario: Creating and Testing Windows Installer (NSIS)
      Given NSIS is installed and an `windows_installer.nsi` script is prepared
      When the NSIS script is compiled
      Then a `TraderAdmin_Setup_vX.Y.Z.exe` installer is generated
      And the installer successfully installs the application on a Windows test environment.
    ```

---

## Implementation Notes

* **Core Technologies:**
    * Wails for desktop app framework (Go backend, Svelte/TS frontend).
    * Go for Wails backend logic and potentially some standalone backend services.
    * Python for the primary trading orchestrator service.
    * Docker/Kubernetes for server-side service orchestration.
    * TOML for the central `config.toml` file.
    * NSIS for Windows installer.
* **API Design Philosophy (Wails Go Backend):**
    * Clear separation between GUI (Svelte) and Go backend logic.
    * Methods exposed from Go to Svelte should be well-defined and handle specific tasks.
    * Reactive data flow in Svelte primarily managed by Svelte stores, updated via Wails calls.
* **Development Workflow:**
    * Implement features incrementally based on these phases.
    * Prioritize clear Gherkin scenarios to define behavior before implementation.
    * Regularly test components and integrations.

This roadmap provides a balanced and detailed approach to building the TraderAdmin GUI, focusing on essential functionality, user experience, and operational robustness, while adhering to the specified constraints.
