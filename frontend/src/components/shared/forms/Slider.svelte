<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let id: string | undefined = undefined;
  export let value: number = 0;
  export let min: number = 0;
  export let max: number = 100;
  export let step: number = 1;
  export let label: string | undefined = undefined;
  export let showValue: boolean = true;
  export let valueSuffix: string = '';
  export let disabled: boolean = false;
  export let required: boolean = false;
  export let helpText: string | undefined = undefined;
  export let error: string | undefined = undefined;
  export let ariaLabel: string | undefined = undefined;

  const dispatch = createEventDispatcher();

  // Generate unique ID if not provided
  let uniqueId = id || `slider-${Math.random().toString(36).substring(2, 9)}`;
  let helpId = helpText ? `${uniqueId}-help` : undefined;
  let errorId = error ? `${uniqueId}-error` : undefined;

  // Percentage for styling
  $: percentage = ((value - min) / (max - min)) * 100;

  function handleInput(event: Event) {
    const target = event.target as HTMLInputElement;
    value = Number(target.value);
    dispatch('input', value);
  }

  function handleChange(event: Event) {
    dispatch('change', value);
  }

  function formatValue(val: number): string {
    return `${val}${valueSuffix}`;
  }
</script>

<div class={`slider-field ${error ? 'has-error' : ''}`}>
  <div class="slider-header">
    {#if label}
      <label for={uniqueId} class={required ? 'required' : ''}>
        {label}
      </label>
    {/if}

    {#if showValue}
      <div class="slider-value">
        {formatValue(value)}
      </div>
    {/if}
  </div>

  <div class="slider-container">
    <input
      type="range"
      id={uniqueId}
      bind:value
      {min}
      {max}
      {step}
      {disabled}
      {required}
      aria-required={required}
      aria-invalid={!!error}
      aria-describedby={[helpId, errorId].filter(Boolean).join(' ') || undefined}
      aria-label={ariaLabel || label}
      aria-valuemin={min}
      aria-valuemax={max}
      aria-valuenow={value}
      aria-valuetext={formatValue(value)}
      style={`--percentage: ${percentage}%`}
      on:input={handleInput}
      on:change={handleChange}
    />

    {#if min !== undefined || max !== undefined}
      <div class="slider-range">
        {#if min !== undefined}
          <span class="slider-min">{formatValue(min)}</span>
        {/if}

        {#if max !== undefined}
          <span class="slider-max">{formatValue(max)}</span>
        {/if}
      </div>
    {/if}
  </div>

  {#if helpText}
    <div class="help-text" id={helpId}>{helpText}</div>
  {/if}

  {#if error}
    <div class="error-message" id={errorId}>{error}</div>
  {/if}
</div>

<style>
  .slider-field {
    margin-bottom: 1rem;
  }

  .slider-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  label {
    font-weight: 500;
    font-size: 0.875rem;
  }

  label.required::after {
    content: '*';
    color: #d32f2f;
    margin-left: 0.25rem;
  }

  .slider-value {
    font-size: 0.875rem;
    color: #333;
    font-weight: 600;
  }

  .slider-container {
    position: relative;
  }

  input[type="range"] {
    -webkit-appearance: none;
    width: 100%;
    height: 4px;
    background: linear-gradient(to right, #0066cc var(--percentage), #ddd var(--percentage));
    outline: none;
    border-radius: 4px;
    margin: 0.75rem 0;
  }

  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 16px;
    height: 16px;
    background-color: #0066cc;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    transition: transform 0.1s;
  }

  input[type="range"]::-moz-range-thumb {
    width: 16px;
    height: 16px;
    background-color: #0066cc;
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    transition: transform 0.1s;
    border: none;
  }

  input[type="range"]:hover::-webkit-slider-thumb,
  input[type="range"]:focus::-webkit-slider-thumb {
    transform: scale(1.2);
  }

  input[type="range"]:hover::-moz-range-thumb,
  input[type="range"]:focus::-moz-range-thumb {
    transform: scale(1.2);
  }

  input[type="range"]:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  input[type="range"]:disabled::-webkit-slider-thumb {
    cursor: not-allowed;
  }

  input[type="range"]:disabled::-moz-range-thumb {
    cursor: not-allowed;
  }

  .slider-range {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #666;
    margin-top: 0.25rem;
  }

  .help-text {
    margin-top: 0.375rem;
    font-size: 0.75rem;
    color: #666;
  }

  .has-error input[type="range"] {
    background: linear-gradient(to right, #d32f2f var(--percentage), #ddd var(--percentage));
  }

  .has-error input[type="range"]::-webkit-slider-thumb {
    background-color: #d32f2f;
  }

  .has-error input[type="range"]::-moz-range-thumb {
    background-color: #d32f2f;
  }

  .error-message {
    margin-top: 0.375rem;
    font-size: 0.75rem;
    color: #d32f2f;
  }
</style>
