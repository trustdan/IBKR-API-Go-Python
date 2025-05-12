<script lang="ts">
  import DynamicForm from './common/DynamicForm.svelte';
  import { configStore, schema, updateConfig } from '../store/config';

  let selectedSymbol = '';
  let optionsChain: any[] = [];
  let isLoading = false;
  let error = '';

  // Handler for form changes
  function handleFormChange(event: CustomEvent) {
    const { path, value } = event.detail;
    updateConfig(path, value);
  }

  // Fetch options chain for the selected symbol
  async function fetchOptionsChain() {
    if (!selectedSymbol) {
      error = 'Please enter a symbol';
      return;
    }

    error = '';
    isLoading = true;

    try {
      // Assuming the API method is defined in the Wails backend
      optionsChain = await window.go.main.App.FetchOptionChain(selectedSymbol);
    } catch (err: any) {
      error = `Error fetching options chain: ${err.message}`;
      optionsChain = [];
    } finally {
      isLoading = false;
    }
  }

  // Filter options chain based on current settings
  $: filteredOptionsChain = optionsChain.filter(option => {
    if (!$configStore) return true;

    // Apply filters based on current config settings
    const options = $configStore.options;
    const greeks = $configStore.greeks;
    const probability = $configStore.probability;

    if (options.min_open_interest && option.openInterest < options.min_open_interest) {
      return false;
    }

    if (options.max_bid_ask_spread_pct && option.bidAskSpreadPct > options.max_bid_ask_spread_pct) {
      return false;
    }

    if (options.min_iv_rank && option.ivRank < options.min_iv_rank) {
      return false;
    }

    if (options.max_iv_rank && option.ivRank > options.max_iv_rank) {
      return false;
    }

    if (greeks && greeks.max_theta_per_day && Math.abs(option.theta) > greeks.max_theta_per_day) {
      return false;
    }

    if (greeks && greeks.max_vega_exposure && Math.abs(option.vega) > greeks.max_vega_exposure) {
      return false;
    }

    if (greeks && greeks.max_gamma_exposure && Math.abs(option.gamma) > greeks.max_gamma_exposure) {
      return false;
    }

    if (probability && probability.min_pop && option.probabilityOTM < probability.min_pop) {
      return false;
    }

    return true;
  });
</script>

<div class="options-tab">
  <h2>Options Trading Settings</h2>

  {#if $schema && $configStore}
    <div class="options-sections">
      <!-- Options Settings -->
      <section class="options-section">
        <h3>Options Filters</h3>
        <DynamicForm
          schema={$schema.properties?.options || {}}
          data={$configStore.options || {}}
          parentPath="options"
          on:change={handleFormChange}
        />
      </section>

      <!-- Greeks Settings -->
      <section class="options-section">
        <h3>Greek Risk Limits</h3>
        <DynamicForm
          schema={$schema.properties?.greeks || {}}
          data={$configStore.greeks || {}}
          parentPath="greeks"
          on:change={handleFormChange}
        />
      </section>

      <!-- Probability Settings -->
      <section class="options-section">
        <h3>Probability Metrics</h3>
        <DynamicForm
          schema={$schema.properties?.probability || {}}
          data={$configStore.probability || {}}
          parentPath="probability"
          on:change={handleFormChange}
        />
      </section>

      <!-- Events Settings -->
      <section class="options-section">
        <h3>Event Avoidance</h3>
        <DynamicForm
          schema={$schema.properties?.events || {}}
          data={$configStore.events || {}}
          parentPath="events"
          on:change={handleFormChange}
        />
      </section>

      <!-- DTE Settings -->
      <section class="options-section">
        <h3>Dynamic DTE</h3>
        <DynamicForm
          schema={$schema.properties?.dte || {}}
          data={$configStore.dte || {}}
          parentPath="dte"
          on:change={handleFormChange}
        />
      </section>
    </div>

    <!-- Option Chain Viewer -->
    <section class="option-chain-section">
      <h3>Option Chain Viewer</h3>

      <div class="symbol-input">
        <input
          type="text"
          placeholder="Enter symbol (e.g., AAPL)"
          bind:value={selectedSymbol}
        />
        <button on:click={fetchOptionsChain} disabled={isLoading}>
          {isLoading ? 'Loading...' : 'Fetch Options'}
        </button>
      </div>

      {#if error}
        <div class="error-message">{error}</div>
      {/if}

      {#if filteredOptionsChain.length > 0}
        <div class="option-chain-container">
          <table class="option-chain-table">
            <thead>
              <tr>
                <th>Expiry</th>
                <th>Strike</th>
                <th>Type</th>
                <th>Bid</th>
                <th>Ask</th>
                <th>IV</th>
                <th>Delta</th>
                <th>Gamma</th>
                <th>Theta</th>
                <th>Vega</th>
                <th>OI</th>
                <th>POP (%)</th>
              </tr>
            </thead>
            <tbody>
              {#each filteredOptionsChain as option}
                <tr>
                  <td>{option.expiry}</td>
                  <td>{option.strike}</td>
                  <td>{option.type}</td>
                  <td>{option.bid}</td>
                  <td>{option.ask}</td>
                  <td>{option.iv.toFixed(2)}%</td>
                  <td>{option.delta.toFixed(2)}</td>
                  <td>{option.gamma.toFixed(4)}</td>
                  <td>{option.theta.toFixed(2)}</td>
                  <td>{option.vega.toFixed(2)}</td>
                  <td>{option.openInterest}</td>
                  <td>{option.probabilityOTM?.toFixed(1)}%</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {:else if isLoading}
        <div class="loading">Loading options chain...</div>
      {:else if optionsChain.length > 0}
        <div class="no-results">No options match your current filter criteria.</div>
      {/if}
    </section>
  {:else}
    <div class="loading">Loading settings...</div>
  {/if}
</div>

<style>
  .options-tab {
    padding: 20px;
  }

  .options-sections {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
  }

  .options-section {
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 4px;
  }

  h2 {
    margin-bottom: 20px;
  }

  h3 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 1.1rem;
  }

  .option-chain-section {
    margin-top: 30px;
  }

  .symbol-input {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
  }

  .symbol-input input {
    flex: 1;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  .symbol-input button {
    padding: 8px 15px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .symbol-input button:hover {
    background-color: #45a049;
  }

  .symbol-input button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }

  .error-message {
    color: #f44336;
    margin-bottom: 10px;
  }

  .loading, .no-results {
    padding: 15px;
    text-align: center;
    font-style: italic;
    color: #666;
  }

  .option-chain-container {
    overflow-x: auto;
    margin-top: 15px;
  }

  .option-chain-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }

  .option-chain-table th,
  .option-chain-table td {
    padding: 8px;
    text-align: right;
    border-bottom: 1px solid #ddd;
  }

  .option-chain-table th {
    background-color: #f2f2f2;
    font-weight: 500;
  }

  .option-chain-table tr:hover {
    background-color: #f5f5f5;
  }
</style>
