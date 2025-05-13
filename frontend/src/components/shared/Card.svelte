<script lang="ts">
  export let title: string | null = null;
  export let subtitle: string | null = null;
  export let noPadding: boolean = false;
  export let variant: 'default' | 'outlined' | 'elevated' = 'default';
</script>

<div class={`card card-${variant} ${noPadding ? 'no-padding' : ''}`}>
  {#if title || $$slots.header}
    <div class="card-header">
      {#if $$slots.header}
        <slot name="header"></slot>
      {:else}
        <div class="header-content">
          <h2 class="card-title">{title}</h2>
          {#if subtitle}
            <p class="card-subtitle">{subtitle}</p>
          {/if}
        </div>
      {/if}

      {#if $$slots.actions}
        <div class="card-actions">
          <slot name="actions"></slot>
        </div>
      {/if}
    </div>
  {/if}

  <div class="card-content">
    <slot></slot>
  </div>

  {#if $$slots.footer}
    <div class="card-footer">
      <slot name="footer"></slot>
    </div>
  {/if}
</div>

<style>
  .card {
    background-color: white;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 1.5rem;
  }

  .card-default {
    border: 1px solid #e0e0e0;
  }

  .card-outlined {
    border: 1px solid #e0e0e0;
    background-color: transparent;
  }

  .card-elevated {
    border: none;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #e0e0e0;
  }

  .header-content {
    flex: 1;
  }

  .card-title {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
  }

  .card-subtitle {
    margin: 0.25rem 0 0;
    font-size: 0.875rem;
    color: #666;
  }

  .card-content {
    padding: 1.5rem;
  }

  .no-padding .card-content {
    padding: 0;
  }

  .card-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid #e0e0e0;
    background-color: #f9f9f9;
  }

  .card-actions {
    display: flex;
    gap: 0.5rem;
  }
</style>
