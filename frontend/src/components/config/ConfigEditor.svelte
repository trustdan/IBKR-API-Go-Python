<script lang="ts">
  import { onMount } from 'svelte';
  import { GetConfig, UpdateConfig, IsConfigLoaded } from '../../../wailsjs/go/main/App';
  import type { Configuration } from '../../../wailsjs/go/models';

  let config: Configuration | null = null;
  let isLoading = true;
  let errorMessage = '';
  let successMessage = '';

  onMount(async () => {
    try {
      const configLoaded = await IsConfigLoaded();
      if (configLoaded) {
        config = await GetConfig();
      } else {
        errorMessage = 'Configuration not loaded. Please check the config file exists.';
      }
    } catch (error) {
      errorMessage = `Error loading configuration: ${error}`;
    } finally {
      isLoading = false;
    }
  });

  async function saveConfig() {
    if (!config) return;

    try {
      successMessage = '';
      errorMessage = '';
      await UpdateConfig(config);
      successMessage = 'Configuration saved successfully!';

      // Clear success message after 3 seconds
      setTimeout(() => {
        successMessage = '';
      }, 3000);
    } catch (error) {
      errorMessage = `Error saving configuration: ${error}`;
    }
  }
</script>

<div class="config-editor">
  <h2>Configuration Editor</h2>

  {#if isLoading}
    <div class="loading">
      <p>Loading configuration...</p>
    </div>
  {:else if errorMessage}
    <div class="error">
      <p>{errorMessage}</p>
      <button on:click={() => errorMessage = ''}>Dismiss</button>
    </div>
  {:else if !config}
    <div class="error">
      <p>No configuration loaded.</p>
    </div>
  {:else}
    {#if successMessage}
      <div class="success">
        <p>{successMessage}</p>
      </div>
    {/if}

    <div class="form-section">
      <h3>General Settings</h3>
      <div class="form-group">
        <label for="log-level">Log Level</label>
        <select id="log-level" bind:value={config.General.LogLevel}>
          <option value="DEBUG">DEBUG</option>
          <option value="INFO">INFO</option>
          <option value="WARNING">WARNING</option>
          <option value="ERROR">ERROR</option>
          <option value="CRITICAL">CRITICAL</option>
        </select>
      </div>
    </div>

    <div class="form-section">
      <h3>IBKR Connection</h3>
      <div class="form-group">
        <label for="ibkr-host">Host</label>
        <input type="text" id="ibkr-host" bind:value={config.IBKRConnection.Host} />
      </div>
      <div class="form-group">
        <label for="ibkr-port">Port</label>
        <input type="number" id="ibkr-port" bind:value={config.IBKRConnection.Port} />
      </div>
      <div class="form-group">
        <label for="ibkr-client-id-trading">Client ID (Trading)</label>
        <input type="number" id="ibkr-client-id-trading" bind:value={config.IBKRConnection.ClientIDTrading} />
      </div>
      <div class="form-group">
        <label for="ibkr-client-id-data">Client ID (Data)</label>
        <input type="number" id="ibkr-client-id-data" bind:value={config.IBKRConnection.ClientIDData} />
      </div>
      <div class="form-group">
        <label for="ibkr-account-code">Account Code</label>
        <input type="text" id="ibkr-account-code" bind:value={config.IBKRConnection.AccountCode} />
      </div>
      <div class="form-group">
        <label for="ibkr-read-only">Read-Only API</label>
        <input type="checkbox" id="ibkr-read-only" bind:checked={config.IBKRConnection.ReadOnlyAPI} />
      </div>
    </div>

    <div class="form-section">
      <h3>Trading Parameters</h3>
      <div class="form-group">
        <label for="max-positions">Max Concurrent Positions</label>
        <input type="number" id="max-positions" bind:value={config.TradingParameters.GlobalMaxConcurrentPositions} />
      </div>
      <div class="form-group">
        <label for="risk-percentage">Risk Per Trade (%)</label>
        <input type="number" step="0.1" id="risk-percentage" bind:value={config.TradingParameters.DefaultRiskPerTradePercentage} />
      </div>
      <div class="form-group">
        <label for="stop-loss-percentage">Emergency Stop Loss (%)</label>
        <input type="number" step="0.1" id="stop-loss-percentage" bind:value={config.TradingParameters.EmergencyStopLossPercentage} />
      </div>
    </div>

    <!-- Strategy section would be more complex and likely need a dynamic form component -->
    <!-- This is just a placeholder example -->
    <div class="form-section">
      <h3>Strategy Parameters</h3>
      <p>Strategy configuration would be rendered here</p>
    </div>

    <div class="form-actions">
      <button class="btn-save" on:click={saveConfig}>Save Configuration</button>
      <button class="btn-reset" on:click={() => window.location.reload()}>Reset</button>
    </div>
  {/if}
</div>

<style>
  .config-editor {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }

  h2 {
    color: #333;
    margin-bottom: 20px;
  }

  h3 {
    color: #555;
    margin-top: 30px;
    margin-bottom: 15px;
    border-bottom: 1px solid #eee;
    padding-bottom: 8px;
  }

  .form-section {
    margin-bottom: 30px;
  }

  .form-group {
    margin-bottom: 15px;
    display: flex;
    flex-direction: column;
  }

  label {
    margin-bottom: 5px;
    font-weight: bold;
    color: #555;
  }

  input[type="text"],
  input[type="number"],
  select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    width: 100%;
    max-width: 400px;
  }

  input[type="checkbox"] {
    width: auto;
  }

  .error {
    background-color: #ffebee;
    color: #c62828;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 20px;
  }

  .success {
    background-color: #e8f5e9;
    color: #2e7d32;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 20px;
  }

  .loading {
    font-style: italic;
    color: #666;
  }

  .form-actions {
    margin-top: 30px;
    display: flex;
    gap: 10px;
  }

  button {
    padding: 10px 15px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    transition: background-color 0.2s;
  }

  .btn-save {
    background-color: #1976d2;
    color: white;
  }

  .btn-save:hover {
    background-color: #1565c0;
  }

  .btn-reset {
    background-color: #f5f5f5;
    color: #333;
  }

  .btn-reset:hover {
    background-color: #e0e0e0;
  }
</style>
