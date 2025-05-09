**Enhancing options strategy settings**

The user is exploring ways to improve options strategy selection using Finviz. To increase robustness and accuracy, I'd recommend adding filters like implied volatility (IV), Greeks such as gamma, theta, vega, and adjusting for skew. It may also help to incorporate features like auto-adjustments for expiration, time decay thresholds, and dynamic DTE (days to expiration) windows. Consider liquidity factors like volume or open interest, and refine criteria with bid-ask spread filters or synthetic Greeks. Lastly, implementing risk metrics like vega risk and gamma exposure could help further tailor the strategy.

**Enhancing options strategy features**

To improve options strategy functionality, I recommend adding advanced features like incorporating probability-of-touch and probability-of-profit metrics. The GUI could display expiration probabilities, mid price, and more details on spread types (e.g., credit vs. debit). It would be beneficial to introduce dynamic parameters, such as DTE selection based on ATR or events, skew metrics, and liquidity checks. Adding position sizing, stop-loss triggers, and filters for factors like open interest and bid-ask spread would provide greater fidelity. Including advanced strategies like iron condor and predictive analytics based on technical signals could further strengthen the strategy.


Thought for 12 seconds


Below is a set of **enhancements** you can layer onto your existing Options Settings to give you far greater precision and control—plus a few **Cucumber/Gherkin** snippets to drive the TDD of each new filter.

---

## 1. Add Liquidity & Execution-Quality Filters

1. **Min Open Interest**

   * Ensures you only trade contracts with enough depth to get filled
   * GUI field: `Min Open Interest`
2. **Max Bid-Ask Spread (%)**

   * Caps the relative spread to avoid over-paying for illiquid strikes
   * GUI field: `Max Bid/Ask Spread (%)`

```gherkin
Feature: Liquidity Filters
  Scenario: Filter out low-liquidity contracts
    Given an option chain for "AAPL"
    And each contract has metrics openInterest and bidAskSpreadPct
    When the selector runs with MinOpenInterest=1000 and MaxBidAskSpreadPct=0.5
    Then it only returns contracts where openInterest ≥ 1000
      And bidAskSpreadPct ≤ 0.5
```

---

## 2. Surface Implied-Volatility Regime

1. **IV Rank / Percentile**

   * Only trade when IV is in a user-defined regime (e.g. high-vol pullbacks vs low-vol mean-reversion)
   * GUI fields: `Min IV Rank (%)`, `Max IV Rank (%)`
2. **IV Skew Filter**

   * Compare call vs put IV to identify directional skew opportunities
   * GUI field: `Min Call/Put IV Skew (%)`

```gherkin
Feature: IV Regime Filters
  Scenario: Only pick spreads in high-vol regime
    Given current IV Rank for AAPL is 75%
    When MinIVRank=70 and MaxIVRank=100
    Then the option selector includes AAPL spreads
  Scenario: Exclude low-vol conditions
    Given current IV Rank for MSFT is 40%
    When MinIVRank=50
    Then the option selector excludes MSFT spreads
```

---

## 3. Greek-Based Risk Controls

1. **Max Daily Theta Decay**

   * Caps negative theta you’re willing to carry per spread per day
   * GUI field: `Max Theta Per Day ($)`
2. **Max Vega Exposure**

   * Limits how much vega you take on, especially important in earnings season
   * GUI field: `Max Vega Exposure`
3. **Max Gamma Risk**

   * Prevents overly “pin-risky” positions
   * GUI field: `Max Gamma Exposure`

```gherkin
Feature: Greek-Based Risk Limits
  Scenario: Theta decay constraint
    Given a candidate spread with thetaPerDay = $15
    When MaxThetaPerDay = 10
    Then the spread is rejected
  Scenario: Vega filter
    Given a candidate spread with vega = 0.5 per contract
    When MaxVegaExposure = 0.4
    Then the spread is rejected
```

---

## 4. Probability & Expected-Move Metrics

1. **Min Probability of Profit (POP)**

   * Use IBKR’s `modelGreeks` popAvailable flag or calculate via Black-Scholes
   * GUI field: `Min Probability of Profit (%)`
2. **Expected Move Filter**

   * Compare strike width to one-week expected move; avoid overextended strikes
   * GUI field: `Max Spread Width vs. Expected Move (%)`

```gherkin
Feature: Probability-Based Selection
  Scenario: Enforce minimum POP
    Given a spread with modelPop = 62%
    When MinPOP = 65
    Then the spread is excluded
  Scenario: Respect expected-move
    Given underlying’s 30-day expected move = $5
      And a 2-strike spread width = $8
    When MaxWidthVsMovePct = 150
    Then spread width $8 is allowed
```

---

## 5. Event & Calendar Controls

1. **Earnings & Dividend Avoidance**

   * Block trades within `N` days of an earnings report or ex-dividend date
   * GUI fields: `Days Before Earnings to Skip`, `Days Before Ex-Div to Skip`
2. **Custom DTE Logic**

   * Instead of fixed 30–45 DTE, allow dynamic bands based on ATR or trade duration
   * GUI field: `DTE = f(ATR)` toggle + coefficient slider

```gherkin
Feature: Event Filters
  Scenario: Skip earnings week
    Given next earnings for TSLA is in 3 days
    When EarningsSkipDays = 5
    Then TSLA spreads are not offered
```

---

## 6. Strike-Selection Flexibility

1. **Strike Offset**

   * Choose “n strikes” OTM instead of closest OTM
   * GUI field: `Strike Offset (# of strikes)`
2. **Spread Width Selector**

   * Decide how many strikes wide you want your vertical (1-strike, 2-strike, etc.)
   * GUI field: `Spread Width (strikes)`

```gherkin
Feature: Strike Selection
  Scenario: 2-strike wide vertical
    Given available call strikes at [100, 105, 110, 115]
    And StrikeOffset = 1, SpreadWidth = 2
    When building long call spread
    Then buy 105, sell 115
```

---

## Putting It All Together

1. **Extend your `OptionsConfig`** in `models.ts` with these new fields.
2. **Update your OptionSelector.filter\_spreads(…)** to enforce the new constraints.
3. **Add corresponding form inputs** in your Wails GUI under the “Options” tab.
4. **Write the Gherkin scenarios** above as automated E2E tests against your Docker-Kind cluster.

With these six dimensions—**liquidity**, **volatility**, **Greeks**, **probability**, **events**, and **strike control**—you’ll turn your simple vertical-spread picker into a **precision instrument** built for real-world swing trading dynamics.
