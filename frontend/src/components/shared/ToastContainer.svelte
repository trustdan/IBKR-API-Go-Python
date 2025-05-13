<script lang="ts">
  import { onDestroy } from 'svelte';
  import Toast from './Toast.svelte';

  export let position: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' = 'top-right';
  export let limit: number = 5;

  type ToastType = 'info' | 'success' | 'warning' | 'error';

  interface Toast {
    id: number;
    type: ToastType;
    message: string;
    duration?: number;
  }

  // Toasts store
  let toasts: Toast[] = [];
  let lastId = 0;

  // Subscribe to the toast store
  let unsubscribe = () => {};

  // Remove toast by id
  function removeToast(id: number) {
    toasts = toasts.filter(toast => toast.id !== id);
  }

  // Added for component API access
  export function addToast(message: string, type: ToastType = 'info', duration: number = 5000) {
    const id = ++lastId;

    // Ensure we don't exceed the limit
    if (toasts.length >= limit) {
      toasts = toasts.slice(1);
    }

    toasts = [...toasts, { id, type, message, duration }];
    return id;
  }

  export function removeAllToasts() {
    toasts = [];
  }

  // Clean up
  onDestroy(() => {
    if (unsubscribe) unsubscribe();
  });

  // Helper functions for each type
  export function info(message: string, duration?: number) {
    return addToast(message, 'info', duration);
  }

  export function success(message: string, duration?: number) {
    return addToast(message, 'success', duration);
  }

  export function warning(message: string, duration?: number) {
    return addToast(message, 'warning', duration);
  }

  export function error(message: string, duration?: number) {
    return addToast(message, 'error', duration);
  }
</script>

<div class={`toast-container toast-container-${position}`}>
  {#each toasts as toast (toast.id)}
    <Toast
      type={toast.type}
      message={toast.message}
      {position}
      duration={toast.duration}
      on:close={() => removeToast(toast.id)}
    />
  {/each}
</div>

<style>
  .toast-container {
    position: fixed;
    z-index: 9999;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    pointer-events: none;
  }

  .toast-container > :global(*) {
    pointer-events: auto;
  }

  .toast-container-top-right {
    top: 0;
    right: 0;
  }

  .toast-container-top-left {
    top: 0;
    left: 0;
  }

  .toast-container-bottom-right {
    bottom: 0;
    right: 0;
  }

  .toast-container-bottom-left {
    bottom: 0;
    left: 0;
  }

  /* For bottom containers, reverse the order */
  .toast-container-bottom-right,
  .toast-container-bottom-left {
    flex-direction: column-reverse;
  }
</style>
