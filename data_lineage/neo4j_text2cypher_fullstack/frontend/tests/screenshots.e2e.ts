import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { test } from '@e2e-dev/web';
import { expect } from 'e2e';

const SHOTS_DIR = join(process.env.KG_SHOTS_DIR ?? join(tmpdir(), 'kg_frontend_shots'), process.env.KG_SHOTS_LABEL ?? 'latest');

test('captures a graph answer in dark and light mode', { tags: ['screenshots'] }, async ({ app, screen, browser }) => {
  mkdirSync(SHOTS_DIR, { recursive: true });
  await app.open('/');
  await screen
    .getByPlaceholder('Ask me a question (Press Shift+Enter for new line)...')
    .fill('Show the tables in the wholesale_core schema');
  await screen.getByRole('button', 'Submit').tap();
  await expect(screen.getByRole('button', 'Graph View')).toBeVisible({ timeout: 120_000 });
  await expect(screen.getByRole('button', 'Submit')).toBeVisible({ timeout: 120_000 });
  await screen.getByRole('button', 'Fit to screen').tap();

  const body = browser.locator('body');
  await expect(browser).toHaveClass(body, /ndl-theme-dark/);
  copyFileSync(await app.screenshot('graph-dark'), join(SHOTS_DIR, 'graph-dark.png'));

  await screen.getByRole('button', 'Toggle dark mode').tap();
  await expect(browser).not.toHaveClass(body, /ndl-theme-dark/);
  await screen.getByRole('button', 'Fit to screen').tap();
  copyFileSync(await app.screenshot('graph-light'), join(SHOTS_DIR, 'graph-light.png'));
});
