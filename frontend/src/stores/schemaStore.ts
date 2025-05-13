import { writable } from 'svelte/store';
import { GetConfigSchema } from '../wailsjs/go/main/App';

// Define JSONSchema7 type for schema representation
export interface JSONSchema7 {
  $schema?: string;
  $id?: string;
  title?: string;
  description?: string;
  type?: string | string[];
  properties?: Record<string, JSONSchema7>;
  required?: string[];
  items?: JSONSchema7 | JSONSchema7[];
  minimum?: number;
  maximum?: number;
  minLength?: number;
  maxLength?: number;
  enum?: any[];
  format?: string;
  default?: any;
  additionalProperties?: boolean | JSONSchema7;
  [key: string]: any;
}

// Create a writable store for the schema
export const schemaStore = writable<JSONSchema7 | null>(null);

// Function to load the schema from the backend
export async function loadSchema(): Promise<boolean> {
  try {
    // Call the real Wails backend
    const schemaString = await GetConfigSchema();
    const schema = JSON.parse(schemaString);

    console.log('Schema loaded from backend:', schema);
    schemaStore.set(schema);
    return true;
  } catch (error) {
    console.error("Failed to load schema:", error);
    return false;
  }
}
