### Plan 3: Advanced Trading Features & Enhancements

**Timeline:** ~2 weeks
 **Objective:** Layer in sophisticated strategy controls, risk-and-liquidity filters, dynamic expiration logic, and probability metrics so your scans and executions have enterprise-grade fidelity.

------

#### 3.1 Extend Configuration & Schema

1. **Add new fields to `Config` struct** (in Go/Python) and to `config.toml` under appropriate sections:

   ```toml
   [options]
   min_open_interest = 1000
   max_bid_ask_spread_pct = 0.5
   min_iv_rank = 30.0
   max_iv_rank = 70.0
   min_call_put_skew_pct = 5.0

   [greeks]
   max_theta_per_day = 15.0
   max_vega_exposure = 0.8
   max_gamma_exposure = 0.05

   [probability]
   min_pop = 60.0
   max_width_vs_move_pct = 150.0

   [events]
   skip_earnings_days = 3
   skip_exdiv_days = 2

   [dte]
   dynamic = true
   dte_coefficient = 1.5
   ```

2. **Regenerate JSON schema** via `jsonschema.Reflect(&Config{})` so your forms auto-include these new fields.

------

#### 3.2 Enhance OptionSelector Logic

1. **Liquidity & Spread Filters**

   - In `filter_spreads(...)`, reject any spread containing a leg with

     ```go
     if opt.OpenInterest < cfg.Options.MinOpenInterest ||
        opt.BidAskSpreadPct > cfg.Options.MaxBidAskSpreadPct { continue }
     ```

2. **IV Rank & Skew**

   - Before spread creation, fetch IV metrics (`modelGreeks` via IBKR or Black-Scholes)
   - Reject if `IVRank < MinIVRank` or `> MaxIVRank`
   - Compute `CallIV - PutIV`; reject if less than `MinCallPutSkewPct`

3. **Greek Limits**

   - After building each `OptionSpread`, compute per-day theta and total vega/gamma:

     ```go
     if spread.ThetaPerDay > cfg.Greeks.MaxThetaPerDay { continue }
     if spread.TotalVega > cfg.Greeks.MaxVegaExposure { continue }
     if spread.TotalGamma > cfg.Greeks.MaxGammaExposure { continue }
     ```

4. **Probability & Expected-Move**

   - Use `spread.ModelPOP` or calculate via Black-Scholes; reject if `< MinPOP`
   - Fetch underlyingÃ¢â‚¬â„¢s expected move (e.g. 1ÃÆ’) and compute width / move; reject if `> MaxWidthVsMovePct`

5. **Event Avoidance**

   - Pull calendar data (earnings, ex-div dates) from IBKR API or external
   - Skip any expiration within `SkipEarningsDays` or `SkipExDivDays`

------

#### 3.3 Dynamic DTE & Strike Controls

1. **Dynamic DTE**

   - If `cfg.DTE.Dynamic` is true, compute

     ```python
     target_dte = int(ATR * cfg.DTE.Coefficient)
     ```

   - Filter expirations closest to `target_dte`

2. **Strike Offset & Width**

   - From sorted strikes, pick OTM strike at index `Offset`
   - Sell leg at `Offset + SpreadWidth`

------

#### 3.4 GUI Integration

1. **Update JSON schema** so these fields appear in the **Options tab** and **Risk tab**.
2. **Enhance `<DynamicForm>`**:
   - Render min/max inputs for new numeric values
   - Add help tooltips explaining each metric (e.g. Ã¢â‚¬Å“IV Rank measures current implied vol relative to past yearÃ¢â‚¬Â)
3. **Option Chain Viewer**
   - Add filter controls above the chain: liquidity sliders, IV rank sliders, Greek caps
   - Re-render spreads list upon filter change

------

#### 3.5 Cucumber/Gherkin Smoke Tests

```gherkin
Feature: Liquidity & Greek Filters
  Scenario: Filter by open interest and spread
    Given an options chain with contracts having varying openInterest and bidAskSpreadPct
    When MinOpenInterest=1000 and MaxBidAskSpreadPct=0.5
    Then only contracts with openInterest Ã¢â€°Â¥ 1000 and bidAskSpreadPct Ã¢â€°Â¤ 0.5 are considered

Feature: IV & Skew Filters
  Scenario: Enforce IV rank regime
    Given current IVRank = 80% for AAPL
    When MaxIVRank = 70
    Then AAPL spreads are excluded

Feature: Greek Risk Limits
  Scenario: Prevent excessive theta decay
    Given a candidate spread with ThetaPerDay = 20
    When MaxThetaPerDay = 15
    Then the spread is rejected

Feature: Dynamic DTE Selection
  Scenario: Compute target DTE from ATR
    Given ATR = 10 and DTE.Coefficient = 1.5
    When dynamic DTE is enabled
    Then target DTE = 15 days

Feature: Event Avoidance
  Scenario: Skip earnings week
    Given next earnings in 2 days for TSLA
    And SkipEarningsDays = 3
    Then TSLA expirations are not offered
```

------

#### 3.6 Deliverables

- Updated `Config` definitions and TOML file
- Enhanced `OptionSelector` and spread-building routines in Go/Python
- Expanded JSON schema reflecting new advanced settings
- DynamicForm renders and validates new fields
- Option Chain UI with real-time filter controls
- Passing Gherkin tests for each new feature

------

> **Next:** Once this advanced feature set is in place, weÃ¢â‚¬â„¢ll move on to **Plan 4: Save/Restart & Scheduling Workflow**Ã¢â‚¬â€œÃ¢â‚¬â€œwiring up Pause/Edit/Unpause and time-of-day automation. Let me know when youÃ¢â‚¬â„¢re ready!

