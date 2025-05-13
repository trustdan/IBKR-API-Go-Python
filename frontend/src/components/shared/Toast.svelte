<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';

  export let type: 'info' | 'success' | 'warning' | 'error' = 'info';
  export let message: string;
  export let duration: number = 5000; // milliseconds
  export let position: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' = 'top-right';

  const dispatch = createEventDispatcher();
  let timeoutId: number;

  onMount(() => {
    if (duration > 0) {
      timeoutId = window.setTimeout(() => {
        close();
      }, duration);
    }

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  });

  function close() {
    dispatch('close');
  }

  // Icon based on type
  const icons = {
    info: '🔵',
    success: '✅',
    warning: '⚠️',
    error: '❌'
  };
</script>

<div
  class={`toast toast-${type} toast-${position}`}
  role="alert"
  in:fly={{ y: position.includes('top') ? -20 : 20, duration: 300 }}
  out:fade={{ duration: 200 }}
>
  <div class="toast-icon">
    {icons[type]}
  </div>
  <div class="toast-content">
    {message}
  </div>
  <button class="toast-close" on:click={close} aria-label="Close">
    &times;
  </button>
</div>

<style>
  .toast {
    display: flex;
    align-items: flex-start;
    padding: 1rem;
    border-radius: 4px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
    margin-bottom: 0.5rem;
    position: relative;
    min-width: 250px;
    max-width: 350px;
    animation: progress linear forwards;
  }

  @keyframes progress {
    to {
      background-position: 0% 0%;
    }
  }

  .toast-icon {
    margin-right: 0.75rem;
    font-size: 1.25rem;
  }

  .toast-content {
    flex: 1;
    margin-right: 1.5rem;
  }

  .toast-close {
    background: none;
    border: none;
    font-size: 1.25rem;
    line-height: 1;
    cursor: pointer;
    opacity: 0.6;
    padding: 0;
    color: inherit;
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
  }

  .toast-close:hover {
    opacity: 1;
  }

  .toast-info {
    background-color: #e3f2fd;
    color: #0277bd;
    border-left: 4px solid #0277bd;
    background-image: linear-gradient(to right, #e3f2fd, #e3f2fd);
    background-size: 100% 100%;
  }

  .toast-success {
    background-color: #e8f5e9;
    color: #2e7d32;
    border-left: 4px solid #2e7d32;
    background-image: linear-gradient(to right, #e8f5e9, #e8f5e9);
    background-size: 100% 100%;
  }

  .toast-warning {
    background-color: #fff8e1;
    color: #ff8f00;
    border-left: 4px solid #ff8f00;
    background-image: linear-gradient(to right, #fff8e1, #fff8e1);
    background-size: 100% 100%;
  }

  .toast-error {
    background-color: #ffebee;
    color: #c62828;
    border-left: 4px solid #c62828;
    background-image: linear-gradient(to right, #ffebee, #ffebee);
    background-size: 100% 100%;
  }
</style>
