"Plan 4: Configuration Management Workflow & Scheduling" with the same focus on clarity, efficiency, and necessary detail, using Gherkin for behavioral specifications.

Here's the revised plan echoed back to you:

Markdown

### Revised Plan 4: Configuration Management Workflow & Scheduling

**Timeline:** ~1 week

**Preamble:** This phase is critical for operational stability and automation. We will implement a robust workflow for users to safely update the application's configuration (pause services, save new config, unpause services). Additionally, we'll integrate a scheduler to automate the start and stop of trading activities based on user-defined times.

**Objective:** Implement a reliable "Save & Restart" (or "Apply Configuration") workflow in the GUI and backend, and enable time-based scheduling of trading operations controlled via the `config.toml` file.

------

#### 4.1 Backend API for Configuration Workflow & Scheduling

1.  **Define Wails Go Backend Functions:**
    * **`PauseTradingServices() error`**:
        * Identifies target Kubernetes deployments/pods (e.g., Python orchestrator, Go scanner) using labels (e.g., `app=traderadmin-orchestrator`, `app=traderadmin-scanner`).
        * Uses the Kubernetes client-go library to gracefully scale down the targeted deployments to 0 replicas or use a more sophisticated pause mechanism if available (e.g., by setting an annotation that a custom controller acts upon to pause operations within the pods without fully scaling down).
        * Returns an error if pausing fails.
    * **`SaveConfigurationAndRestart(configData map[string]interface{}) error`**:
        * This will be the primary function called by the GUI.
        * **Step 1: Pause:** Calls `PauseTradingServices()`. If error, return immediately.
        * **Step 2: Validate & Save:**
            * Validates `configData` against the JSON schema (this can be a re-validation or primary server-side validation).
            * If invalid, returns a descriptive error.
            * Creates a timestamped backup of the current `config.toml` (e.g., `config.toml.bak.YYYYMMDD_HHMMSS`) on the PVC.
            * Overwrites the main `config.toml` on the PVC with the new `configData` (properly formatted as TOML).
            * Returns an error if saving fails.
        * **Step 3: Unpause & Reload:** Calls `ResumeTradingServices()`. If error, report but note that config was saved.
        * Returns `nil` on full success.
    * **`ResumeTradingServices() error`**:
        * Scales the targeted deployments back to their original replica count (e.g., 1).
        * Relies on the previously implemented `fsnotify` (for Go) and signal-based reload (for Python, if still applicable, or also `fsnotify` if Python service is adapted) to pick up the changed `config.toml` upon restart/unpause. Kubernetes readiness/liveness probes should ensure services only become "ready" after successfully loading the new config.
        * Returns an error if unpausing fails.

2.  **Python Orchestrator: Scheduling Logic:**
    * The Python orchestrator service will be responsible for managing the trading schedule.
    * On startup (and after a configuration reload), it reads the schedule parameters from its loaded configuration (e.g., `config.trading_schedule.enabled`, `config.trading_schedule.start_time_utc`, `config.trading_schedule.stop_time_utc`).
    * It should use a robust scheduling library (like `schedule` or APScheduler).
    * A global, thread-safe flag (e.g., `is_trading_session_active: bool`) will be maintained.
    * The scheduler will set `is_trading_session_active = True` at `start_time_utc` and `is_trading_session_active = False` at `stop_time_utc`.
    * All order entry and active trading logic within the orchestrator must check the state of `is_trading_session_active` before proceeding.
    * Ensure time zones are handled correctly (e.g., by requiring UTC times in `config.toml`).

3.  **Configuration for Scheduling in `config.toml`:**
    * Add a dedicated section if not already present:
        ```toml
        [trading_schedule]
        enabled = true             # Master switch for the scheduler
        start_time_utc = "13:30"   # HH:MM format, UTC (e.g., 9:30 AM ET)
        stop_time_utc = "20:00"    # HH:MM format, UTC (e.g., 4:00 PM ET)
        # Optionally, add days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        ```

------

#### 4.2 GUI Integration

1.  **"Apply Configuration" Button:**
    * In a prominent location (e.g., `StatusBar.svelte` or a dedicated section in `SettingsTab.svelte`), add an "Apply Configuration" (or "Save & Restart Services") button.
    * This button becomes enabled only if there are pending changes in the `configStore` (i.e., the store's content differs from the last successfully loaded/saved state).
    * When clicked, it calls the `SaveConfigurationAndRestart(updatedConfig)` Wails backend function, passing the current state of the `configStore`.
    * Provide visual feedback during the operation (e.g., loading spinner, disabling the button).
    * Display success or error messages (e.g., using toasts) based on the backend response.
    * On success, update the "pending changes" state.

2.  **Scheduler Configuration UI (`SettingsTab.svelte` or dedicated `ScheduleTab.svelte`):**
    * Use the `<DynamicForm />` component to render input fields for `trading_schedule.enabled` (checkbox), `trading_schedule.start_time_utc` (e.g., `<input type="time">`), and `trading_schedule.stop_time_utc`.
    * Changes made here update the `configStore`. The "Apply Configuration" button handles the actual saving and service restart.
    * Consider adding a read-only display of the current server time (UTC) or the user's local time with UTC conversion for clarity.

------

#### 4.3 Testing & Validation (Behavior Defined with Gherkin)

```gherkin
Feature: Configuration Save, Service Restart, and Trading Schedule Workflow

  Scenario: Successfully Applying Configuration Changes
    Given the trading services (orchestrator, scanner) are running
    And the user has made valid modifications to the configuration in the GUI
    When the user clicks the "Apply Configuration" button
    Then the GUI calls the 'SaveConfigurationAndRestart' backend function
    And the backend function first calls 'PauseTradingServices'
    And the targeted Kubernetes deployments (orchestrator, scanner) are scaled to 0 replicas or paused
    And the backend function then validates and saves the new configuration to 'config.toml' on the PVC
    And a backup of the old 'config.toml' is created
    And the backend function then calls 'ResumeTradingServices'
    And the targeted Kubernetes deployments are scaled back to their original replica count or resumed
    And the services (orchestrator, scanner) reload their configuration upon restart/unpause
    And the GUI displays a success message

  Scenario: Handling Failure During Configuration Apply (e.g., Pause Fails)
    Given the trading services are running
    And the user clicks "Apply Configuration"
    When the 'PauseTradingServices' backend function fails (e.g., Kubernetes API error)
    Then the 'SaveConfigurationAndRestart' process is halted before saving the config
    And the GUI displays an error message indicating the failure point (e.g., "Failed to pause services")
    And the services remain in their original running state with the old configuration

  Scenario: Automated Trading Stop Based on Schedule
    Given the 'trading_schedule.enabled' in config.toml is true
    And 'trading_schedule.stop_time_utc' is set to "20:00"
    And the Python orchestrator service is running and its internal 'is_trading_session_active' flag is true
    When the system time (UTC) reaches "20:00:00"
    Then the Python orchestrator's scheduler sets its 'is_trading_session_active' flag to false
    And new trading orders are no longer placed by the orchestrator

  Scenario: Automated Trading Start Based on Schedule
    Given the 'trading_schedule.enabled' in config.toml is true
    And 'trading_schedule.start_time_utc' is set to "13:30"
    And the Python orchestrator service is running and its internal 'is_trading_session_active' flag is false
    When the system time (UTC) reaches "13:30:00"
    Then the Python orchestrator's scheduler sets its 'is_trading_session_active' flag to true
    And the orchestrator is now permitted to place new trading orders (if other conditions met)

  Scenario: Scheduler Respects 'enabled' Flag
    Given the 'trading_schedule.enabled' in config.toml is false
    And 'trading_schedule.start_time_utc' is set to "13:30"
    And 'trading_schedule.stop_time_utc' is set to "20:00"
    And the Python orchestrator service is running
    When the system time (UTC) passes "13:30:00" and "20:00:00"
    Then the Python orchestrator's 'is_trading_session_active' flag remains unchanged (e.g., consistently false or true based on its initial state before schedule times)
    And trading activity is not automatically started or stopped by the scheduler
```

------

#### 4.4 Deliverables for Phase 4

- Implemented and tested Wails Go backend functions: `PauseTradingServices`, `SaveConfigurationAndRestart`, `ResumeTradingServices`.
- Python orchestrator service includes robust scheduling logic that manages an `is_trading_session_active` flag based on `config.toml` settings.
- GUI features an "Apply Configuration" button with appropriate loading/feedback states, triggering the backend workflow.
- GUI section (e.g., in `SettingsTab`) allows users to view and modify trading schedule parameters.
- Updated `config.toml` template with a `[trading_schedule]` section.
- Passing Gherkin scenarios for the configuration workflow and automated trading schedule.

------

> **Next:** With the core operational workflows in place, **Plan 5: Real-Time Monitoring & Alerts** will focus on providing users with insights into the system's performance and notifying them of critical events.
