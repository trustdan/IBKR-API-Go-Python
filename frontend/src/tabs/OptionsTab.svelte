<script lang="ts">
  import { onMount } from 'svelte';
  import { currentConfig, updateConfig, saveConfig } from '../stores/configStore';
  import DynamicForm from '../components/DynamicForm.svelte';

  let loading = false;
  let saveSuccess = false;
  let saveError = null;
  let confirmSave = false;
  let config = {};

  // Options filters params
  let optionsFilters = {
    // Liquidity
    MinOpenInterest: 500,
    MaxBidAskSpreadPercentage: 0.6,
    // Volatility
    UseIVRankFilter: true,
    MinIVRank: 25.0,
    MaxIVRank: 75.0,
    UseIVSkewFilter: false,
    MinPutCallIVSkewPercentage: -10.0,
    MaxPutCallIVSkewPercentage: 20.0,
    // Probability & Risk/Reward
    UsePOPFilter: true,
    MinProbabilityOfProfitPercentage: 55.0,
    UseWidthVsExpectedMoveFilter: true,
    MaxSpreadWidthVsExpectedMovePercentage: 120.0
  };

  // Greek limits params
  let greekLimits = {
    UseGreekLimits: true,
    MaxAbsPositionDelta: 0.50,
    MaxAbsPositionGamma: 0.05,
    MaxAbsPositionVega: 10.0,
    MinPositionTheta: 0.10
  };

  // Trade timing params
  let tradeTiming = {
    // Dynamic DTE Calculation
    UseDynamicDTE: true,
    TargetDTEMode: "ATR_MULTIPLE",
    DTEAtrPeriod: 14,
    DTEAtrCoefficient: 1.2,
    FixedTargetDTE: 45,
    MinDTE: 7,
    MaxDTE: 90,
    // Event Avoidance
    AvoidEarningsDaysBefore: 3,
    AvoidEarningsDaysAfter: 1,
    AvoidExDividendDaysBefore: 2
  };

  const dteOptions = [
    { value: "FIXED", label: "Fixed DTE" },
    { value: "ATR_MULTIPLE", label: "ATR Multiple" },
    { value: "VOLATILITY_INDEX", label: "Volatility Index" }
  ];

  onMount(() => {
    if ($currentConfig) {
      config = $currentConfig;

      // Load options filters
      if ($currentConfig.OptionsFilters) {
        optionsFilters = { ...$currentConfig.OptionsFilters };
      }

      // Load greek limits
      if ($currentConfig.GreekLimits) {
        greekLimits = { ...$currentConfig.GreekLimits };
      }

      // Load trade timing
      if ($currentConfig.TradeTiming) {
        tradeTiming = { ...$currentConfig.TradeTiming };
      }
    }
  });

  function updateOptionsConfig() {
    const updatedConfig = {
      ...$currentConfig,
      OptionsFilters: optionsFilters,
      GreekLimits: greekLimits,
      TradeTiming: tradeTiming
    };
    updateConfig(updatedConfig);
  }

  async function handleSave() {
    loading = true;
    saveSuccess = false;
    saveError = null;

    try {
      await saveConfig(); // Save without restarting
      saveSuccess = true;
      setTimeout(() => (saveSuccess = false), 3000);
    } catch (err) {
      saveError = err.message;
    } finally {
      loading = false;
      confirmSave = false;
    }
  }

  // Handle boolean toggle
  function handleToggle(section, field) {
    if (section === 'optionsFilters') {
      optionsFilters[field] = !optionsFilters[field];
    } else if (section === 'greekLimits') {
      greekLimits[field] = !greekLimits[field];
    } else if (section === 'tradeTiming') {
      tradeTiming[field] = !tradeTiming[field];
    }
    updateOptionsConfig();
  }

  // Handle numeric input change
  function handleNumericChange(section, field, value, isFloat = false) {
    const numValue = isFloat ? parseFloat(value) : parseInt(value);

    if (section === 'optionsFilters') {
      optionsFilters[field] = numValue;
    } else if (section === 'greekLimits') {
      greekLimits[field] = numValue;
    } else if (section === 'tradeTiming') {
      tradeTiming[field] = numValue;
    }
    updateOptionsConfig();
  }

  // Handle select change
  function handleSelectChange(field, value) {
    tradeTiming[field] = value;
    updateOptionsConfig();
  }
</script>

<div class="options-tab">
  <header>
    <h1>Options Trading Configuration</h1>
    <p>Configure advanced options trading parameters, including filters, Greek limits, and trade timing.</p>
  </header>

  {#if saveSuccess}
    <div class="alert alert-success">
      Configuration saved successfully!
    </div>
  {/if}

  {#if saveError}
    <div class="alert alert-error">
      <p>{saveError}</p>
      <button class="alert-dismiss" on:click={() => saveError = null}>×</button>
    </div>
  {/if}

  <div class="card mb-4">
    <div class="card-header">
      <h3>Options Contract Filters</h3>
    </div>
    <div class="card-content">
      <!-- Liquidity Filters -->
      <div class="section-group mb-4">
        <h4>Liquidity Filters</h4>

        <div class="form-row">
          <div class="form-group col-md-6">
            <label for="minOpenInterest">Minimum Open Interest</label>
            <input
              type="number"
              id="minOpenInterest"
              class="form-control"
              min="0"
              step="10"
              value={optionsFilters.MinOpenInterest}
              on:change={(e) => handleNumericChange('optionsFilters', 'MinOpenInterest', e.target.value)}
            />
            <small class="form-text text-muted">Minimum number of open contracts</small>
          </div>
          <div class="form-group col-md-6">
            <label for="maxBidAskSpread">Maximum Bid-Ask Spread (%)</label>
            <input
              type="number"
              id="maxBidAskSpread"
              class="form-control"
              min="0"
              max="5"
              step="0.1"
              value={optionsFilters.MaxBidAskSpreadPercentage}
              on:change={(e) => handleNumericChange('optionsFilters', 'MaxBidAskSpreadPercentage', e.target.value, true)}
            />
            <small class="form-text text-muted">As percentage of mark price</small>
          </div>
        </div>
      </div>

      <!-- Volatility Filters -->
      <div class="section-group mb-4">
        <h4>Volatility Filters</h4>

        <div class="form-group">
          <div class="custom-control custom-switch">
            <input
              type="checkbox"
              class="custom-control-input"
              id="useIVRankFilter"
              checked={optionsFilters.UseIVRankFilter}
              on:change={() => handleToggle('optionsFilters', 'UseIVRankFilter')}
            />
            <label class="custom-control-label" for="useIVRankFilter">Filter by IV Rank</label>
          </div>
        </div>

        <div class="form-row mb-3">
          <div class="form-group col-md-6">
            <label for="minIVRank">Minimum IV Rank (%)</label>
            <input
              type="number"
              id="minIVRank"
              class="form-control"
              min="0"
              max="100"
              step="1"
              value={optionsFilters.MinIVRank}
              on:change={(e) => handleNumericChange('optionsFilters', 'MinIVRank', e.target.value, true)}
              disabled={!optionsFilters.UseIVRankFilter}
            />
          </div>
          <div class="form-group col-md-6">
            <label for="maxIVRank">Maximum IV Rank (%)</label>
            <input
              type="number"
              id="maxIVRank"
              class="form-control"
              min="0"
              max="100"
              step="1"
              value={optionsFilters.MaxIVRank}
              on:change={(e) => handleNumericChange('optionsFilters', 'MaxIVRank', e.target.value, true)}
              disabled={!optionsFilters.UseIVRankFilter}
            />
          </div>
        </div>

        <div class="form-group">
          <div class="custom-control custom-switch">
            <input
              type="checkbox"
              class="custom-control-input"
              id="useIVSkewFilter"
              checked={optionsFilters.UseIVSkewFilter}
              on:change={() => handleToggle('optionsFilters', 'UseIVSkewFilter')}
            />
            <label class="custom-control-label" for="useIVSkewFilter">Filter by IV Skew</label>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group col-md-6">
            <label for="minIVSkew">Minimum Put-Call IV Skew (%)</label>
            <input
              type="number"
              id="minIVSkew"
              class="form-control"
              min="-50"
              max="100"
              step="1"
              value={optionsFilters.MinPutCallIVSkewPercentage}
              on:change={(e) => handleNumericChange('optionsFilters', 'MinPutCallIVSkewPercentage', e.target.value, true)}
              disabled={!optionsFilters.UseIVSkewFilter}
            />
          </div>
          <div class="form-group col-md-6">
            <label for="maxIVSkew">Maximum Put-Call IV Skew (%)</label>
            <input
              type="number"
              id="maxIVSkew"
              class="form-control"
              min="-50"
              max="100"
              step="1"
              value={optionsFilters.MaxPutCallIVSkewPercentage}
              on:change={(e) => handleNumericChange('optionsFilters', 'MaxPutCallIVSkewPercentage', e.target.value, true)}
              disabled={!optionsFilters.UseIVSkewFilter}
            />
          </div>
        </div>
      </div>

      <!-- Probability Filters -->
      <div class="section-group">
        <h4>Probability & Risk/Reward Filters</h4>

        <div class="form-group">
          <div class="custom-control custom-switch">
            <input
              type="checkbox"
              class="custom-control-input"
              id="usePOPFilter"
              checked={optionsFilters.UsePOPFilter}
              on:change={() => handleToggle('optionsFilters', 'UsePOPFilter')}
            />
            <label class="custom-control-label" for="usePOPFilter">Filter by Probability of Profit</label>
          </div>
        </div>

        <div class="form-row mb-3">
          <div class="form-group col-md-6">
            <label for="minPOP">Minimum Probability of Profit (%)</label>
            <input
              type="number"
              id="minPOP"
              class="form-control"
              min="0"
              max="100"
              step="1"
              value={optionsFilters.MinProbabilityOfProfitPercentage}
              on:change={(e) => handleNumericChange('optionsFilters', 'MinProbabilityOfProfitPercentage', e.target.value, true)}
              disabled={!optionsFilters.UsePOPFilter}
            />
          </div>
        </div>

        <div class="form-group">
          <div class="custom-control custom-switch">
            <input
              type="checkbox"
              class="custom-control-input"
              id="useWidthFilter"
              checked={optionsFilters.UseWidthVsExpectedMoveFilter}
              on:change={() => handleToggle('optionsFilters', 'UseWidthVsExpectedMoveFilter')}
            />
            <label class="custom-control-label" for="useWidthFilter">Filter by Spread Width vs. Expected Move</label>
          </div>
        </div>

        <div class="form-group">
          <label for="maxWidthVsMove">Maximum Spread Width as % of Expected Move</label>
          <input
            type="number"
            id="maxWidthVsMove"
            class="form-control"
            min="0"
            max="300"
            step="5"
            value={optionsFilters.MaxSpreadWidthVsExpectedMovePercentage}
            on:change={(e) => handleNumericChange('optionsFilters', 'MaxSpreadWidthVsExpectedMovePercentage', e.target.value, true)}
            disabled={!optionsFilters.UseWidthVsExpectedMoveFilter}
          />
        </div>
      </div>
    </div>
  </div>

  <!-- Greek Limits Section -->
  <div class="card mb-4">
    <div class="card-header">
      <h3>Greek Limits</h3>
    </div>
    <div class="card-content">
      <div class="form-group">
        <div class="custom-control custom-switch">
          <input
            type="checkbox"
            class="custom-control-input"
            id="useGreekLimits"
            checked={greekLimits.UseGreekLimits}
            on:change={() => handleToggle('greekLimits', 'UseGreekLimits')}
          />
          <label class="custom-control-label" for="useGreekLimits">Apply Greek Limits to Positions</label>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group col-md-6">
          <label for="maxDelta">Maximum Absolute Delta Exposure</label>
          <input
            type="number"
            id="maxDelta"
            class="form-control"
            min="0"
            max="1"
            step="0.05"
            value={greekLimits.MaxAbsPositionDelta}
            on:change={(e) => handleNumericChange('greekLimits', 'MaxAbsPositionDelta', e.target.value, true)}
            disabled={!greekLimits.UseGreekLimits}
          />
          <small class="form-text text-muted">Per position (0-1)</small>
        </div>
        <div class="form-group col-md-6">
          <label for="maxGamma">Maximum Absolute Gamma Exposure</label>
          <input
            type="number"
            id="maxGamma"
            class="form-control"
            min="0"
            max="0.2"
            step="0.01"
            value={greekLimits.MaxAbsPositionGamma}
            on:change={(e) => handleNumericChange('greekLimits', 'MaxAbsPositionGamma', e.target.value, true)}
            disabled={!greekLimits.UseGreekLimits}
          />
          <small class="form-text text-muted">Per position (0-0.2)</small>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group col-md-6">
          <label for="maxVega">Maximum Absolute Vega Exposure</label>
          <input
            type="number"
            id="maxVega"
            class="form-control"
            min="0"
            max="50"
            step="1"
            value={greekLimits.MaxAbsPositionVega}
            on:change={(e) => handleNumericChange('greekLimits', 'MaxAbsPositionVega', e.target.value, true)}
            disabled={!greekLimits.UseGreekLimits}
          />
          <small class="form-text text-muted">Per position (0-50)</small>
        </div>
        <div class="form-group col-md-6">
          <label for="minTheta">Minimum Positive Theta Decay</label>
          <input
            type="number"
            id="minTheta"
            class="form-control"
            min="0"
            max="10"
            step="0.05"
            value={greekLimits.MinPositionTheta}
            on:change={(e) => handleNumericChange('greekLimits', 'MinPositionTheta', e.target.value, true)}
            disabled={!greekLimits.UseGreekLimits}
          />
          <small class="form-text text-muted">Per day, per position (0-10)</small>
        </div>
      </div>
    </div>
  </div>

  <!-- Trade Timing Section -->
  <div class="card mb-4">
    <div class="card-header">
      <h3>Trade Timing</h3>
    </div>
    <div class="card-content">
      <!-- DTE Configuration -->
      <div class="section-group mb-4">
        <h4>Days to Expiration (DTE) Configuration</h4>

        <div class="form-group">
          <div class="custom-control custom-switch">
            <input
              type="checkbox"
              class="custom-control-input"
              id="useDynamicDTE"
              checked={tradeTiming.UseDynamicDTE}
              on:change={() => handleToggle('tradeTiming', 'UseDynamicDTE')}
            />
            <label class="custom-control-label" for="useDynamicDTE">Use Dynamic DTE Calculation</label>
          </div>
          <small class="form-text text-muted">Dynamically calculate DTE based on market conditions</small>
        </div>

        <div class="form-group">
          <label for="targetDTEMode">Target DTE Calculation Method</label>
          <select
            id="targetDTEMode"
            class="form-control"
            value={tradeTiming.TargetDTEMode}
            on:change={(e) => handleSelectChange('TargetDTEMode', e.target.value)}
            disabled={!tradeTiming.UseDynamicDTE}
          >
            {#each dteOptions as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
        </div>

        <div class="form-row mb-3">
          <div class="form-group col-md-6">
            <label for="dteAtrPeriod">ATR Period</label>
            <input
              type="number"
              id="dteAtrPeriod"
              class="form-control"
              min="1"
              max="100"
              step="1"
              value={tradeTiming.DTEAtrPeriod}
              on:change={(e) => handleNumericChange('tradeTiming', 'DTEAtrPeriod', e.target.value)}
              disabled={!tradeTiming.UseDynamicDTE || tradeTiming.TargetDTEMode !== "ATR_MULTIPLE"}
            />
          </div>
          <div class="form-group col-md-6">
            <label for="dteAtrCoef">ATR Coefficient</label>
            <input
              type="number"
              id="dteAtrCoef"
              class="form-control"
              min="0.1"
              max="5"
              step="0.1"
              value={tradeTiming.DTEAtrCoefficient}
              on:change={(e) => handleNumericChange('tradeTiming', 'DTEAtrCoefficient', e.target.value, true)}
              disabled={!tradeTiming.UseDynamicDTE || tradeTiming.TargetDTEMode !== "ATR_MULTIPLE"}
            />
          </div>
        </div>

        <div class="form-group">
          <label for="fixedTargetDTE">Fixed Target DTE</label>
          <input
            type="number"
            id="fixedTargetDTE"
            class="form-control"
            min="1"
            max="365"
            step="1"
            value={tradeTiming.FixedTargetDTE}
            on:change={(e) => handleNumericChange('tradeTiming', 'FixedTargetDTE', e.target.value)}
            disabled={tradeTiming.UseDynamicDTE}
          />
          <small class="form-text text-muted">Used when dynamic DTE is disabled</small>
        </div>

        <div class="form-row">
          <div class="form-group col-md-6">
            <label for="minDTE">Minimum DTE</label>
            <input
              type="number"
              id="minDTE"
              class="form-control"
              min="0"
              max="365"
              step="1"
              value={tradeTiming.MinDTE}
              on:change={(e) => handleNumericChange('tradeTiming', 'MinDTE', e.target.value)}
            />
          </div>
          <div class="form-group col-md-6">
            <label for="maxDTE">Maximum DTE</label>
            <input
              type="number"
              id="maxDTE"
              class="form-control"
              min="1"
              max="365"
              step="1"
              value={tradeTiming.MaxDTE}
              on:change={(e) => handleNumericChange('tradeTiming', 'MaxDTE', e.target.value)}
            />
          </div>
        </div>
      </div>

      <!-- Event Avoidance -->
      <div class="section-group">
        <h4>Event Avoidance</h4>

        <div class="form-row">
          <div class="form-group col-md-4">
            <label for="avoidEarningsBefore">Days Before Earnings</label>
            <input
              type="number"
              id="avoidEarningsBefore"
              class="form-control"
              min="0"
              max="30"
              step="1"
              value={tradeTiming.AvoidEarningsDaysBefore}
              on:change={(e) => handleNumericChange('tradeTiming', 'AvoidEarningsDaysBefore', e.target.value)}
            />
            <small class="form-text text-muted">Days to avoid before earnings</small>
          </div>
          <div class="form-group col-md-4">
            <label for="avoidEarningsAfter">Days After Earnings</label>
            <input
              type="number"
              id="avoidEarningsAfter"
              class="form-control"
              min="0"
              max="30"
              step="1"
              value={tradeTiming.AvoidEarningsDaysAfter}
              on:change={(e) => handleNumericChange('tradeTiming', 'AvoidEarningsDaysAfter', e.target.value)}
            />
            <small class="form-text text-muted">Days to avoid after earnings</small>
          </div>
          <div class="form-group col-md-4">
            <label for="avoidDividendsBefore">Days Before Ex-Div</label>
            <input
              type="number"
              id="avoidDividendsBefore"
              class="form-control"
              min="0"
              max="30"
              step="1"
              value={tradeTiming.AvoidExDividendDaysBefore}
              on:change={(e) => handleNumericChange('tradeTiming', 'AvoidExDividendDaysBefore', e.target.value)}
            />
            <small class="form-text text-muted">Days to avoid before ex-dividend date</small>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Option Chain Viewer Placeholder -->
  <div class="card mb-4">
    <div class="card-header">
      <h3>Option Chain Viewer</h3>
    </div>
    <div class="card-content">
      <p>
        The Option Chain Viewer will be implemented in the next phase. This feature will allow you to:
      </p>
      <ul>
        <li>View available option contracts for selected symbols</li>
        <li>Filter contracts based on your configured criteria</li>
        <li>Analyze Greeks, probability of profit, and expected returns</li>
        <li>Test different strategies with visual payoff diagrams</li>
      </ul>
      <div class="placeholder-viewer">
        <div class="text-center py-5">
          <span class="muted-text">Option Chain Viewer - Coming Soon</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Save Button -->
  <div class="form-actions">
    {#if confirmSave}
      <div class="alert alert-warning mb-3">
        Are you sure you want to save these changes?
        <div class="mt-2">
          <button class="btn btn-primary" on:click={handleSave} disabled={loading}>
            {loading ? 'Saving...' : 'Yes, Save Changes'}
          </button>
          <button class="btn btn-secondary ml-2" on:click={() => (confirmSave = false)}>
            Cancel
          </button>
        </div>
      </div>
    {:else}
      <button class="btn btn-primary" on:click={() => (confirmSave = true)} disabled={loading}>
        Save Options Configuration
      </button>
    {/if}
  </div>
</div>

<style>
  .options-tab {
    padding: 2rem;
    max-width: 1000px;
    margin: 0 auto;
  }

  header {
    margin-bottom: 2rem;
  }

  h1 {
    font-size: 1.75rem;
    margin-bottom: 0.5rem;
  }

  h3 {
    font-size: 1.25rem;
    margin-bottom: 0;
  }

  h4 {
    font-size: 1.1rem;
    margin-bottom: 1rem;
    color: #4b5563;
  }

  p {
    color: #6b7280;
    margin-bottom: 1.5rem;
  }

  .card {
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    background-color: white;
    overflow: hidden;
  }

  .card-header {
    padding: 1rem 1.5rem;
    background-color: #f9fafb;
    border-bottom: 1px solid #e5e7eb;
  }

  .card-content {
    padding: 1.5rem;
  }

  .mb-4 {
    margin-bottom: 1.5rem;
  }

  .mb-3 {
    margin-bottom: 1rem;
  }

  .form-row {
    display: flex;
    flex-wrap: wrap;
    margin-right: -0.5rem;
    margin-left: -0.5rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .col-md-6 {
    flex: 0 0 50%;
    max-width: 50%;
    padding: 0 0.5rem;
  }

  .col-md-4 {
    flex: 0 0 33.333333%;
    max-width: 33.333333%;
    padding: 0 0.5rem;
  }

  .form-control {
    display: block;
    width: 100%;
    padding: 0.5rem 0.75rem;
    font-size: 1rem;
    line-height: 1.5;
    color: #374151;
    background-color: #fff;
    background-clip: padding-box;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    transition: border-color 0.15s ease-in-out;
  }

  .form-control:focus {
    border-color: #3b82f6;
    outline: 0;
  }

  .form-control:disabled {
    background-color: #f3f4f6;
    opacity: 0.7;
  }

  .custom-control {
    position: relative;
    padding-left: 2.5rem;
    min-height: 1.5rem;
  }

  .custom-control-input {
    position: absolute;
    z-index: -1;
    opacity: 0;
  }

  .custom-control-label {
    position: relative;
    margin-bottom: 0;
    vertical-align: top;
    cursor: pointer;
  }

  .custom-control-label::before {
    position: absolute;
    left: -2.5rem;
    display: block;
    width: 2rem;
    height: 1rem;
    content: "";
    background-color: #d1d5db;
    border-radius: 1rem;
  }

  .custom-control-label::after {
    position: absolute;
    top: 0.25rem;
    left: -2.25rem;
    display: block;
    width: 0.5rem;
    height: 0.5rem;
    content: "";
    background-color: white;
    border-radius: 1rem;
    transition: transform 0.15s ease-in-out;
  }

  .custom-control-input:checked ~ .custom-control-label::before {
    background-color: #3b82f6;
  }

  .custom-control-input:checked ~ .custom-control-label::after {
    transform: translateX(1rem);
  }

  .custom-switch .custom-control-label::before {
    width: 2rem;
    border-radius: 1rem;
  }

  .section-group {
    padding-top: 1.25rem;
    border-top: 1px solid #e5e7eb;
  }

  .section-group:first-child {
    border-top: none;
    padding-top: 0;
  }

  .form-text {
    display: block;
    margin-top: 0.25rem;
    font-size: 0.75rem;
  }

  .text-muted {
    color: #6b7280;
  }

  .placeholder-viewer {
    border: 2px dashed #d1d5db;
    border-radius: 0.375rem;
    margin-top: 1rem;
  }

  .text-center {
    text-align: center;
  }

  .py-5 {
    padding-top: 3rem;
    padding-bottom: 3rem;
  }

  .muted-text {
    color: #9ca3af;
    font-style: italic;
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 1.5rem;
    margin-bottom: 2rem;
  }

  .btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    font-weight: 500;
    line-height: 1.5;
    text-align: center;
    vertical-align: middle;
    cursor: pointer;
    border: 1px solid transparent;
    border-radius: 0.375rem;
    transition: color 0.15s, background-color 0.15s, border-color 0.15s;
  }

  .btn-primary {
    color: #fff;
    background-color: #3b82f6;
    border-color: #3b82f6;
  }

  .btn-primary:hover:not(:disabled) {
    background-color: #2563eb;
    border-color: #2563eb;
  }

  .btn-secondary {
    color: #1f2937;
    background-color: #f3f4f6;
    border-color: #d1d5db;
  }

  .btn-secondary:hover {
    background-color: #e5e7eb;
    border-color: #9ca3af;
  }

  .btn:disabled {
    opacity: 0.65;
    cursor: not-allowed;
  }

  .ml-2 {
    margin-left: 0.5rem;
  }

  .mt-2 {
    margin-top: 0.5rem;
  }

  .alert {
    position: relative;
    padding: 1rem;
    margin-bottom: 1rem;
    border: 1px solid transparent;
    border-radius: 0.375rem;
  }

  .alert-success {
    color: #065f46;
    background-color: #ecfdf5;
    border-color: #a7f3d0;
  }

  .alert-warning {
    color: #92400e;
    background-color: #fffbeb;
    border-color: #fef3c7;
  }

  .alert-error {
    color: #b91c1c;
    background-color: #fef2f2;
    border-color: #fecaca;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .alert-dismiss {
    background: none;
    border: none;
    font-size: 1.25rem;
    cursor: pointer;
    color: inherit;
    line-height: 1;
    padding: 0;
  }
</style>
