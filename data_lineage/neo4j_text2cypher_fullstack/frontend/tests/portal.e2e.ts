import { beforeEach, describe, test } from '@e2e-dev/web';
import { expect } from 'e2e';

const ANSWER_TIMEOUT = 120_000;

type GraphSample = {
  scale: number;
  panX: number;
  panY: number;
  nodes: { id: string; x: number; y: number; sx: number; sy: number }[];
  bounds: { left: number; top: number; right: number; bottom: number };
};

async function readGraph(browser: { evaluate<T>(fn: () => T | Promise<T>): Promise<T> }): Promise<GraphSample | null> {
  return browser.evaluate(() => {
    const root = document.querySelector('.nvl-canvas-container');
    if (!(root instanceof HTMLElement)) return null;
    const fiberKey = Object.keys(root).find((key) => key.startsWith('__reactFiber'));
    if (!fiberKey) return null;
    let fiber = (root as unknown as Record<string, any>)[fiberKey];
    let nvl: any = null;
    const seen = new Set<unknown>();
    let guard = 0;
    while (fiber && guard < 80 && !seen.has(fiber)) {
      seen.add(fiber);
      guard += 1;
      let hook = fiber.memoizedState;
      let hooks = 0;
      while (hook && hooks < 40) {
        const current = hook.memoizedState?.current;
        if (current && typeof current.getScale === 'function') {
          nvl = current;
          break;
        }
        hook = hook.next;
        hooks += 1;
      }
      if (nvl) break;
      fiber = fiber.return;
    }
    if (!nvl) return null;
    const rect = root.getBoundingClientRect();
    const pan = nvl.getPan();
    return {
      scale: nvl.getScale(),
      panX: pan.x,
      panY: pan.y,
      nodes: nvl.getNodes().map((node: any) => ({
        id: String(node.id),
        x: node.x,
        y: node.y,
        sx: rect.left + node.clientPosition.x,
        sy: rect.top + node.clientPosition.y,
      })),
      bounds: { left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom },
    };
  });
}

async function settledGraph(browser: { evaluate<T>(fn: () => T | Promise<T>): Promise<T> }): Promise<GraphSample> {
  let previous = await readGraph(browser);
  for (let attempt = 0; attempt < 20; attempt += 1) {
    await browser.evaluate(() => new Promise((resolve) => setTimeout(resolve, 400)));
    const next = await readGraph(browser);
    if (
      previous &&
      next &&
      next.nodes.length > 0 &&
      Math.abs(next.scale - previous.scale) < 0.001 &&
      next.nodes.every((node, index) => {
        const prior = previous?.nodes[index];
        return prior && Math.abs(node.x - prior.x) < 1 && Math.abs(node.y - prior.y) < 1;
      })
    ) {
      return next;
    }
    previous = next;
  }
  if (!previous || previous.nodes.length === 0) throw new Error('graph did not render');
  return previous;
}

function emptyCanvasPoint(sample: GraphSample): { x: number; y: number } | null {
  const { left, top, right, bottom } = sample.bounds;
  for (let y = bottom - 36; y > top + 24; y -= 28) {
    for (let x = left + 36; x < right - 24; x += 28) {
      const hit = sample.nodes.some((node) => Math.hypot(node.sx - x, node.sy - y) < 30);
      if (!hit) return { x, y };
    }
  }
  return null;
}

describe('semantic portal', () => {
  beforeEach(async ({ app, screen }) => {
    await app.open('/');
    await expect(screen.getByText('Lagos Refining & Supply Company Semantic Portal').first()).toBeVisible();
  });

  test('loads with the header and an empty dashboard', async ({ screen }) => {
    await expect(screen.getByRole('navigation', 'main navigation')).toBeVisible();
    await expect(screen.getByRole('button', 'Toggle dark mode')).toBeVisible();
    await expect(screen.getByPlaceholder('Ask me a question (Press Shift+Enter for new line)...')).toBeVisible();
    await expect(
      screen.getByText('The interactive lineage graph, tabular view, and Cypher tab render here.'),
    ).toBeVisible();
  });

  test('theme toggle switches between dark and light', async ({ screen, browser }) => {
    const body = browser.locator('body');
    const toggle = screen.getByRole('button', 'Toggle dark mode');

    await expect(browser).toHaveClass(body, /ndl-theme-dark/);
    await expect(screen.getByRole('image', 'sun')).toBeVisible();

    await toggle.tap();
    await expect(browser).not.toHaveClass(body, /ndl-theme-dark/);
    await expect(screen.getByRole('image', 'moon')).toBeVisible();

    await toggle.tap();
    await expect(browser).toHaveClass(body, /ndl-theme-dark/);
    await expect(screen.getByRole('image', 'sun')).toBeVisible();
  });

  test('answers a Gold table count with 43', async ({ screen }) => {
    await screen.getByPlaceholder('Ask me a question (Press Shift+Enter for new line)...').fill('How many Gold tables are there?');
    await screen.getByRole('button', 'Submit').tap();

    await expect(screen.getByRole('button', 'Stop')).toBeVisible();
    await expect(screen.getByRole('button', 'Submit')).toBeVisible({ timeout: ANSWER_TIMEOUT });
    await expect(screen.getByRole('button', 'Thumbs up')).toBeVisible();
    await expect(screen.getByText(/\b43\b[^:]*Gold|Gold[^:]*\b43\b/i).first()).toBeVisible();
  });

  test('a greeting gets a conversational reply and leaves the dashboard empty', async ({ screen }) => {
    await screen.getByPlaceholder('Ask me a question (Press Shift+Enter for new line)...').fill('hey');
    await screen.getByRole('button', 'Submit').tap();

    await expect(screen.getByRole('button', 'Thumbs up')).toBeEnabled({ timeout: ANSWER_TIMEOUT });
    await expect(screen.getByText(/How many Gold tables are there\?/).first()).toBeVisible();
    await expect(
      screen.getByText('The interactive lineage graph, tabular view, and Cypher tab render here.'),
    ).toBeVisible();
    await expect(screen.getByRole('button', 'Graph View')).toHaveCount(0);
  });

  test('stop cancels a pending ask', async ({ screen, browser }) => {
    await screen.getByPlaceholder('Ask me a question (Press Shift+Enter for new line)...').fill('How many Gold tables are there?');
    await screen.getByRole('button', 'Submit').tap();
    await screen.getByRole('button', 'Stop').tap();

    await expect(screen.getByRole('button', 'Submit')).toBeVisible();
    await expect(screen.getByText('How many Gold tables are there?')).toBeVisible();
    await expect(screen.getByRole('button', 'Thumbs up')).toHaveCount(0);
    expect(await browser.evaluate(() => document.querySelectorAll('.loader').length)).toBe(0);
  });

  test('answer metadata dialog and feedback box open and close', async ({ screen, browser }) => {
    await screen.getByPlaceholder('Ask me a question (Press Shift+Enter for new line)...').fill('How many Gold tables are there?');
    await screen.getByRole('button', 'Submit').tap();
    await expect(screen.getByRole('button', 'Thumbs up')).toBeEnabled({ timeout: ANSWER_TIMEOUT });

    await screen.getByRole('button', 'Information').tap();
    await expect(screen.getByRole('dialog', 'Lineage Query Metadata')).toBeVisible();
    await browser.keyboard.press('Escape');
    await expect(screen.getByRole('dialog')).toHaveCount(0);

    await screen.getByRole('button', 'Thumbs up').tap();
    await expect(screen.getByRole('textbox', 'Feedback notes')).toBeVisible();
    await screen.getByRole('button', 'Cancel').tap();
    await expect(screen.getByRole('textbox', 'Feedback notes')).toHaveCount(0);
  });

  test('a new answer resets the dashboard to its own default tab', async ({ screen }) => {
    const input = screen.getByPlaceholder('Ask me a question (Press Shift+Enter for new line)...');
    await input.fill('Show the tables in the wholesale_core schema');
    await screen.getByRole('button', 'Submit').tap();
    await expect(screen.getByRole('button', 'Fit to screen')).toBeVisible({ timeout: ANSWER_TIMEOUT });
    await expect(screen.getByRole('button', 'Submit')).toBeVisible({ timeout: ANSWER_TIMEOUT });
    await screen.getByRole('button', 'Cypher').tap();

    await input.fill('How many Gold tables are there?');
    await screen.getByRole('button', 'Submit').tap();
    await expect(screen.getByRole('button', 'Submit')).toBeVisible({ timeout: ANSWER_TIMEOUT });
    await expect(screen.getByRole('table')).toBeVisible({ timeout: ANSWER_TIMEOUT });
    await expect(screen.getByRole('cell').filter({ hasText: '43' }).first()).toBeVisible();
  });

  test('renders the graph for wholesale_core and toggles the table grid', async ({ screen, browser }) => {
    await browser.setViewport({ width: 1600, height: 1000 });
    await screen
      .getByPlaceholder('Ask me a question (Press Shift+Enter for new line)...')
      .fill('Show the tables in the wholesale_core schema');
    await screen.getByRole('button', 'Submit').tap();

    const graphTab = screen.getByRole('button', 'Graph View');
    const tableTab = screen.getByRole('button', 'Table Grid');
    await expect(graphTab).toBeVisible({ timeout: ANSWER_TIMEOUT });
    await expect(screen.getByRole('button', 'Fit to screen')).toBeVisible();
    await expect(screen.getByText('Gold', { exact: true })).toBeVisible();
    await expect(screen.getByRole('button', 'Submit')).toBeVisible({ timeout: ANSWER_TIMEOUT });

    const before = await settledGraph(browser);
    const node = before.nodes[0];
    await browser.mouse.move(node.sx, node.sy);
    await browser.mouse.wheel(0, -400);
    const zoomed = await readGraph(browser);
    if (!zoomed) throw new Error('graph missing after wheel');
    expect(zoomed.scale).toBeGreaterThan(before.scale + 0.05);

    const dragged = zoomed.nodes.find((item) => item.id === node.id) ?? zoomed.nodes[0];
    await browser.mouse.move(dragged.sx, dragged.sy);
    await browser.mouse.down();
    await browser.mouse.move(dragged.sx + 140, dragged.sy + 80);
    await browser.mouse.up();
    const afterDrag = await readGraph(browser);
    if (!afterDrag) throw new Error('graph missing after drag');
    const moved = afterDrag.nodes.find((item) => item.id === dragged.id);
    if (!moved) throw new Error('dragged node missing');
    expect(Math.hypot(moved.x - dragged.x, moved.y - dragged.y)).toBeGreaterThan(20);

    const blank = emptyCanvasPoint(afterDrag);
    if (!blank) throw new Error('no empty canvas point to pan from');
    await browser.mouse.move(blank.x, blank.y);
    await browser.mouse.down();
    await browser.mouse.move(blank.x + 160, blank.y - 90);
    await browser.mouse.up();
    const afterPan = await readGraph(browser);
    if (!afterPan) throw new Error('graph missing after pan');
    expect(Math.hypot(afterPan.panX - afterDrag.panX, afterPan.panY - afterDrag.panY)).toBeGreaterThan(10);

    await tableTab.tap();
    await expect(screen.getByRole('table')).toBeVisible();
    await expect(screen.getByRole('columnheader').first()).toBeVisible();
    await expect(screen.getByRole('cell').filter({ hasText: 'wholesale_core.' }).first()).toBeVisible();
    await expect(screen.getByRole('button', 'Fit to screen')).toBeHidden();

    await graphTab.tap();
    await expect(screen.getByRole('table')).toBeHidden();
    await expect(screen.getByRole('button', 'Fit to screen')).toBeVisible();
  });
});
