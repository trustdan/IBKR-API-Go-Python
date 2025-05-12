<script lang="ts">
  import DynamicForm from './common/DynamicForm.svelte';
  import { configStore, schema, updateConfig } from '../store/config';
  import { status } from '../store/status';

  // Handler for form changes
  function handleFormChange(event: CustomEvent) {
    const { path, value } = event.detail;
    updateConfig(path, value);
  }

  // Test connection with current settings
  async function testConnection() {
    try {
      const result = await window.go.main.App.TestConnection();
      if (result) {
        alert('Connection successful!');
      } else {
        alert('Connection failed. Please check your settings.');
      }
    } catch (error: any) {
      alert(`Error: ${error.message}`);
    }
  }
</script>

<div class="connection-tab">
  <h2>IBKR Connection Settings</h2>

  <div class="connection-status">
    <div class="status-indicator {$status.ibkrConnected ? 'connected' : 'disconnected'}">
      {$status.ibkrConnected ? 'Connected' : 'Disconnected'}
    </div>
    {#if $status.ibkrError}
      <div class="error-message">{$status.ibkrError}</div>
    {/if}
  </div>

  {#if $schema && $configStore}
    <div class="form-container">
      <DynamicForm
        schema={$schema.properties?.ibkr || {}}
        data={$configStore.ibkr || {}}
        parentPath="ibkr"
        on:change={handleFormChange}
      />

      <div class="actions">
        <button class="test-btn" on:click={testConnection}>Test Connection</button>
      </div>
    </div>
  {:else}
    <div class="loading">Loading settings...</div>
  {/if}
</div>

<style>
  .connection-tab {
    padding: 20px;
  }

  h2 {
    margin-top: 0;
    margin-bottom: 20px;
    color: #2c3e50;
  }

  .connection-status {
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .status-indicator {
    padding: 5px 10px;
    border-radius: 4px;
    font-weight: bold;
  }

  .connected {
    background-color: #4caf50;
    color: white;
  }

  .disconnected {
    background-color: #f44336;
    color: white;
  }

  .error-message {
    color: #f44336;
  }

  .form-container {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .actions {
    margin-top: 20px;
    text-align: right;
  }

  .test-btn {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    cursor: pointer;
    font-weight: 500;
  }

  .test-btn:hover {
    background-color: #2980b9;
  }

  .loading {
    color: #666;
    font-style: italic;
  }
</style>
