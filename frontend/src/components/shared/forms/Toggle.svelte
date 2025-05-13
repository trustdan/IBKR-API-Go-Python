<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let id: string | undefined = undefined;
  export let value: boolean = false;
  export let label: string | undefined = undefined;
  export let disabled: boolean = false;
  export let required: boolean = false;
  export let helpText: string | undefined = undefined;
  export let error: string | undefined = undefined;
  export let ariaLabel: string | undefined = undefined;
  export let size: 'small' | 'medium' | 'large' = 'medium';

  const dispatch = createEventDispatcher();

  // Generate unique ID if not provided
  let uniqueId = id || `toggle-${Math.random().toString(36).substring(2, 9)}`;
  let helpId = helpText ? `${uniqueId}-help` : undefined;
  let errorId = error ? `${uniqueId}-error` : undefined;

  function handleChange(event: Event) {
    const target = event.target as HTMLInputElement;
    value = target.checked;
    dispatch('change', value);
  }
</script>

<div class={`toggle-field toggle-${size} ${error ? 'has-error' : ''}`}>
  <label class="toggle-container" for={uniqueId}>
    <input
      type="checkbox"
      id={uniqueId}
      checked={value}
      {disabled}
      {required}
      aria-required={required}
      aria-invalid={!!error}
      aria-describedby={[helpId, errorId].filter(Boolean).join(' ') || undefined}
      aria-label={ariaLabel || label}
      on:change={handleChange}
    />
    <span class="toggle-slider"></span>

    {#if label}
      <span class="toggle-label">{label}</span>
    {/if}
  </label>

  {#if helpText}
    <div class="help-text" id={helpId}>{helpText}</div>
  {/if}

  {#if error}
    <div class="error-message" id={errorId}>{error}</div>
  {/if}
</div>

<style>
  .toggle-field {
    margin-bottom: 1rem;
  }

  .toggle-container {
    display: inline-flex;
    align-items: center;
    position: relative;
    cursor: pointer;
  }

  input[type="checkbox"] {
    opacity: 0;
    width: 0;
    height: 0;
    position: absolute;
  }

  .toggle-slider {
    position: relative;
    display: inline-block;
    background-color: #ccc;
    border-radius: 24px;
    transition: background-color 0.2s;
  }

  .toggle-slider::before {
    content: '';
    position: absolute;
    background-color: white;
    border-radius: 50%;
    transform: translateX(0);
    transition: transform 0.2s;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  /* Sizes */
  .toggle-small .toggle-slider {
    width: 32px;
    height: 16px;
  }

  .toggle-small .toggle-slider::before {
    width: 12px;
    height: 12px;
    top: 2px;
    left: 2px;
  }

  .toggle-medium .toggle-slider {
    width: 40px;
    height: 20px;
  }

  .toggle-medium .toggle-slider::before {
    width: 16px;
    height: 16px;
    top: 2px;
    left: 2px;
  }

  .toggle-large .toggle-slider {
    width: 48px;
    height: 24px;
  }

  .toggle-large .toggle-slider::before {
    width: 20px;
    height: 20px;
    top: 2px;
    left: 2px;
  }

  /* Checked state */
  input:checked + .toggle-slider {
    background-color: #0066cc;
  }

  .toggle-small input:checked + .toggle-slider::before {
    transform: translateX(16px);
  }

  .toggle-medium input:checked + .toggle-slider::before {
    transform: translateX(20px);
  }

  .toggle-large input:checked + .toggle-slider::before {
    transform: translateX(24px);
  }

  /* Disabled state */
  input:disabled + .toggle-slider {
    opacity: 0.6;
    cursor: not-allowed;
  }

  input:disabled ~ .toggle-label {
    opacity: 0.6;
    cursor: not-allowed;
  }

  /* Focus state */
  input:focus + .toggle-slider {
    box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.3);
  }

  /* Label */
  .toggle-label {
    margin-left: 0.5rem;
    font-size: 0.875rem;
  }

  /* Help text and error message */
  .help-text {
    margin-top: 0.375rem;
    font-size: 0.75rem;
    color: #666;
  }

  .error-message {
    margin-top: 0.375rem;
    font-size: 0.75rem;
    color: #d32f2f;
  }

  .has-error .toggle-slider {
    box-shadow: 0 0 0 2px rgba(211, 47, 47, 0.3);
  }
</style>
