import { existsSync, readFileSync } from 'node:fs';
import { beforeEach, describe, test } from '@e2e-dev/web';
import { expect } from 'e2e';

const ANSWER_TIMEOUT = 150_000;
const repo = new URL('../../../', import.meta.url);
const manifestPath = new URL('synthetic_data/manifest.json', repo);

type Question = {
  id: string;
  question: string;
  expect?: string | string[];
  ask_match?: 'any' | 'feedback' | 'poor';
  small_talk?: boolean;
};

const questions: Question[] = JSON.parse(readFileSync(new URL('synthetic/competency_questions.json', repo), 'utf-8'));
const expected: Record<string, unknown> = existsSync(manifestPath)
  ? JSON.parse(readFileSync(manifestPath, 'utf-8')).expected
  : {};

function flatten(value: unknown): string[] {
  if (Array.isArray(value)) return value.flatMap(flatten);
  if (value && typeof value === 'object') return Object.values(value).flatMap(flatten);
  return [String(value)];
}

function appears(text: string, value: string): boolean {
  const escaped = value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(`(?<![\\w.])${escaped}(?![\\w])`, 'i').test(text);
}

describe('competency questions against the synthetic catalog', () => {
  beforeEach(async ({ app, screen }) => {
    await app.open('/');
    await expect(screen.getByText('Lagos Refining & Supply Company Semantic Portal').first()).toBeVisible();
  });

  for (const q of questions) {
    test(`${q.id}: ${q.question}`, async ({ screen, browser }) => {
      await screen.getByPlaceholder('Ask me a question (Press Shift+Enter for new line)...').fill(q.question);
      await screen.getByRole('button', 'Submit').tap();
      await expect(screen.getByRole('button', 'Thumbs up')).toBeEnabled({ timeout: ANSWER_TIMEOUT });
      await expect(screen.getByRole('button', 'Submit')).toBeVisible({ timeout: ANSWER_TIMEOUT });

      if (q.small_talk) {
        await expect(screen.getByRole('button', 'Graph View')).toHaveCount(0);
        return;
      }

      const values = [q.expect ?? []].flat().flatMap((key) => {
        if (!(key in expected)) throw new Error(`manifest.json has no expected value ${key}; generate the catalog first`);
        return flatten(expected[key]);
      });

      if ((await screen.getByRole('button', 'Table Grid').count()) > 0) {
        await screen.getByRole('button', 'Table Grid').tap();
      }
      await expect(screen.getByRole('table').first()).toBeVisible();

      const page = await browser.evaluate(() => ({
        text: document.body.innerText,
        rows: document.querySelectorAll('table tbody tr').length,
      }));
      const answer = page.text.split(q.question).join(' ');
      console.log(`${q.id} answer page:\n${answer.slice(0, 4000)}`);

      if (q.ask_match === 'feedback' || q.ask_match === 'poor') {
        const count = Number(values[0]);
        expect(appears(answer, String(count)) || page.rows === count).toBe(true);
      } else if (q.ask_match === 'any') {
        expect(values.some((v) => appears(answer, v))).toBe(true);
      } else {
        expect(values.filter((v) => !appears(answer, v))).toEqual([]);
      }
    });
  }
});
