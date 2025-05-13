<script lang="ts">
  export let variant: 'primary' | 'secondary' | 'danger' = 'primary';
  export let size: 'small' | 'medium' | 'large' = 'medium';
  export let type: 'button' | 'submit' | 'reset' = 'button';
  export let disabled: boolean = false;
  export let loading: boolean = false;
  export let icon: string | null = null;
  export let fullWidth: boolean = false;
</script>

<button
  {type}
  class={`btn btn-${variant} btn-${size} ${fullWidth ? 'full-width' : ''}`}
  disabled={disabled || loading}
  on:click
>
  {#if loading}
    <span class="spinner"></span>
  {:else if icon}
    <span class="icon">{icon}</span>
  {/if}
  <slot />
</button>

<style>
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    transition: background-color 0.2s, box-shadow 0.2s;
    position: relative;
    text-align: center;
  }

  .btn:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.3);
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  /* Variants */
  .btn-primary {
    background-color: #0066cc;
    color: white;
  }

  .btn-primary:not(:disabled):hover {
    background-color: #0055aa;
  }

  .btn-secondary {
    background-color: #f0f0f0;
    color: #333;
    border: 1px solid #ccc;
  }

  .btn-secondary:not(:disabled):hover {
    background-color: #e0e0e0;
  }

  .btn-danger {
    background-color: #f44336;
    color: white;
  }

  .btn-danger:not(:disabled):hover {
    background-color: #d32f2f;
  }

  /* Sizes */
  .btn-small {
    padding: 0.25rem 0.5rem;
    font-size: 0.875rem;
  }

  .btn-medium {
    padding: 0.5rem 1rem;
    font-size: 1rem;
  }

  .btn-large {
    padding: 0.75rem 1.5rem;
    font-size: 1.125rem;
  }

  /* Loading spinner */
  .spinner {
    display: inline-block;
    width: 1em;
    height: 1em;
    margin-right: 0.5rem;
    border: 2px solid currentColor;
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Icon */
  .icon {
    margin-right: 0.5rem;
  }

  /* Full width */
  .full-width {
    width: 100%;
  }
</style>
