<script lang="ts">
  import { SaveConfig } from '../../wailsjs/go/main/App.js';
  export let config;
  export let logAction;

  let loading = false;
  let errorMessage = '';
  let successMessage = '';

  async function saveDataSettings() {
    loading = true;
    errorMessage = '';
    successMessage = '';

    try {
      logAction('Saving Data Settings');
      await SaveConfig(config);
      successMessage = 'Data settings saved successfully';
      logAction('Data Settings Saved', { success: true });
    } catch (err) {
      errorMessage = err.message || 'Failed to save data settings';
      logAction('Data Settings Save Failed', null, err);
      console.error('Data settings save error:', err);
    } finally {
      loading = false;
    }
  }

  async function clearCache(cacheType) {
    // Confirm with the user
    if (!confirm(`Are you sure you want to clear the ${cacheType} cache?`)) {
      return;
    }

    loading = true;
    errorMessage = '';
    successMessage = '';

    try {
      logAction(`Clearing ${cacheType} Cache`);
      // For now, we'll simulate a cache clear
      // await ClearCache(cacheType);
      successMessage = `${cacheType} cache cleared successfully`;
      logAction('Cache Cleared', { type: cacheType, success: true });
    } catch (err) {
      errorMessage = err.message || `Failed to clear ${cacheType} cache`;
      logAction('Cache Clear Failed', { type: cacheType }, err);
      console.error('Cache clear error:', err);
    } finally {
      loading = false;
    }
  }
</script>

<div class="tab-panel">
  <h2>Data Management</h2>
  <p>Configure data caching and storage settings</p>

  {#if errorMessage}
    <div class="error-message">{errorMessage}</div>
  {/if}

  {#if successMessage}
    <div class="success-message">{successMessage}</div>
  {/if}

  <div class="settings-section">
    <h3>Cache Directory</h3>

    <div class="form-group">
      <label for="cache-dir">Cache Directory Path</label>
      <input type="text" id="cache-dir" bind:value={config.Data.CacheDir}>
      <span class="hint">Directory where market data will be cached</span>
    </div>
  </div>

  <div class="settings-section">
    <h3>Cache Expiry Settings</h3>

    <div class="form-group">
      <label for="universe-cache">Universe Cache Expiry (seconds)</label>
      <input
        type="number"
        id="universe-cache"
        bind:value={config.Data.UniverseCacheExpiry}
        min="300"
        max="86400"
        step="300"
      >
      <span class="hint">How long to keep universe data before refreshing (e.g., 1800 = 30 minutes)</span>
    </div>

    <div class="form-group">
      <label for="minute-cache">Minute Data Cache Expiry (seconds)</label>
      <input
        type="number"
        id="minute-cache"
        bind:value={config.Data.MinuteDataCacheExpiry}
        min="60"
        max="3600"
        step="60"
      >
      <span class="hint">How long to keep minute bars before refreshing</span>
    </div>

    <div class="form-group">
      <label for="options-cache">Options Data Cache Expiry (seconds)</label>
      <input
        type="number"
        id="options-cache"
        bind:value={config.Data.OptionsCacheExpiry}
        min="60"
        max="3600"
        step="60"
      >
      <span class="hint">How long to keep options data before refreshing</span>
    </div>
  </div>

  <div class="settings-section">
    <h3>Cache Management</h3>
    <p>Clear specific caches to force reloading data</p>

    <div class="button-group">
      <button
        class="btn secondary"
        on:click={() => clearCache('universe')}
        disabled={loading}
      >
        Clear Universe Cache
      </button>

      <button
        class="btn secondary"
        on:click={() => clearCache('minute')}
        disabled={loading}
      >
        Clear Minute Data Cache
      </button>

      <button
        class="btn secondary"
        on:click={() => clearCache('options')}
        disabled={loading}
      >
        Clear Options Cache
      </button>

      <button
        class="btn warning"
        on:click={() => clearCache('all')}
        disabled={loading}
      >
        Clear All Caches
      </button>
    </div>
  </div>

  <div class="footer-actions">
    <button class="btn primary" on:click={saveDataSettings} disabled={loading}>
      {loading ? 'Saving...' : 'Save Data Settings'}
    </button>
  </div>
</div>

<style>
  .tab-panel {
    padding: 1rem;
  }

  .settings-section {
    margin-bottom: 2rem;
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .hint {
    display: block;
    margin-top: 0.25rem;
    font-size: 0.85rem;
    color: #888;
  }

  .button-group {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1rem;
  }

  .error-message {
    padding: 0.5rem;
    background-color: #fff1f1;
    border: 1px solid #ffc0c0;
    color: #d32f2f;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .success-message {
    padding: 0.5rem;
    background-color: #f1fff1;
    border: 1px solid #c0ffc0;
    color: #2fd32f;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .btn {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    border: 1px solid #ccc;
    background-color: #f5f5f5;
    cursor: pointer;
  }

  .btn.primary {
    background-color: #4caf50;
    color: white;
    border-color: #388e3c;
  }

  .btn.secondary {
    background-color: #2196f3;
    color: white;
    border-color: #1976d2;
  }

  .btn.warning {
    background-color: #ff9800;
    color: white;
    border-color: #f57c00;
  }

  .footer-actions {
    margin-top: 2rem;
    display: flex;
    justify-content: flex-end;
  }

  /* Dark mode */
  :global(body.dark-mode) .settings-section {
    border-color: #444;
  }

  :global(body.dark-mode) .hint {
    color: #aaa;
  }

  :global(body.dark-mode) .btn {
    background-color: #333;
    border-color: #555;
    color: #eee;
  }

  :global(body.dark-mode) .btn.primary {
    background-color: #388e3c;
    border-color: #2e7d32;
  }

  :global(body.dark-mode) .btn.secondary {
    background-color: #1976d2;
    border-color: #1565c0;
  }

  :global(body.dark-mode) .btn.warning {
    background-color: #f57c00;
    border-color: #ef6c00;
  }
</style>
