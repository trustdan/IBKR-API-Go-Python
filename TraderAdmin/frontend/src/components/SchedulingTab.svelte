<script lang="ts">
  import { onMount } from 'svelte';
  import { LoadConfig, SaveAndRestartStack } from '../../wailsjs/go/main/App';
  import { toast } from '@zerodevx/svelte-toast';

  let config: any = {};
  let loading: boolean = false;
  let saving: boolean = false;

  onMount(async () => {
    try {
      loading = true;
      config = await LoadConfig();
    } catch (error) {
      console.error('Failed to load config:', error);
      toast.push('Error loading configuration: ' + error.message, {
        theme: { '--toastBackground': '#F56565', '--toastBarBackground': '#C53030' }
      });
    } finally {
      loading = false;
    }
  });

  async function saveAndRestart() {
    if (!config) return;

    try {
      saving = true;
      const result = await SaveAndRestartStack(config);
      toast.push('Configuration saved and services restarted', {
        theme: { '--toastBackground': '#48BB78', '--toastBarBackground': '#2F855A' }
      });
      console.log('Save result:', result);
    } catch (error) {
      console.error('Failed to save config:', error);
      toast.push('Error saving configuration: ' + error.message, {
        theme: { '--toastBackground': '#F56565', '--toastBarBackground': '#C53030' }
      });
    } finally {
      saving = false;
    }
  }

  function validateTimeFormat(time: string): boolean {
    const regex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$/;
    return regex.test(time);
  }

  function handleInputChange(field: string, event: Event) {
    const target = event.target as HTMLInputElement;
    if (!config.scheduling) config.scheduling = {};
    config.scheduling[field] = target.value;
  }

  function handleCheckboxChange(day: string, event: Event) {
    const target = event.target as HTMLInputElement;

    if (!config.scheduling) config.scheduling = {};
    if (!config.scheduling.trading_days) config.scheduling.trading_days = [];

    if (target.checked) {
      if (!config.scheduling.trading_days.includes(day)) {
        config.scheduling.trading_days = [...config.scheduling.trading_days, day];
      }
    } else {
      config.scheduling.trading_days = config.scheduling.trading_days.filter((d: string) => d !== day);
    }
  }
</script>

<div class="tab-container">
  <h2>Scheduling & Execution</h2>

  {#if loading}
    <div class="loading">Loading configuration...</div>
  {:else}
    <div class="scheduling-form">
      <div class="form-section">
        <h3>Trading Hours</h3>

        <div class="form-group">
          <label for="trading_start_time">Trading Start Time:</label>
          <input
            type="time"
            id="trading_start_time"
            step="1"
            value={config.scheduling?.trading_start_time || ''}
            on:input={(e) => handleInputChange('trading_start_time', e)}
            class:invalid={!validateTimeFormat(config.scheduling?.trading_start_time || '')}
          />
          <span class="help-text">Format: HH:MM:SS (24-hour format)</span>
        </div>

        <div class="form-group">
          <label for="trading_end_time">Trading End Time:</label>
          <input
            type="time"
            id="trading_end_time"
            step="1"
            value={config.scheduling?.trading_end_time || ''}
            on:input={(e) => handleInputChange('trading_end_time', e)}
            class:invalid={!validateTimeFormat(config.scheduling?.trading_end_time || '')}
          />
          <span class="help-text">Format: HH:MM:SS (24-hour format)</span>
        </div>

        <div class="form-group">
          <label for="timezone">Timezone:</label>
          <input
            type="text"
            id="timezone"
            value={config.scheduling?.timezone || ''}
            on:input={(e) => handleInputChange('timezone', e)}
          />
          <span class="help-text">Example: America/New_York</span>
        </div>
      </div>

      <div class="form-section">
        <h3>Trading Days</h3>

        <div class="checkbox-group">
          {#each ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] as day}
            <label class="checkbox-label">
              <input
                type="checkbox"
                checked={config.scheduling?.trading_days?.includes(day) || false}
                on:change={(e) => handleCheckboxChange(day, e)}
              />
              {day}
            </label>
          {/each}
        </div>
      </div>

      <div class="form-section">
        <h3>Maintenance Window</h3>

        <div class="form-group">
          <label for="maintenance_window">Maintenance Window:</label>
          <input
            type="text"
            id="maintenance_window"
            value={config.scheduling?.maintenance_window || ''}
            on:input={(e) => handleInputChange('maintenance_window', e)}
          />
          <span class="help-text">Format: HH:MM:SS-HH:MM:SS (start-end times)</span>
        </div>
      </div>

      <div class="actions">
        <button
          class="save-btn"
          on:click={saveAndRestart}
          disabled={saving}
        >
          {saving ? 'Saving & Restarting...' : 'Save & Restart'}
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .tab-container {
    padding: 1rem;
  }

  h2 {
    margin-bottom: 1.5rem;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 0.5rem;
  }

  h3 {
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    font-size: 1.1rem;
  }

  .scheduling-form {
    max-width: 800px;
  }

  .form-section {
    margin-bottom: 2rem;
    padding: 1rem;
    background-color: #f8fafc;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .form-group {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.25rem;
    font-weight: 500;
  }

  input[type="text"],
  input[type="time"] {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #cbd5e0;
    border-radius: 0.25rem;
    font-size: 1rem;
    max-width: 250px;
  }

  input.invalid {
    border-color: #e53e3e;
    background-color: #fff5f5;
  }

  .help-text {
    display: block;
    font-size: 0.8rem;
    color: #718096;
    margin-top: 0.25rem;
  }

  .checkbox-group {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 0.5rem;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    font-weight: normal;
  }

  .checkbox-label input {
    margin-right: 0.5rem;
  }

  .actions {
    margin-top: 2rem;
  }

  .save-btn {
    background-color: #4299e1;
    color: white;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 500;
    transition: background-color 0.2s;
  }

  .save-btn:hover {
    background-color: #3182ce;
  }

  .save-btn:disabled {
    background-color: #a0aec0;
    cursor: not-allowed;
  }

  .loading {
    padding: 2rem;
    text-align: center;
    color: #718096;
  }
</style>
