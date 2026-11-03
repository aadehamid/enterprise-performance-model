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
  async function checkValueStreams(mobile = false) {
    if (mobile) {
      await page.setViewportSize({ width: 390, height: 844 });
      await page.locator("#back").click();
    }
    await page.locator("#query").fill("");
    await page.locator("#module").selectOption("value-stream");
    const expected = await page.evaluate(() => {
      const ns = "https://w3id.org/mpc/ontology/modules/value-stream/";
      const targets = (n, p) => n.values.filter(v => !v.literal && v.p === ns + p).map(v => byId.get(v.v));
      const sequence = n => Number(n.values.find(v => v.p === ns + "sequence").v);
      return data.nodes.filter(n => n.values.some(v => v.p === "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" && v.v === ns + "ValueStream"))
        .map(n => ({id: n.id, label: n.label, stages: targets(n, "hasStage").sort((a,b) => sequence(a)-sequence(b)).map(s => ({id:s.id, sequence:sequence(s), processes:targets(s,"hasProcess").map(p => ({id:p.id, realized:targets(p,"realizes").map(r=>r.id).sort()}))}))}));
    });
    assert.deepEqual(expected.map(n => n.label).sort(), ["Commercial Hydrocarbon Lifecycle", "Order to Cash"]);
    assert.equal(await page.locator("#stream-entry button").count(), expected.length);
    for (const stream of expected) {
      await page.locator("#stream-entry button").filter({hasText:stream.label}).click();
      assert.equal(await page.locator("#iri").textContent(), stream.id);
      assert.deepEqual(await page.locator("#stream-children button").evaluateAll(els=>els.map(el=>el.dataset.term)), stream.stages.map(s=>s.id));
      assert.deepEqual(await page.locator("#stream-children li").evaluateAll(els=>els.map(el=>el.value)), stream.stages.map(s=>s.sequence));
      for (const stage of stream.stages) {
        await page.locator(`#stream-children button[data-term="${stage.id}"]`).click();
        assert.equal(await page.locator("#iri").textContent(), stage.id);
        assert.deepEqual((await page.locator("#stream-children button").evaluateAll(els=>els.map(el=>el.dataset.term))).sort(), stage.processes.map(p=>p.id).sort());
        const process = stage.processes[0];
        await page.locator(`#stream-children button[data-term="${process.id}"]`).click();
        assert.equal(await page.locator("#iri").textContent(), process.id);
        assert.deepEqual((await page.locator("#stream-children button").evaluateAll(els=>els.map(el=>el.dataset.term))).sort(), process.realized);
        await page.locator(`#stream-parents button[data-term="${stage.id}"]`).click();
        await page.locator(`#stream-parents button[data-term="${stream.id}"]`).click();
      }
      if (mobile) await page.locator("#back").click();
    }
    await page.locator("#query").fill("has stage");
    assert.equal(await page.locator("#stream-entry").isVisible(), false);
    assert.ok(await page.locator("#results button").count());
    await page.locator("#query").fill("");
    if (mobile) await page.locator("#stream-entry button").first().click();
  }
  await checkValueStreams();
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
  await page.locator("#tree-mode").click();
  const moduleTrees = page.locator("#results > details");
  for (let index = 0; index < await moduleTrees.count(); index++) {
    const tree = moduleTrees.nth(index);
    await tree.locator(":scope > summary").click();
    await tree.locator(":scope > details > summary").click();
    await tree.locator(":scope > details button[data-term]").first().waitFor();
  }
  const hierarchyCoverage = await page.evaluate(() => {
    const rendered = new Set([...document.querySelectorAll("#results > details > details button[data-term]")].map(el => el.dataset.term));
    return {expected: data.nodes.length, rendered: rendered.size, missing: data.nodes.filter(n => !rendered.has(n.id)).map(n => n.id)};
  });
  assert.equal(hierarchyCoverage.rendered, hierarchyCoverage.expected);
  assert.deepEqual(hierarchyCoverage.missing, []);
  await page.locator("#list-mode").click();
  await page.locator("#query").fill("");
  assert.equal(await page.locator("#results > button").count(), 80);
  await page.locator("#pagination").click();
  assert.equal(await page.locator("#results > button").count(), 160);
  const lastResult = page.locator("#results > button").last();
  const lastId = await lastResult.getAttribute("data-term");
  await lastResult.click();
  assert.equal(await page.locator("#iri").textContent(), lastId);
  assert.ok(await page.locator("#results").evaluate(el => el.scrollTop > 0));

  const hub = await page.evaluate(() => data.nodes.find(n =>
    n.values.filter(v => !v.literal && byId.has(v.v)).length > 16).id);
  await page.locator("#query").fill(hub);
  await page.locator("#results > button").first().click();
  assert.equal(await page.locator("#relations button").count(), 8);
  await page.locator("#more-graph").click();
  assert.equal(await page.locator("#relations button").count(), 16);
  await page.locator("#reset-graph").click();
  assert.equal(await page.locator("#relations button").count(), 8);
  const neighborLabel = await page.locator("#graph g:not(.selected)").first().getAttribute("aria-label");
  await page.locator("#graph g:not(.selected)").first().focus();
  await page.keyboard.press("Enter");
  assert.equal(await page.locator("#title").textContent(), neighborLabel);
  assert.notEqual(await page.locator("#iri").textContent(), hub);
  await page.locator("main details > summary").first().click();
  assert.ok(await page.locator("#properties").innerText());
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
  await checkValueStreams(true);
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
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
      valueStreamDrilldown: true,
      graph: true,
      mobile: true,
    }),
  );
} finally {
  await browser.close();
}
