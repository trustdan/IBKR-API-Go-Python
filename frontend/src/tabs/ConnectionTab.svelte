<script lang="ts">
  import { onMount } from 'svelte';
  import DynamicForm from '../components/DynamicForm.svelte';
  import { currentConfig as configStore, saveConfig } from '../stores/configStore';
  import { schemaStore } from '../stores/schemaStore';
  import { statusStore } from '../stores/statusStore';

  let saving = false;
  let saveMessage = '';
  let saveError = '';

  // Function to test the IBKR connection
  async function testConnection() {
    try {
      // In a real implementation, we'd call a backend function
      // const result = await TestIBKRConnection();

      // For now, just simulate a success/failure based on status
      if ($statusStore.ibkr.connected) {
        saveMessage = 'Connection successful!';
        setTimeout(() => saveMessage = '', 3000);
      } else {
        saveError = 'Connection failed. Please check your settings.';
      }
    } catch (error) {
      saveError = `Connection test failed: ${error}`;
    }
  }

  // Function to handle form submission
  async function handleSave() {
    if (!$configStore) return;

    saving = true;
    saveMessage = '';
    saveError = '';

    try {
      const success = await saveConfig($configStore);
      if (success) {
        saveMessage = 'Connection settings saved successfully!';
        setTimeout(() => saveMessage = '', 3000);
      } else {
        saveError = 'Failed to save settings';
      }
    } catch (error) {
      saveError = `Error saving settings: ${error}`;
    } finally {
      saving = false;
    }
  }
</script>

<div class="connection-tab">
  <header>
    <h1>IBKR Connection</h1>
    <p>Configure your connection to Interactive Brokers Trader Workstation (TWS) or IB Gateway.</p>
  </header>

  {#if saveMessage}
    <div class="alert alert-success">
      {saveMessage}
    </div>
  {/if}

  {#if saveError}
    <div class="alert alert-error">
      <p>{saveError}</p>
      <button class="alert-dismiss" on:click={() => saveError = ''}>×</button>
    </div>
  {/if}

  <div class="connection-status">
    <h2>Connection Status</h2>
    <div class={`status-indicator ${$statusStore.ibkr.connected ? 'connected' : 'disconnected'}`}>
      <span class="status-dot"></span>
      <span class="status-text">{$statusStore.ibkr.connected ? 'Connected' : 'Disconnected'}</span>
    </div>
    {#if $statusStore.ibkr.error}
      <div class="status-error">{$statusStore.ibkr.error}</div>
    {/if}
  </div>

  {#if $configStore && $schemaStore && $schemaStore.properties?.IBKRConnection}
    <form on:submit|preventDefault={handleSave}>
      <DynamicForm
        schema={$schemaStore.properties.IBKRConnection}
        data={$configStore.IBKRConnection}
        path="IBKRConnection"
      />

      <div class="form-actions">
        <button type="submit" class="btn btn-primary" disabled={saving}>
          {saving ? 'Saving...' : 'Save Connection Settings'}
        </button>
        <button type="button" class="btn btn-secondary" on:click={testConnection}>
          Test Connection
        </button>
      </div>
    </form>
  {:else}
    <div class="loading">Loading connection settings...</div>
  {/if}

  <div class="help-section">
    <h3>Connection Help</h3>
    <ul>
      <li><strong>Host:</strong> Usually "localhost" when TWS is running on the same machine.</li>
      <li><strong>Port:</strong> Default ports are 7497 for TWS Paper Trading, 7496 for TWS Live, 4002 for IB Gateway.</li>
      <li><strong>Client ID:</strong> A unique identifier for this connection. Use different IDs for trading and data connections.</li>
      <li><strong>Read-Only API:</strong> Enable to prevent the application from placing trades (for monitoring only).</li>
    </ul>
    <p class="tip">Make sure API connections are enabled in TWS/Gateway settings (File → Global Configuration → API → Settings).</p>
  </div>
</div>

<style>
  .connection-tab {
    padding: 1rem;
    max-width: 800px;
  }

  header {
    margin-bottom: 2rem;
  }

  h1 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    color: #1e293b;
  }

  h2 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 1.5rem 0 1rem 0;
    color: #1e293b;
  }

  h3 {
    font-size: 1.1rem;
    font-weight: 600;
    margin: 1.5rem 0 1rem 0;
    color: #334155;
  }

  p {
    color: #64748b;
    margin: 0 0 1rem 0;
  }

  .connection-status {
    margin-bottom: 2rem;
    padding: 1rem;
    background-color: #f8fafc;
    border-radius: 0.5rem;
    border: 1px solid #e2e8f0;
  }

  .status-indicator {
    display: flex;
    align-items: center;
    margin: 0.5rem 0;
  }

  .status-dot {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 0.5rem;
  }

  .connected .status-dot {
    background-color: #22c55e;
  }

  .disconnected .status-dot {
    background-color: #ef4444;
  }

  .status-text {
    font-weight: 500;
  }

  .connected .status-text {
    color: #22c55e;
  }

  .disconnected .status-text {
    color: #ef4444;
  }

  .status-error {
    color: #ef4444;
    margin-top: 0.5rem;
    font-size: 0.875rem;
  }

  .form-actions {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
  }

  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    font-weight: 500;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: background-color 0.2s, border-color 0.2s;
  }

  .btn-primary {
    background-color: #3b82f6;
    color: white;
    border: 1px solid #3b82f6;
  }

  .btn-primary:hover:not(:disabled) {
    background-color: #2563eb;
    border-color: #2563eb;
  }

  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-secondary {
    background-color: white;
    color: #1e293b;
    border: 1px solid #cbd5e1;
  }

  .btn-secondary:hover {
    background-color: #f8fafc;
    border-color: #94a3b8;
  }

  .alert {
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    border-radius: 0.375rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .alert-success {
    background-color: #ecfdf5;
    color: #065f46;
    border: 1px solid #a7f3d0;
  }

  .alert-error {
    background-color: #fef2f2;
    color: #b91c1c;
    border: 1px solid #fecaca;
  }

  .alert-dismiss {
    background: none;
    border: none;
    font-size: 1.25rem;
    cursor: pointer;
    color: inherit;
    line-height: 1;
  }

  .help-section {
    margin-top: 3rem;
    padding: 1rem;
    background-color: #f8fafc;
    border-radius: 0.5rem;
    border: 1px solid #e2e8f0;
  }

  .help-section ul {
    padding-left: 1.5rem;
    margin: 1rem 0;
  }

  .help-section li {
    margin-bottom: 0.5rem;
    color: #334155;
  }

  .tip {
    font-style: italic;
    color: #64748b;
    margin-top: 1rem;
  }

  .loading {
    padding: 2rem;
    text-align: center;
    color: #64748b;
    font-style: italic;
  }
</style>
