<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { JSONSchema7 } from '../stores/schemaStore';

  export let schema: JSONSchema7;
  export let data: Record<string, any>;
  export let path: string = '';

  const dispatch = createEventDispatcher();

  // Helper to get a nested value from an object using a dot-notation path
  function getNestedValue(obj: any, path: string): any {
    if (!path) return obj;
    return path.split('.').reduce((prev, curr) => prev && prev[curr], obj);
  }

  // Helper to set a nested value in an object using a dot-notation path
  function setNestedValue(obj: any, path: string, value: any): void {
    if (!path) return;
    const parts = path.split('.');
    const last = parts.pop();
    const target = parts.reduce((prev, curr) => {
      if (!prev[curr]) prev[curr] = {};
      return prev[curr];
    }, obj);
    if (last) {
      target[last] = value;
    }
  }

  // Handle input changes and update the data object
  function handleChange(fieldPath: string, value: any): void {
    setNestedValue(data, fieldPath, value);
    dispatch('change', { path: fieldPath, value });
  }

  // Generate an ID attribute for form elements
  function generateId(fieldPath: string): string {
    return fieldPath.replace(/\./g, '-');
  }

  // Check if a field is required based on the schema
  function isFieldRequired(fieldName: string): boolean {
    return schema.required?.includes(fieldName) || false;
  }

  // Get validation attributes for a field
  function getValidationAttributes(fieldSchema: JSONSchema7): Record<string, string> {
    const attrs: Record<string, string> = {};

    if (fieldSchema.minimum !== undefined) {
      attrs.min = String(fieldSchema.minimum);
    }

    if (fieldSchema.maximum !== undefined) {
      attrs.max = String(fieldSchema.maximum);
    }

    if (fieldSchema.minLength !== undefined) {
      attrs.minlength = String(fieldSchema.minLength);
    }

    if (fieldSchema.maxLength !== undefined) {
      attrs.maxlength = String(fieldSchema.maxLength);
    }

    return attrs;
  }
</script>

{#if schema.properties}
  <div class="dynamic-form">
    {#each Object.entries(schema.properties) as [fieldName, fieldSchema]}
      {@const fieldPath = path ? `${path}.${fieldName}` : fieldName}
      {@const fieldId = generateId(fieldPath)}
      {@const value = getNestedValue(data, fieldPath)}
      {@const validationAttrs = getValidationAttributes(fieldSchema)}

      <div class="form-group">
        <label for={fieldId} class:required={isFieldRequired(fieldName)}>
          {fieldSchema.title || fieldName}
          {#if fieldSchema.description}
            <span class="tooltip" title={fieldSchema.description}>ℹ</span>
          {/if}
        </label>

        {#if fieldSchema.type === 'object' && fieldSchema.properties}
          <!-- Recursively render nested object properties -->
          <fieldset>
            <legend>{fieldSchema.title || fieldName}</legend>
            <svelte:self
              schema={fieldSchema}
              data={data}
              path={fieldPath}
              on:change
            />
          </fieldset>
        {:else if fieldSchema.type === 'boolean'}
          <!-- Boolean field (checkbox) -->
          <div class="checkbox-wrapper">
            <input
              type="checkbox"
              id={fieldId}
              bind:checked={data[fieldName]}
              on:change={() => handleChange(fieldPath, data[fieldName])}
            />
          </div>
        {:else if fieldSchema.enum}
          <!-- Enum field (select) -->
          <select
            id={fieldId}
            bind:value={data[fieldName]}
            on:change={() => handleChange(fieldPath, data[fieldName])}
            required={isFieldRequired(fieldName)}
          >
            {#each fieldSchema.enum as option}
              <option value={option}>{option}</option>
            {/each}
          </select>
        {:else if fieldSchema.type === 'integer' || fieldSchema.type === 'number'}
          <!-- Number input -->
          <input
            type="number"
            id={fieldId}
            bind:value={data[fieldName]}
            on:change={() => handleChange(fieldPath, data[fieldName])}
            required={isFieldRequired(fieldName)}
            step={fieldSchema.type === 'integer' ? 1 : 'any'}
            {...validationAttrs}
          />
        {:else}
          <!-- Default to text input -->
          <input
            type="text"
            id={fieldId}
            bind:value={data[fieldName]}
            on:change={() => handleChange(fieldPath, data[fieldName])}
            required={isFieldRequired(fieldName)}
            {...validationAttrs}
          />
        {/if}

        {#if validationAttrs.min && validationAttrs.max}
          <div class="form-help">
            Range: {validationAttrs.min} to {validationAttrs.max}
          </div>
        {/if}
      </div>
    {/each}
  </div>
{/if}

<style>
  .dynamic-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
  }

  label {
    font-weight: 500;
    margin-bottom: 0.25rem;
    color: #1e293b;
    display: flex;
    align-items: center;
  }

  label.required::after {
    content: "*";
    color: #dc2626;
    margin-left: 0.25rem;
  }

  input[type="text"],
  input[type="number"],
  select {
    padding: 0.5rem;
    border: 1px solid #cbd5e1;
    border-radius: 0.25rem;
    font-size: 1rem;
    width: 100%;
    max-width: 400px;
  }

  input[type="text"]:focus,
  input[type="number"]:focus,
  select:focus {
    border-color: #3b82f6;
    outline: none;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
  }

  .checkbox-wrapper {
    height: 42px;
    display: flex;
    align-items: center;
  }

  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }

  fieldset {
    border: 1px solid #cbd5e1;
    border-radius: 0.25rem;
    padding: 1rem;
    margin: 0.5rem 0;
  }

  legend {
    font-weight: 600;
    font-size: 0.875rem;
    padding: 0 0.5rem;
    color: #1e293b;
  }

  .tooltip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background-color: #94a3b8;
    color: white;
    font-size: 0.75rem;
    margin-left: 0.5rem;
    cursor: help;
  }

  .form-help {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.25rem;
  }
</style>
