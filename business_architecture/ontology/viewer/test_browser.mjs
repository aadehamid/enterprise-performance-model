import { createRequire } from "node:module";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
const { chromium } = createRequire(import.meta.url)("playwright-core");
import assert from "node:assert/strict";
const browser = await chromium.launch({
  executablePath:
    process.env.CHROME_PATH ||
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
});
try {
  const page = await browser.newPage({
    viewport: { width: 1440, height: 900 },
  });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  let network = 0;
  await page.route(/^https?:/, (route) => {
    network++;
    return route.abort();
  });
  assert.ok(process.argv[2], "Pass the generated viewer HTML path");
  await page.goto(pathToFileURL(resolve(process.argv[2])).href);
  await page.locator("#results button").first().waitFor();
  const initial = await page.locator("#summary").innerText();
  assert.match(initial, /terms in release/);
  for (const name of ["core", "logical-model", "technical-graph"]) {
    await page.locator("#module").selectOption(name);
    await page.locator("#query").fill("");
    const first = page.locator("#results button").first();
    await first.click();
    assert.match(await page.locator("#modules").innerText(), new RegExp(name));
    assert.ok(await page.locator("#graph svg").count());
  }
  await page.locator("#module").selectOption("");
  await page.locator("#query").fill("no-such-ontology-term-913404");
  assert.match(await page.locator("#results").innerText(), /No matching terms/);
  await page.locator("#query").fill("customer");
  assert.ok(await page.locator("#results button").count());
  await page.locator("#results button").first().click();
  const iri = await page.locator("#iri").textContent();
  assert.ok(page.url().includes(encodeURIComponent(iri)));
  await page.evaluate(() => {
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: {
        writeText: async (text) => {
          window.copiedText = text;
        },
      },
    });
  });
  await page.locator("#copy").click();
  assert.equal(await page.evaluate(() => window.copiedText), iri);
  assert.match(await page.locator("#message").innerText(), /copied/);
  await page.reload();
  await page.locator("#title").waitFor();
  assert.equal(await page.locator("#iri").textContent(), iri);
  await page.locator("#support").check();
  await page.locator("#query").fill("");
  await page.locator("#module").selectOption("");
  const coverage = await page.evaluate(() => {
    const nodes = filtered();
    const present = new Set(nodes.map((n) => n.id));
    return {
      expected: data.nodes.length,
      found: present.size,
      missing: data.nodes.filter((n) => !present.has(n.id)).length,
      allSearchable: data.nodes.every((n) =>
        searchText.get(n.id).includes(n.id.toLowerCase()),
      ),
    };
  });
  assert.equal(coverage.missing, 0);
  assert.equal(coverage.expected, coverage.found);
  assert.equal(coverage.allSearchable, true);
  await page.locator("#query").fill("customer");

  await page.locator("#tree-mode").click();
  await page
    .locator("#results>details")
    .first()
    .locator(":scope > summary")
    .click();
  await page.locator("#results>details[open] details>summary").first().click();
  await page.locator("#results .term-button:visible").first().waitFor();
  await page.locator("#results .term-button:visible").first().click();
  assert.ok(await page.locator("#results > details[open]").count(), "Selecting a term must retain the open hierarchy");
  await page.locator("#about").click();
  assert.match(await page.locator("#release-pin").innerText(), /81f2f63b/);
  await page.locator("#close-about").click();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator("#back").click();
  assert.equal(await page.locator("aside").isVisible(), true);
  await page.locator("#list-mode").click();
  await page.locator("#results button").first().click();
  assert.equal(await page.locator("main").isVisible(), true);
  assert.equal(await page.locator("aside").isVisible(), false);
  assert.equal(
    await page.evaluate(
      () => document.documentElement.scrollWidth > innerWidth,
    ),
    false,
  );
  assert.deepEqual(errors, []);
  assert.equal(network, 0);
  console.log(
    JSON.stringify({
      fileProtocol: true,
      networkRequests: network,
      pageErrors: errors,
      search: true,
      modules: true,
      hierarchy: true,
      graph: true,
      mobile: true,
    }),
  );
} finally {
  await browser.close();
}
