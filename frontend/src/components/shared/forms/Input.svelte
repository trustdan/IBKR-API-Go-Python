<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  export let id: string | undefined = undefined;
  export let value: string | number = '';
  export let type: 'text' | 'number' | 'email' | 'password' | 'search' | 'tel' | 'url' = 'text';
  export let placeholder: string = '';
  export let label: string | undefined = undefined;
  export let required: boolean = false;
  export let disabled: boolean = false;
  export let readonly: boolean = false;
  export let min: number | undefined = undefined;
  export let max: number | undefined = undefined;
  export let step: number | undefined = undefined;
  export let error: string | undefined = undefined;
  export let helpText: string | undefined = undefined;
  export let ariaLabel: string | undefined = undefined;
  export let fullWidth: boolean = true;
  export let icon: string | undefined = undefined;

  const dispatch = createEventDispatcher();

  // Generate unique ID if not provided
  let uniqueId = id || `input-${Math.random().toString(36).substring(2, 9)}`;
  let helpId = helpText ? `${uniqueId}-help` : undefined;
  let errorId = error ? `${uniqueId}-error` : undefined;

  // Handle internal value separately to allow two-way binding with different types
  let inputValue: string = typeof value === 'number' ? value.toString() : value;

  $: if (typeof value === 'number' && inputValue !== value.toString()) {
    inputValue = value.toString();
  } else if (typeof value === 'string' && inputValue !== value) {
    inputValue = value;
  }

  function handleInput(event: Event) {
    const target = event.target as HTMLInputElement;

    // Update our internal value
    inputValue = target.value;

    // For number inputs, convert the value to a number before dispatching
    if (type === 'number' && target.value !== '') {
      dispatch('input', Number(target.value));
    } else {
      dispatch('input', target.value);
    }
  }

  function handleChange(event: Event) {
    const target = event.target as HTMLInputElement;

    // For number inputs, update the parent's value as a number
    if (type === 'number' && target.value !== '') {
      value = Number(target.value);
    } else {
      value = target.value;
    }

    dispatch('change', target.value);
  }
</script>

<div class={`form-field ${fullWidth ? 'full-width' : ''} ${error ? 'has-error' : ''}`}>
  {#if label}
    <label for={uniqueId} class={required ? 'required' : ''}>
      {label}
    </label>
  {/if}

  <div class={`input-container ${icon ? 'has-icon' : ''}`}>
    {#if icon}
      <span class="input-icon">{icon}</span>
    {/if}

    {#if type === 'text'}
      <input
        type="text"
        id={uniqueId}
        value={inputValue}
        {placeholder}
        {disabled}
        {readonly}
        {required}
        aria-required={required}
        aria-invalid={!!error}
        aria-describedby={[helpId, errorId].filter(Boolean).join(' ') || undefined}
        aria-label={ariaLabel || label}
        on:input={handleInput}
        on:change={handleChange}
        on:focus
        on:blur
        on:keydown
        on:keyup
      />
    {:else if type === 'number'}
      <input
        type="number"
        id={uniqueId}
        value={inputValue}
        {placeholder}
        {disabled}
        {readonly}
        {min}
        {max}
        {step}
        {required}
        aria-required={required}
        aria-invalid={!!error}
        aria-describedby={[helpId, errorId].filter(Boolean).join(' ') || undefined}
        aria-label={ariaLabel || label}
        on:input={handleInput}
        on:change={handleChange}
        on:focus
        on:blur
        on:keydown
        on:keyup
      />
    {:else if type === 'password'}
      <input
        type="password"
        id={uniqueId}
        value={inputValue}
        {placeholder}
        {disabled}
        {readonly}
        {required}
        aria-required={required}
        aria-invalid={!!error}
        aria-describedby={[helpId, errorId].filter(Boolean).join(' ') || undefined}
        aria-label={ariaLabel || label}
        on:input={handleInput}
        on:change={handleChange}
        on:focus
        on:blur
        on:keydown
        on:keyup
      />
    {:else if type === 'email'}
      <input
        type="email"
        id={uniqueId}
        value={inputValue}
        {placeholder}
        {disabled}
        {readonly}
        {required}
        aria-required={required}
        aria-invalid={!!error}
        aria-describedby={[helpId, errorId].filter(Boolean).join(' ') || undefined}
        aria-label={ariaLabel || label}
        on:input={handleInput}
        on:change={handleChange}
        on:focus
        on:blur
        on:keydown
        on:keyup
      />
    {:else if type === 'search'}
      <input
        type="search"
        id={uniqueId}
        value={inputValue}
        {placeholder}
        {disabled}
        {readonly}
        {required}
        aria-required={required}
        aria-invalid={!!error}
        aria-describedby={[helpId, errorId].filter(Boolean).join(' ') || undefined}
        aria-label={ariaLabel || label}
        on:input={handleInput}
        on:change={handleChange}
        on:focus
        on:blur
        on:keydown
        on:keyup
      />
    {:else if type === 'tel'}
      <input
        type="tel"
        id={uniqueId}
        value={inputValue}
        {placeholder}
        {disabled}
        {readonly}
        {required}
        aria-required={required}
        aria-invalid={!!error}
        aria-describedby={[helpId, errorId].filter(Boolean).join(' ') || undefined}
        aria-label={ariaLabel || label}
        on:input={handleInput}
        on:change={handleChange}
        on:focus
        on:blur
        on:keydown
        on:keyup
      />
    {:else if type === 'url'}
      <input
        type="url"
        id={uniqueId}
        value={inputValue}
        {placeholder}
        {disabled}
        {readonly}
        {required}
        aria-required={required}
        aria-invalid={!!error}
        aria-describedby={[helpId, errorId].filter(Boolean).join(' ') || undefined}
        aria-label={ariaLabel || label}
        on:input={handleInput}
        on:change={handleChange}
        on:focus
        on:blur
        on:keydown
        on:keyup
      />
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
  .form-field {
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

  .input-container {
    position: relative;
  }

  .input-icon {
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    color: #666;
    font-size: 1rem;
    pointer-events: none;
  }

  input {
    width: 100%;
    padding: 0.625rem 0.75rem;
    font-size: 1rem;
    line-height: 1.5;
    border: 1px solid #ccc;
    border-radius: 4px;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  .has-icon input {
    padding-left: 2.5rem;
  }

  input:focus {
    outline: none;
    border-color: #0066cc;
    box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
  }

  input:disabled {
    background-color: #f5f5f5;
    color: #666;
    cursor: not-allowed;
  }

  input:read-only {
    background-color: #f9f9f9;
  }

  input[type="number"] {
    -moz-appearance: textfield;
  }

  input[type="number"]::-webkit-outer-spin-button,
  input[type="number"]::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  .help-text {
    margin-top: 0.375rem;
    font-size: 0.75rem;
    color: #666;
  }

  .has-error input {
    border-color: #d32f2f;
  }

  .has-error input:focus {
    box-shadow: 0 0 0 3px rgba(211, 47, 47, 0.1);
  }

  .error-message {
    margin-top: 0.375rem;
    font-size: 0.75rem;
    color: #d32f2f;
  }
</style>
