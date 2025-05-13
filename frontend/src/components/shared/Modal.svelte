<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';

  export let open: boolean = false;
  export let title: string | null = null;
  export let size: 'small' | 'medium' | 'large' | 'full' = 'medium';
  export let closeOnEscape: boolean = true;
  export let closeOnBackdropClick: boolean = true;

  const dispatch = createEventDispatcher();

  function close() {
    dispatch('close');
  }

  function handleKeydown(event: KeyboardEvent) {
    if (closeOnEscape && event.key === 'Escape' && open) {
      close();
    }
  }

  function handleBackdropClick(event: MouseEvent) {
    if (closeOnBackdropClick && event.target === event.currentTarget) {
      close();
    }
  }

  onMount(() => {
    document.addEventListener('keydown', handleKeydown);
    return () => {
      document.removeEventListener('keydown', handleKeydown);
    };
  });
</script>

{#if open}
  <div
    class="modal-backdrop"
    on:click={handleBackdropClick}
    transition:fade={{ duration: 150 }}
  >
    <div
      class={`modal-container modal-${size}`}
      role="dialog"
      aria-modal="true"
      transition:fly={{ y: -20, duration: 200 }}
    >
      {#if title || $$slots.header}
        <div class="modal-header">
          {#if $$slots.header}
            <slot name="header"></slot>
          {:else}
            <h2 class="modal-title">{title}</h2>
          {/if}
          <button class="close-button" on:click={close} aria-label="Close">
            &times;
          </button>
        </div>
      {/if}

      <div class="modal-content">
        <slot></slot>
      </div>

      {#if $$slots.footer}
        <div class="modal-footer">
          <slot name="footer"></slot>
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    padding: 1rem;
  }

  .modal-container {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    display: flex;
    flex-direction: column;
    max-height: calc(100vh - 2rem);
    width: 100%;
    overflow: hidden;
  }

  .modal-small {
    max-width: 400px;
  }

  .modal-medium {
    max-width: 600px;
  }

  .modal-large {
    max-width: 800px;
  }

  .modal-full {
    max-width: calc(100vw - 2rem);
    height: calc(100vh - 2rem);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #e0e0e0;
  }

  .modal-title {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
  }

  .close-button {
    background: none;
    border: none;
    font-size: 1.5rem;
    line-height: 1;
    cursor: pointer;
    color: #666;
    padding: 0;
  }

  .close-button:hover {
    color: #333;
  }

  .modal-content {
    padding: 1.5rem;
    overflow-y: auto;
    flex: 1;
  }

  .modal-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid #e0e0e0;
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
  }
</style>
