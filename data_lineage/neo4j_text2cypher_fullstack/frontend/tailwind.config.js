import { tailwindConfig } from '@neo4j-ndl/base';

/** @type {import('tailwindcss').Config} */
export default {
  presets: [tailwindConfig],
  content: ['./index.html', './src/**/*.{html,tsx}'],
  corePlugins: {
    preflight: false,
  },
};
