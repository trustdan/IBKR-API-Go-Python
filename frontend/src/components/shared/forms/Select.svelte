<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let id: string | undefined = undefined;
  export let value: string | number = '';
  export let options: Array<string | number | { value: string | number; label: string }> = [];
  export let placeholder: string = 'Select an option';
  export let label: string | undefined = undefined;
  export let required: boolean = false;
  export let disabled: boolean = false;
  export let error: string | undefined = undefined;
  export let helpText: string | undefined = undefined;
  export let ariaLabel: string | undefined = undefined;
  export let fullWidth: boolean = true;

  const dispatch = createEventDispatcher();

  // Generate unique ID if not provided
  let uniqueId = id || `select-${Math.random().toString(36).substring(2, 9)}`;
  let helpId = helpText ? `${uniqueId}-help` : undefined;
  let errorId = error ? `${uniqueId}-error` : undefined;

  // Process options to ensure they're in the right format
  $: processedOptions = options.map(option => {
    if (typeof option === 'string' || typeof option === 'number') {
      return { value: option, label: String(option) };
    }
    return option;
  });

  function handleChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    value = target.value;
    dispatch('change', value);
  }
</script>

<div class={`select-field ${fullWidth ? 'full-width' : ''} ${error ? 'has-error' : ''}`}>
  {#if label}
    <label for={uniqueId} class={required ? 'required' : ''}>
      {label}
    </label>
  {/if}

  <div class="select-container">
    <select
      id={uniqueId}
      bind:value
      {disabled}
      {required}
      aria-required={required}
      aria-invalid={!!error}
      aria-describedby={[helpId, errorId].filter(Boolean).join(' ') || undefined}
      aria-label={ariaLabel || label}
      on:change={handleChange}
      on:blur
    >
      <option value="" disabled selected hidden>{placeholder}</option>

      {#each processedOptions as option}
        <option value={option.value}>{option.label}</option>
      {/each}
    </select>

    <div class="select-arrow">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="6 9 12 15 18 9"></polyline>
      </svg>
    </div>
  </div>

  {#if helpText}
    <div class="help-text" id={helpId}>{helpText}</div>
  {/if}

  {#if error}
    <div class="error-message" id={errorId}>{error}</div>
  {/if}
</div>

<style>
  .select-field {
    display: flex;
    flex-direction: column;
    margin-bottom: 1rem;
  }

  .full-width {
    width: 100%;
  }

  label {
    margin-bottom: 0.5rem;
    font-weight: 500;
    font-size: 0.875rem;
  }

  label.required::after {
    content: '*';
    color: #d32f2f;
    margin-left: 0.25rem;
  }

  .select-container {
    position: relative;
    width: 100%;
  }

  select {
    width: 100%;
    padding: 0.625rem 0.75rem;
    font-size: 1rem;
    line-height: 1.5;
    border: 1px solid #ccc;
    border-radius: 4px;
    transition: border-color 0.2s, box-shadow 0.2s;
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    background-color: white;
    cursor: pointer;
    padding-right: 2rem;
  }

  select:focus {
    outline: none;
    border-color: #0066cc;
    box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
  }

  select:disabled {
    background-color: #f5f5f5;
    color: #666;
    cursor: not-allowed;
  }

  select:invalid {
    color: #999;
  }

  .select-arrow {
    position: absolute;
    right: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    color: #666;
  }

  .help-text {
    margin-top: 0.375rem;
    font-size: 0.75rem;
    color: #666;
  }

  .has-error select {
    border-color: #d32f2f;
  }

  .has-error select:focus {
    box-shadow: 0 0 0 3px rgba(211, 47, 47, 0.1);
  }

  .error-message {
    margin-top: 0.375rem;
    font-size: 0.75rem;
    color: #d32f2f;
  }

  /* Hide default arrow in IE */
  select::-ms-expand {
    display: none;
  }
</style>
