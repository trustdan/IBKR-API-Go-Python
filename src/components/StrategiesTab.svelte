<script>
  import { configStore } from '../store/config.js';

  // Open/Close state for collapsible sections
  let openSections = {
    high_base: true,
    low_base: false,
    breakout: false,
    momentum: false
  };

  // Toggle section visibility
  function toggleSection(section) {
    openSections[section] = !openSections[section];
  }
</script>

<div class="tab-container">
  <h2>Trading Strategies</h2>
  <p class="description">Configure parameters for each strategy type. All active strategies will be considered for trading opportunities.</p>

  <!-- High Base Strategy Section -->
  <div class="strategy-section">
    <div class="section-header" on:click={() => toggleSection('high_base')}>
      <h3>High Base Strategy</h3>
      <div class="toggle-icon">{openSections.high_base ? '▼' : '►'}</div>
    </div>

    {#if openSections.high_base}
      <div class="section-content">
        <div class="form-group">
          <label for="high-base-enabled">Enabled</label>
          <input
            type="checkbox"
            id="high-base-enabled"
            bind:checked={$configStore.strategies.high_base.enabled}
          />
        </div>

        <div class="form-group">
          <label for="high-base-min-rsi">Minimum RSI</label>
          <input
            type="range"
            id="high-base-min-rsi"
            min="0"
            max="100"
            step="1"
            bind:value={$configStore.strategies.high_base.min_rsi}
          />
          <span class="value-display">{$configStore.strategies.high_base.min_rsi}</span>
        </div>

        <div class="form-group">
          <label for="high-base-max-atr">Maximum ATR Ratio</label>
          <input
            type="range"
            id="high-base-max-atr"
            min="0.1"
            max="3.0"
            step="0.1"
            bind:value={$configStore.strategies.high_base.max_atr_ratio}
          />
          <span class="value-display">{$configStore.strategies.high_base.max_atr_ratio}</span>
        </div>

        <div class="form-group">
          <label for="high-base-lookback">Lookback Period (days)</label>
          <input
            type="number"
            id="high-base-lookback"
            min="1"
            max="90"
            bind:value={$configStore.strategies.high_base.lookback_days}
          />
        </div>
      </div>
    {/if}
  </div>

  <!-- Low Base Strategy Section -->
  <div class="strategy-section">
    <div class="section-header" on:click={() => toggleSection('low_base')}>
      <h3>Low Base Strategy</h3>
      <div class="toggle-icon">{openSections.low_base ? '▼' : '►'}</div>
    </div>

    {#if openSections.low_base}
      <div class="section-content">
        <div class="form-group">
          <label for="low-base-enabled">Enabled</label>
          <input
            type="checkbox"
            id="low-base-enabled"
            bind:checked={$configStore.strategies.low_base.enabled}
          />
        </div>

        <div class="form-group">
          <label for="low-base-max-rsi">Maximum RSI</label>
          <input
            type="range"
            id="low-base-max-rsi"
            min="0"
            max="100"
            step="1"
            bind:value={$configStore.strategies.low_base.max_rsi}
          />
          <span class="value-display">{$configStore.strategies.low_base.max_rsi}</span>
        </div>

        <div class="form-group">
          <label for="low-base-max-atr">Maximum ATR Ratio</label>
          <input
            type="range"
            id="low-base-max-atr"
            min="0.1"
            max="3.0"
            step="0.1"
            bind:value={$configStore.strategies.low_base.max_atr_ratio}
          />
          <span class="value-display">{$configStore.strategies.low_base.max_atr_ratio}</span>
        </div>

        <div class="form-group">
          <label for="low-base-lookback">Lookback Period (days)</label>
          <input
            type="number"
            id="low-base-lookback"
            min="1"
            max="90"
            bind:value={$configStore.strategies.low_base.lookback_days}
          />
        </div>
      </div>
    {/if}
  </div>

  <!-- Breakout Strategy Section -->
  <div class="strategy-section">
    <div class="section-header" on:click={() => toggleSection('breakout')}>
      <h3>Breakout Strategy</h3>
      <div class="toggle-icon">{openSections.breakout ? '▼' : '►'}</div>
    </div>

    {#if openSections.breakout}
      <div class="section-content">
        <div class="form-group">
          <label for="breakout-enabled">Enabled</label>
          <input
            type="checkbox"
            id="breakout-enabled"
            bind:checked={$configStore.strategies.breakout.enabled}
          />
        </div>

        <div class="form-group">
          <label for="breakout-period">Breakout Period (days)</label>
          <input
            type="range"
            id="breakout-period"
            min="5"
            max="60"
            step="1"
            bind:value={$configStore.strategies.breakout.period_days}
          />
          <span class="value-display">{$configStore.strategies.breakout.period_days}</span>
        </div>

        <div class="form-group">
          <label for="breakout-volume-factor">Volume Factor</label>
          <input
            type="range"
            id="breakout-volume-factor"
            min="1"
            max="5"
            step="0.1"
            bind:value={$configStore.strategies.breakout.volume_factor}
          />
          <span class="value-display">{$configStore.strategies.breakout.volume_factor}x</span>
        </div>

        <div class="form-group">
          <label for="breakout-confirmation">Require Confirmation</label>
          <input
            type="checkbox"
            id="breakout-confirmation"
            bind:checked={$configStore.strategies.breakout.require_confirmation}
          />
        </div>
      </div>
    {/if}
  </div>

  <!-- Momentum Strategy Section -->
  <div class="strategy-section">
    <div class="section-header" on:click={() => toggleSection('momentum')}>
      <h3>Momentum Strategy</h3>
      <div class="toggle-icon">{openSections.momentum ? '▼' : '►'}</div>
    </div>

    {#if openSections.momentum}
      <div class="section-content">
        <div class="form-group">
          <label for="momentum-enabled">Enabled</label>
          <input
            type="checkbox"
            id="momentum-enabled"
            bind:checked={$configStore.strategies.momentum.enabled}
          />
        </div>

        <div class="form-group">
          <label for="momentum-lookback">Lookback Period (days)</label>
          <input
            type="range"
            id="momentum-lookback"
            min="5"
            max="90"
            step="1"
            bind:value={$configStore.strategies.momentum.lookback_days}
          />
          <span class="value-display">{$configStore.strategies.momentum.lookback_days}</span>
        </div>

        <div class="form-group">
          <label for="momentum-threshold">Minimum Return Threshold (%)</label>
          <input
            type="range"
            id="momentum-threshold"
            min="1"
            max="30"
            step="0.5"
            bind:value={$configStore.strategies.momentum.min_return_pct}
          />
          <span class="value-display">{$configStore.strategies.momentum.min_return_pct}%</span>
        </div>

        <div class="form-group">
          <label for="momentum-volume-increase">Minimum Volume Increase (%)</label>
          <input
            type="range"
            id="momentum-volume-increase"
            min="0"
            max="100"
            step="5"
            bind:value={$configStore.strategies.momentum.min_volume_increase_pct}
          />
          <span class="value-display">{$configStore.strategies.momentum.min_volume_increase_pct}%</span>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .tab-container {
    padding: 20px;
  }

  .description {
    margin-bottom: 20px;
    color: #666;
  }

  .strategy-section {
    margin-bottom: 15px;
    border: 1px solid #ddd;
    border-radius: 4px;
    overflow: hidden;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 15px;
    background-color: #f5f5f5;
    cursor: pointer;
    user-select: none;
  }

  .section-header h3 {
    margin: 0;
    font-size: 16px;
  }

  .toggle-icon {
    font-size: 14px;
  }

  .section-content {
    padding: 15px;
    border-top: 1px solid #ddd;
  }

  .form-group {
    margin-bottom: 15px;
    display: flex;
    align-items: center;
  }

  label {
    width: 180px;
    font-weight: 500;
  }

  input[type="range"] {
    flex: 1;
    margin-right: 10px;
  }

  input[type="number"] {
    width: 80px;
    padding: 5px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  input[type="checkbox"] {
    width: 20px;
    height: 20px;
  }

  .value-display {
    width: 60px;
    text-align: right;
  }
</style>
