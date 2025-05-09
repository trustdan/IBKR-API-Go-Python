<script lang="ts">
  import { SaveConfig } from '../../wailsjs/go/main/App.js';
  export let config;
  export let logAction;

  let loading = false;
  let errorMessage = '';
  let successMessage = '';

  async function saveScheduleSettings() {
    loading = true;
    errorMessage = '';
    successMessage = '';

    try {
      logAction('Saving Schedule Settings');
      await SaveConfig(config);
      successMessage = 'Schedule settings saved successfully';
      logAction('Schedule Settings Saved', { success: true });
    } catch (err) {
      errorMessage = err.message || 'Failed to save schedule settings';
      logAction('Schedule Settings Save Failed', null, err);
      console.error('Schedule save error:', err);
    } finally {
      loading = false;
    }
  }
</script>

<div class="tab-panel">
  <h2>Trading Schedule</h2>
  <p>Configure the automatic trading schedule for your algorithm</p>

  {#if errorMessage}
    <div class="error-message">{errorMessage}</div>
  {/if}

  {#if successMessage}
    <div class="success-message">{successMessage}</div>
  {/if}

  <div class="settings-section">
    <h3>Automatic Schedule</h3>

    <div class="form-group">
      <label>
        <input type="checkbox" bind:checked={config.Schedule.AutoStartEnabled}>
        Enable Automatic Start
      </label>
    </div>

    <div class="form-group">
      <label for="start-time">Start Time (24h format)</label>
      <input
        type="time"
        id="start-time"
        bind:value={config.Schedule.StartTime}
        disabled={!config.Schedule.AutoStartEnabled}
      >
      <span class="hint">Market time in {config.Schedule.Timezone}</span>
    </div>

    <div class="form-group">
      <label>
        <input type="checkbox" bind:checked={config.Schedule.AutoStopEnabled}>
        Enable Automatic Stop
      </label>
    </div>

    <div class="form-group">
      <label for="stop-time">Stop Time (24h format)</label>
      <input
        type="time"
        id="stop-time"
        bind:value={config.Schedule.StopTime}
        disabled={!config.Schedule.AutoStopEnabled}
      >
      <span class="hint">Market time in {config.Schedule.Timezone}</span>
    </div>

    <div class="form-group">
      <label for="timezone">Time Zone</label>
      <select id="timezone" bind:value={config.Schedule.Timezone}>
        <option value="America/New_York">America/New_York (Eastern)</option>
        <option value="America/Chicago">America/Chicago (Central)</option>
        <option value="America/Denver">America/Denver (Mountain)</option>
        <option value="America/Los_Angeles">America/Los_Angeles (Pacific)</option>
      </select>
    </div>
  </div>

  <div class="settings-section">
    <h3>Manual Controls</h3>
    <p>Manually start or stop trading now, regardless of the schedule</p>

    <div class="button-group">
      <button class="btn start">Start Trading Now</button>
      <button class="btn stop">Stop Trading Now</button>
    </div>
  </div>

  <div class="footer-actions">
    <button class="btn primary" on:click={saveScheduleSettings} disabled={loading}>
      {loading ? 'Saving...' : 'Save Schedule Settings'}
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
    gap: 1rem;
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

  .btn.start {
    background-color: #4caf50;
    color: white;
    border-color: #388e3c;
  }

  .btn.stop {
    background-color: #f44336;
    color: white;
    border-color: #d32f2f;
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

  :global(body.dark-mode) .btn.start {
    background-color: #388e3c;
    border-color: #2e7d32;
  }

  :global(body.dark-mode) .btn.stop {
    background-color: #d32f2f;
    border-color: #c62828;
  }
</style>
