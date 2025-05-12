### Plan 4: Save/Restart & Scheduling Workflow

**Timeline:** ~1 week
 **Objective:** Implement a rock-solid pauseÃ¢â€ â€™editÃ¢â€ â€™unpause flow plus time-of-day scheduling so traders can safely tweak settings and/or automate trading windows.

------

#### 4.1 Backend Methods

1. **PauseStack()**

   - Use Docker SDK (or `kubectl scale`) to pause trading containers/pods
   - Label targets: `app=python-orchestrator`, `app=go-scanner`

2. **SaveConfig(cfg)**

   - Validate against JSON schema
   - Backup current `config.toml` Ã¢â€ â€™ `config.toml.bak.YYYYMMDD_HHMMSS`
   - Overwrite `/config/config.toml` via TOML encoder

3. **UnpauseStack()**

   - Unpause containers/pods
   - For each service, send reload signal (`SIGUSR1` for Python, rely on fsnotify for Go)

4. **Scheduler Hooks**

   - Read `config.schedule.start` & `config.schedule.stop` (cron or HH:MM)

   - In Python orchestrator, spawn a scheduler thread:

     ```python
     import schedule, time

     def start_trading(): trading_enabled.set(True)
     def stop_trading():  trading_enabled.set(False)

     schedule.every().day.at(cfg.schedule.start).do(start_trading)
     schedule.every().day.at(cfg.schedule.stop).do(stop_trading)

     while True:
         schedule.run_pending()
         time.sleep(1)
     ```

   - All order-entry logic gated on `trading_enabled.get()`

------

#### 4.2 GUI Integration

1. **Ã¢â‚¬Å“Save & RestartÃ¢â‚¬Â Button**

   ```ts
   async function saveAndRestart(cfg) {
     loading.set(true)
     try {
       await api.PauseStack()
       await api.SaveConfig(cfg)
       await api.UnpauseStack()
       toast.success("Configuration applied")
     } catch (e) {
       toast.error("Failed to apply configuration: " + e.message)
     } finally {
       loading.set(false)
     }
   }
   ```

2. **Scheduler Tab**

   - Two time pickers (`<input type="time">`) bound to `config.schedule.start` and `.stop`
   - Ã¢â‚¬Å“Apply ScheduleÃ¢â‚¬Â Ã¢â€ â€™ `saveAndRestart(config)`

------

#### 4.3 Cucumber/Gherkin Scenarios

```gherkin
Feature: Pause/Edit/Unpause Workflow
  Scenario: Safely apply new settings
    Given containers are running
    When I click Ã¢â‚¬Å“Save & RestartÃ¢â‚¬Â
    Then PauseStack is called
      And config.toml is backed up and updated
      And UnpauseStack is called
      And services log Ã¢â‚¬Å“Config reloadedÃ¢â‚¬Â

Feature: Automated Trading Schedule
  Scenario: Auto-stop at end of day
    Given schedule.stop = "16:00"
    And trading_enabled = true
    When system time reaches 16:00
    Then trading_enabled is set to false

  Scenario: Auto-start next day
    Given schedule.start = "09:30"
    And trading_enabled = false
    When system time reaches 09:30
    Then trading_enabled is set to true
```

------

#### 4.4 Validation & Tests

- **Smoke Test:** Manually click Save & Restart; verify live reload in logs with zero downtime.
- **Schedule Test:** Mock system clock or override scheduler thread to fire immediately; assert `trading_enabled` toggles.

------

#### 4.5 Deliverables

- Backend `PauseStack`, `SaveConfig`, `UnpauseStack` methods implemented and tested
- Scheduler thread in orchestrator managing `trading_enabled` flag
- GUI Ã¢â‚¬Å“Save & RestartÃ¢â‚¬Â button wired and visual feedback added
- Scheduler tab with time-picker UI and validation
- Gherkin tests passing for workflow and scheduling

------

> **Next:** Ready for **Plan 5: Real-Time Monitoring & Alerts**, where weÃ¢â‚¬â„¢ll wire up dashboards, charts, and notification channels? Let me know!

