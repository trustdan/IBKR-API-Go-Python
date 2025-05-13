<script lang="ts">
  import { onMount } from 'svelte';
  import DynamicForm from '../components/DynamicForm.svelte';
  import { currentConfig as configStore, saveConfig } from '../stores/configStore';
  import { schemaStore } from '../stores/schemaStore';

  let saving = false;
  let saveMessage = '';
  let saveError = '';

  // Function to handle form submission
  async function handleSave() {
    if (!$configStore) return;

    saving = true;
    saveMessage = '';
    saveError = '';

    try {
      const success = await saveConfig($configStore);
      if (success) {
        saveMessage = 'Trading & Risk settings saved successfully!';
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

<div class="trading-risk-tab">
  <header>
    <h1>Trading & Risk Management</h1>
    <p>Configure global trading parameters and risk management settings.</p>
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

  {#if $configStore && $schemaStore}
    <form on:submit|preventDefault={handleSave}>
      <div class="form-sections">
        <!-- Trading Parameters Section -->
        <section class="form-section">
          <h2>Global Trading Parameters</h2>
          <p>Configure global position limits and risk allocation.</p>

          {#if $schemaStore.properties?.TradingParameters}
            <DynamicForm
              schema={$schemaStore.properties.TradingParameters}
              data={$configStore.TradingParameters}
              path="TradingParameters"
            />
          {:else}
            <div class="schema-missing">Schema definition for TradingParameters not found.</div>
          {/if}
        </section>

        <!-- Trading Schedule Section -->
        <section class="form-section">
          <h2>Trading Schedule</h2>
          <p>Set when trading is allowed to occur.</p>

          {#if $schemaStore.properties?.Schedule}
            <DynamicForm
              schema={$schemaStore.properties.Schedule}
              data={$configStore.Schedule}
              path="Schedule"
            />
          {:else}
            <div class="schema-missing">Schema definition for Schedule not found.</div>
          {/if}
        </section>

        <!-- Risk Statistics Dashboard (Placeholder) -->
        <section class="form-section risk-dashboard">
          <h2>Risk Dashboard</h2>
          <p>Overview of current risk exposure and position statistics.</p>

          <div class="risk-grid">
            <div class="risk-card">
              <div class="risk-value">0/10</div>
              <div class="risk-label">Positions Used</div>
            </div>

            <div class="risk-card">
              <div class="risk-value">0%</div>
              <div class="risk-label">Capital Allocated</div>
            </div>

            <div class="risk-card">
              <div class="risk-value">1.0%</div>
              <div class="risk-label">Per-Trade Risk</div>
            </div>

            <div class="risk-card">
              <div class="risk-value">0%</div>
              <div class="risk-label">Portfolio Delta</div>
            </div>
          </div>

          <div class="dashboard-placeholder">
            <div class="placeholder-text">Advanced risk analytics coming in future update</div>
          </div>
        </section>
      </div>

      <div class="form-actions">
        <button type="submit" class="btn btn-primary" disabled={saving}>
          {saving ? 'Saving...' : 'Save Trading & Risk Settings'}
        </button>
      </div>
    </form>
  {:else}
    <div class="loading">Loading trading & risk settings...</div>
  {/if}
</div>

<style>
  .trading-risk-tab {
    padding: 1rem;
    max-width: 1000px;
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
    margin: 0 0 1rem 0;
    color: #1e293b;
  }

  p {
    color: #64748b;
    margin: 0 0 1rem 0;
  }

  .form-sections {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    margin-bottom: 2rem;
  }

  .form-section {
    padding: 1.5rem;
    background-color: #f8fafc;
    border-radius: 0.5rem;
    border: 1px solid #e2e8f0;
  }

  .risk-dashboard {
    background-color: #f1f5f9;
  }

  .risk-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .risk-card {
    background-color: white;
    padding: 1rem;
    border-radius: 0.375rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    text-align: center;
  }

  .risk-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.25rem;
  }

  .risk-label {
    font-size: 0.875rem;
    color: #64748b;
  }

  .dashboard-placeholder {
    height: 120px;
    border: 1px dashed #cbd5e1;
    border-radius: 0.375rem;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #ffffff;
  }

  .placeholder-text {
    color: #94a3b8;
    font-style: italic;
  }

  .schema-missing {
    padding: 1rem;
    color: #dc2626;
    background-color: #fef2f2;
    border-radius: 0.375rem;
    border: 1px solid #fecaca;
  }

  .form-actions {
    margin-top: 2rem;
    display: flex;
    justify-content: flex-start;
  }

  .btn {
    padding: 0.75rem 1.5rem;
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

  .alert {
    padding: 0.75rem 1rem;
    margin-bottom: 1.5rem;
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

  .loading {
    padding: 2rem;
    text-align: center;
    color: #64748b;
    font-style: italic;
  }
</style>
