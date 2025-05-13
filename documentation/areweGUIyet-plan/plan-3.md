Okay, I can definitely help refine Plan 3. Let's apply the same principles to make it clear, efficient, and focused on the necessary complexity, using Gherkin for behavioral definitions where appropriate.

Here is the revised "Plan 3: Advanced Trading Features & Enhancements" echoed back to you:

Markdown

### Revised Plan 3: Advanced Trading Features & Enhancements

**Timeline:** ~1.5 - 2 weeks

**Preamble:** This phase builds upon the core GUI and configuration system established in Phase 2. We will introduce more sophisticated trading logic by adding advanced filtering options (liquidity, volatility, Greeks, probability), dynamic expiration date (DTE) selection, and event avoidance mechanisms. These enhancements aim to increase the precision and robustness of the trading strategy execution.

**Objective:** Integrate advanced filtering and selection criteria into both the backend trading logic and the frontend configuration interface, allowing users fine-grained control over option selection based on market conditions and risk parameters.

------

#### 3.1 Extend Configuration Model & Schema

1.  **Update `config.toml` Structure:**
    * Add new sections and parameters to `TraderAdmin/config/config.toml` to accommodate advanced options. Group related settings logically.
    * *Example Additions:*
      ```toml
      # Add within TraderAdmin/config/config.toml

      [options_filters]
      # Liquidity
      min_open_interest = 500
      max_bid_ask_spread_percentage = 0.6 # e.g., 60% of the mark price

      # Volatility
      use_iv_rank_filter = true
      min_iv_rank = 25.0 # Percentile
      max_iv_rank = 75.0 # Percentile
      use_iv_skew_filter = false
      min_put_call_iv_skew_percentage = -10.0 # Put IV can be 10% lower than Call IV
      max_put_call_iv_skew_percentage = 20.0  # Put IV can be 20% higher than Call IV

      # Probability & Risk/Reward
      use_pop_filter = true
      min_probability_of_profit_percentage = 55.0 # Based on theoretical model
      use_width_vs_expected_move_filter = true
      max_spread_width_vs_expected_move_percentage = 120.0 # Spread width <= 1.2 * Expected Move

      [greek_limits]
      use_greek_limits = true
      max_abs_position_delta = 0.50 # Max delta exposure per position
      max_abs_position_gamma = 0.05 # Max gamma exposure per position
      max_abs_position_vega = 10.0  # Max vega exposure per position
      min_position_theta = 0.10   # Minimum positive theta decay per day per position

      [trade_timing]
      # Dynamic DTE Calculation
      use_dynamic_dte = true
      target_dte_mode = "ATR_MULTIPLE" # Or "FIXED", "VOLATILITY_INDEX"
      dte_atr_period = 14
      dte_atr_coefficient = 1.2 # Target DTE = ATR(14) * 1.2 (rounded)
      fixed_target_dte = 45   # Used if target_dte_mode = "FIXED"
      min_dte = 7
      max_dte = 90

      # Event Avoidance
      avoid_earnings_days_before = 3
      avoid_earnings_days_after = 1
      avoid_ex_dividend_days_before = 2
      ```

2.  **Update Go Backend `Config` Struct:**
    * Modify the corresponding Go struct (e.g., in `backend/config/config.go`) to include fields matching the new `config.toml` parameters. Use appropriate data types and struct tags for TOML parsing and JSON schema generation.

3.  **Regenerate & Expose JSON Schema:**
    * Rerun the JSON schema generation process in the Go backend.
    * Ensure the `GetConfigSchema()` Wails function now returns the updated schema including all new parameters and their metadata (types, descriptions from struct tags, constraints).

------

#### 3.2 Backend Logic Enhancements (Conceptual)

* **Refactor Option Selection / Filtering Logic:**
    * Modify the core backend logic (likely in Go or Python service) responsible for fetching options data and filtering potential trades/spreads.
    * This logic should now:
        1.  Load the extended configuration.
        2.  Fetch necessary market data (option chains, underlying price, volatility metrics, Greeks, event dates).
        3.  Apply the configured filters sequentially or in an optimized order:
            * **Event Avoidance:** Exclude expirations falling within the specified windows around earnings or ex-dividend dates.
            * **DTE Filtering:** Select expirations based on the `trade_timing` settings (fixed DTE, dynamic DTE calculation, min/max DTE).
            * **Liquidity Filters:** Filter individual option legs based on `min_open_interest` and `max_bid_ask_spread_percentage`.
            * **Volatility Filters:** Filter based on `min_iv_rank`, `max_iv_rank`, and IV skew if enabled.
            * **Spread Construction:** Build potential spreads (e.g., verticals, iron condors) based on strategy rules.
            * **Greek Limits:** Filter constructed spreads based on calculated position Greeks (`delta`, `gamma`, `vega`, `theta`) against configured limits.
            * **Probability/Risk Filters:** Filter spreads based on calculated Probability of Profit (`min_pop`) and `max_spread_width_vs_expected_move_percentage`.
    * The final output should be a list of valid, filtered candidate trades/spreads meeting all criteria.

------

#### 3.3 GUI Integration & Enhancements

1.  **Consume Updated Schema:**
    * The frontend (`schemaStore`) will automatically load the new schema on startup.

2.  **Enhance `<DynamicForm>` Component (If Necessary):**
    * Ensure the `DynamicForm.svelte` component can handle any new input types or validation patterns introduced by the advanced options (though most should map to existing types like number, boolean, select).
    * Consider adding more sophisticated input controls if needed (e.g., sliders with defined steps for percentages, specific date range pickers if applicable).

3.  **Update Configuration Tabs:**
    * The existing tabs (`OptionsTab`, `TradingRiskTab`, `SettingsTab`) should automatically display the new configuration fields thanks to the dynamic form generation.
    * Organize the new fields logically within these tabs, perhaps using collapsible sections or sub-tabs if a single tab becomes too crowded.
    * Add clear labels and potentially tooltips (using the `description` field from the JSON schema) to explain each advanced parameter.

4.  **Develop Option Chain Viewer Component (Placeholder/Basic):**
    * If not already started, create a basic `OptionChainViewer.svelte` component within the `OptionsTab`.
    * Initially, this might just display fetched chain data in a table format.
    * **Future Enhancement (Phase 4/5):** Add interactive filtering controls directly to this viewer (e.g., sliders for OI, IV Rank) that dynamically refilter the displayed chain *client-side* or trigger a backend refetch with new parameters. For this phase, focus is on configuring the *backend* filters via the main forms.

------

#### 3.4 Testing & Validation (Behavior Defined with Gherkin)

```gherkin
Feature: Advanced Option Filtering and Selection

  Scenario: Filtering by Liquidity Criteria
    Given the configuration specifies MinOpenInterest=500 and MaxBidAskSpreadPercentage=0.5
    And an option chain is fetched containing contracts with varying liquidity
    When the backend filters options for potential trades
    Then only individual option contracts with OpenInterest >= 500 and BidAskSpread <= 50% of the mark price are considered for spread construction

  Scenario: Filtering by IV Rank
    Given the configuration specifies UseIVRankFilter=true, MinIVRank=30, MaxIVRank=70
    And the calculated IV Rank for the underlying is 25%
    When the backend evaluates the underlying for trades
    Then no trades are considered for this underlying due to low IV Rank

  Scenario: Filtering Spreads by Greek Limits
    Given the configuration specifies UseGreekLimits=true and MaxAbsPositionDelta=0.50
    And a potential candidate spread is constructed with a calculated position delta of 0.65
    When the backend filters constructed spreads
    Then this spread is rejected due to exceeding the MaxAbsPositionDelta limit

  Scenario: Dynamic DTE Selection based on ATR
    Given the configuration specifies UseDynamicDTE=true, TargetDTEMode="ATR_MULTIPLE", DTEAtrCoefficient=1.2
    And the calculated 14-day ATR for the underlying implies a target DTE of 24 days (after applying coefficient and rounding)
    And available expirations are [10, 17, 24, 31, 38] days away
    When the backend selects target expirations
    Then the expiration 24 days away is prioritized or selected

  Scenario: Event Avoidance for Earnings
    Given the configuration specifies AvoidEarningsDaysBefore=3 and AvoidEarningsDaysAfter=1
    And the underlying has an earnings announcement scheduled in 2 days
    And available expirations are [1, 8, 15, 22] days away
    When the backend filters expirations
    Then the expirations 1 and 8 days away are excluded due to the upcoming earnings event

  Scenario: Configuration Display in GUI
    Given the backend provides an updated JSON schema including 'options_filters' and 'greek_limits'
    And the frontend loads the schema and configuration
    When the user navigates to the 'OptionsTab' or 'TradingRiskTab'
    Then input controls for MinOpenInterest, MaxBidAskSpreadPercentage, UseGreekLimits, MaxAbsPositionDelta, etc., are displayed
    And these controls reflect the current values loaded from the configuration store
```

------

#### 3.5 Deliverables for Phase 3

- Updated `TraderAdmin/config/config.toml` template including sections for advanced filters (liquidity, IV, Greeks, probability, timing, events).
- Updated Go backend `Config` struct matching the new TOML structure.
- Regenerated JSON schema reflecting all new configuration parameters.
- Enhanced backend service logic implementing the filtering based on the new configuration options.
- GUI tabs (`OptionsTab`, `TradingRiskTab`, etc.) correctly display and allow editing of the new advanced parameters via the `<DynamicForm>` component.
- Passing Gherkin scenarios validating the backend filtering logic and the GUI's ability to display/edit the new settings.

------

> **Next:** With these advanced trading controls implemented, **Plan 4: Configuration Management Workflow & Scheduling** will focus on the crucial pause/edit/unpause functionality for safe configuration changes and implementing the trading schedule defined in the configuration.
