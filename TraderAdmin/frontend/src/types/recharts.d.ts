/**
 * Type declarations for recharts library to resolve TypeScript errors in Svelte components
 */

declare module 'recharts' {
  // Import SvelteComponent type from svelte
  import type { SvelteComponent } from 'svelte';

  // Define component types
  export class LineChart extends SvelteComponent<any> {}
  export class Line extends SvelteComponent<any> {}
  export class XAxis extends SvelteComponent<any> {}
  export class YAxis extends SvelteComponent<any> {}
  export class CartesianGrid extends SvelteComponent<any> {}
  export class Tooltip extends SvelteComponent<any> {}
  export class Legend extends SvelteComponent<any> {}
  export class ResponsiveContainer extends SvelteComponent<any> {}
  export class BarChart extends SvelteComponent<any> {}
  export class Bar extends SvelteComponent<any> {}
}
