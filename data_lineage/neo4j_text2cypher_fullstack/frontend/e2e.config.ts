import type { E2EConfig } from 'e2e';
import { web } from '@e2e-dev/web';

const url = process.env.E2E_BASE_URL ?? 'http://localhost:5173';

export default {
  tests: 'tests/**/*.e2e.ts',
  timeout: 180_000,
  workers: 1,
  targets: [
    {
      engine: web(),
      app: {
        url,
        command: {
          executable: 'pnpm',
          args: ['dev', '--port', new URL(url).port || '5173', '--strictPort'],
          reuseExisting: true,
          startupTimeout: 120_000,
          log: '.e2e/logs/app.log',
        },
      },
    },
  ],
} satisfies E2EConfig;
