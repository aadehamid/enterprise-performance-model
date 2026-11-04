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
  assert.equal(await page.locator("#overview").getAttribute("data-view"), "modules");
  await page.locator("#view-browse").click();
  await page.locator("#results button").first().waitFor();
  const initial = await page.locator("#summary").innerText();
  assert.match(initial, /terms in release/);
  async function checkBrowseContext() {
    await page.locator("#view-browse").click();
    await page.locator("#module").selectOption("value-stream");
    assert.equal(await page.locator("#stream-entry").isVisible(), true);
    async function openModuleBrowser(name, expected = name) {
      await page.locator("#view-modules").click();
      await page.locator(`#module-catalogue button[data-module="${name}"]`).click();
      await page.locator("#browse-module").click();
      assert.equal(await page.locator("#module").inputValue(), expected);
    }
    await openModuleBrowser("party");
    assert.equal(await page.locator("#stream-entry").isVisible(), false);
    await page.locator("#view-browse").click();
    assert.equal(await page.locator("#module").inputValue(), "value-stream");
    assert.equal(await page.locator("#stream-entry").isVisible(), true,
      "restoring the value-stream browser must restore its stream entry points");
    await openModuleBrowser("value-stream");
    assert.equal(await page.locator("#stream-entry").isVisible(), true);
    await openModuleBrowser("party");
    assert.equal(await page.locator("#stream-entry").isVisible(), false,
      "restoring the party browser must hide stale value-stream entry points");
    await page.locator("#module").selectOption("");
    const allResults = await page.locator("#results").innerHTML();
    const allSummary = await page.locator("#summary").innerText();
    await openModuleBrowser("value-stream");
    await openModuleBrowser("party", "");
    assert.equal(await page.locator("#results").innerHTML(), allResults,
      "restoring All modules must preserve the matching cached results");
    assert.equal(await page.locator("#summary").innerText(), allSummary);
    assert.equal(await page.locator("#stream-entry").isVisible(), false);
    await page.locator("#module").selectOption("party");
  }
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
    await page.locator("#tree-mode").click();
    const moduleTree = page.locator("#results > details").filter({hasText:/^value-stream ·/});
    await moduleTree.locator(":scope > summary").click();
    await moduleTree.locator(":scope > ul > li").first().waitFor();
    const roots = moduleTree.locator(":scope > ul > li > details");
    assert.equal(await roots.count(), expected.length);
    for (let i = 0; i < expected.length; i++) {
      const root = roots.nth(i);
      const id = await root.locator(":scope > button").getAttribute("data-term");
      const stream = expected.find(n => n.id === id);
      assert.ok(stream);
      await root.locator(":scope > summary").click();
      await root.locator(":scope > ul > li").first().waitFor();
      assert.deepEqual(await root.locator(":scope > ul > li > details > button").evaluateAll(els=>els.map(el=>el.dataset.term)), stream.stages.map(s=>s.id));
      const stageTree = root.locator(":scope > ul > li > details").first();
      await stageTree.locator(":scope > summary").click();
      await stageTree.locator(":scope > ul > li").first().waitFor();
      assert.deepEqual((await stageTree.locator(":scope > ul > li > button").evaluateAll(els=>els.map(el=>el.dataset.term))).sort(), stream.stages[0].processes.map(p=>p.id).sort());
    }
    await page.locator("#list-mode").click();
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
  // Derive the customer model's connected component from the released RDF, independently
  // of the UI's presentation groups. Verify every entity, edge and lifecycle mapping.
  const customer = await page.evaluate(() => {
    const ns = "https://w3id.org/mpc/ontology/modules/party/", rdfs = "http://www.w3.org/2000/01/rdf-schema#";
    const refs = (n, p) => n.values.filter(v => !v.literal && v.p === p).map(v => v.v);
    const classes = new Set(data.nodes.filter(n => n.id.startsWith(ns) && n.kind === "Class").map(n => n.id));
    const edges = [];
    for (const n of data.nodes) {
      if (n.kind === "Property") for (const from of refs(n, rdfs + "domain"))
        for (const to of refs(n, rdfs + "range")) if (classes.has(from) && classes.has(to)) edges.push([from,n.id,to]);
      if (classes.has(n.id)) for (const p of [rdfs + "subClassOf", "http://www.w3.org/2002/07/owl#disjointWith"])
        for (const to of refs(n,p)) if (classes.has(to)) edges.push([n.id,p,to]);
    }
    const ids = new Set([ns + "Party"]);
    let changed = true;
    while (changed) {
      const before = ids.size;
      for (const [from,,to] of edges) if (ids.has(from) || ids.has(to)) {ids.add(from);ids.add(to);}
      changed = ids.size !== before;
    }
    const stages = refs(byId.get(ns + "lifecycle-stage"), "http://www.w3.org/2004/02/skos/core#hasTopConcept").map(id => {
      const n = byId.get(id);
      return {id, label:n.label, processes:refs(n,ns+"stageProcess"), systems:refs(n,ns+"correspondsTo").map(id=>({id,targets:refs(byId.get(id),ns+"stageSystem")}))};
    });
    return {ids:[...ids].sort(), edges:edges.filter(([from,,to])=>ids.has(from)&&ids.has(to)).sort(), stages};
  });
  assert.equal(customer.ids.length, 17, "The released customer conceptual model has 17 entity classes");
  assert.equal(customer.stages.length, 6);
  for (const width of [1440, 390]) {
    await page.setViewportSize({width,height:900});
    await page.locator("#view-lifecycle").click();
    assert.equal(await page.locator("#layout").isVisible(), false);
    assert.equal(await page.locator("#overview").isVisible(), true);
    assert.deepEqual((await page.locator(".lifecycle-card").evaluateAll(els=>els.map(e=>e.dataset.stage))).sort(), customer.stages.map(s=>s.id).sort());
    for (const stage of customer.stages) {
      const card = page.locator(`.lifecycle-card[data-stage="${stage.id}"]`);
      await card.locator("summary").click();
      const expected = [...stage.processes, ...stage.systems.flatMap(s=>[s.id,...s.targets])].sort();
      assert.deepEqual((await card.locator("details [data-term]").evaluateAll(els=>els.map(e=>e.dataset.term))).sort(), expected);
      for (const system of stage.systems) assert.deepEqual((await card.locator(`.system-stage[data-stage="${system.id}"] li button`).evaluateAll(els=>els.map(e=>e.dataset.term))).sort(), system.targets.sort());
      await card.locator(":scope > button").click();
      assert.equal(await page.locator("#iri").textContent(),stage.id);
      assert.deepEqual((await page.locator("#lifecycle-links [data-term]").evaluateAll(els=>els.map(e=>e.dataset.term))).sort(), expected);
      await page.locator("#lifecycle-links > ul button").first().click();
      assert.ok(stage.processes.includes(await page.locator("#iri").textContent()));
      await page.locator("#return-overview").click();
      assert.equal(await page.locator("#overview").getAttribute("data-view"), "lifecycle");
    }
    await page.reload();
    assert.equal(await page.locator("#overview").getAttribute("data-view"), "lifecycle");
    await page.locator("#view-model").click();
    await page.locator("#model-reset").click();
    assert.deepEqual((await page.locator("#model-diagram [data-entity]").evaluateAll(els=>els.map(e=>e.dataset.entity))).sort(),customer.ids);
    const edgeRows = () => page.locator("#model-relations tbody tr").evaluateAll(els=>els.map(e=>[e.dataset.source,e.dataset.predicate,e.dataset.target]).sort());
    assert.deepEqual(await edgeRows(), customer.edges);
    assert.equal(await page.locator("#model-diagram .model-edge").count(),customer.edges.length);
    for (const id of customer.ids) {
      const node=page.locator(`#model-diagram [data-entity="${id}"]`);
      await node.focus(); await page.keyboard.press("Enter");
      assert.equal(await node.getAttribute("aria-pressed"),"true");
      assert.deepEqual(await edgeRows(),customer.edges.filter(([a,,b])=>a===id||b===id));
      await page.locator("#model-focus [data-term]").click();
      assert.equal(await page.locator("#iri").textContent(),id);
      await page.locator("#return-overview").click();
      assert.equal(await page.locator(`#model-diagram [data-entity="${id}"]`).getAttribute("aria-pressed"),"true");
    }
    await page.locator("#model-reset").click();
    const property = customer.edges.find(([,p])=>p.startsWith("https://w3id.org/mpc/ontology/modules/party/"))[1];
    await page.locator(`#model-relations [data-term="${property}"]`).first().click();
    assert.equal(await page.locator("#iri").textContent(),property);
    await page.goBack();
    assert.equal(await page.locator("#overview").getAttribute("data-view"),"model");
    await page.reload();
    assert.equal(await page.locator("#overview").isVisible(),true);
    assert.equal(await page.locator("#overview").getAttribute("data-view"),"model");
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    const scroll=page.locator(".model-scroll");
    await scroll.evaluate(e=>e.scrollLeft=e.scrollWidth);
    await page.locator('#model-diagram [aria-label="product"]').click();
    assert.equal(await page.locator("#model-focus h3").textContent(),"product");
    await page.locator("#view-browse").click();
    assert.equal(await page.locator("#overview").isVisible(),false);
    assert.equal(await page.locator("aside").isVisible(),true);
  }
  const catalogue = await page.evaluate(() => {
    const root = "https://w3id.org/mpc/ontology/modules/";
    const names = [...new Set(data.nodes.flatMap(n=>n.modules.map(m=>m.name)))].sort();
    return names.map(name=>{
      const node=data.nodes.find(n=>n.id===root+name);
      const terms=data.nodes.filter(n=>n.modules.some(m=>m.name===name)&&!data.supportingKinds.includes(n.kind));
      return {name,label:node.label,terms:terms.length,groups:Object.fromEntries(["Class","Concept scheme","Property","Individual"].map(kind=>[kind,terms.filter(n=>n.kind===kind).map(n=>n.id).sort()])),deps:node.values.filter(v=>!v.literal&&["http://purl.org/dc/terms/requires","http://www.w3.org/2002/07/owl#imports"].includes(v.p)).map(v=>v.v).sort(),version:node.values.find(v=>v.p==="http://www.w3.org/2002/07/owl#versionInfo").v};
    });
  });
  const moduleEdges=catalogue.flatMap(m=>[...new Set(m.deps.map(iri=>catalogue.find(target=>iri==="https://w3id.org/mpc/ontology/modules/"+target.name || iri==="https://w3id.org/mpc/ontology/modules/"+target.name+"/"+target.version)?.name).filter(Boolean))].map(target=>[m.name,target])).sort();
  const expectedStreams = await page.evaluate(()=>data.nodes.filter(n=>n.values.some(v=>!v.literal&&v.p==="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"&&v.v==="https://w3id.org/mpc/ontology/modules/value-stream/ValueStream")).map(n=>{
    const ns="https://w3id.org/mpc/ontology/modules/value-stream/";
    const refs=(x,p)=>x.values.filter(v=>!v.literal&&v.p===ns+p).map(v=>byId.get(v.v));
    return {id:n.id,label:n.label,stages:refs(n,"hasStage").map(s=>({id:s.id,sequence:Number(s.values.find(v=>v.p===ns+"sequence").v),processes:refs(s,"hasProcess").map(p=>p.id).sort()})).sort((a,b)=>a.sequence-b.sequence)};
  }));
  for (const width of [1440,390]) {
    await page.setViewportSize({width,height:900});
    await page.locator("#view-modules").click();
    assert.deepEqual((await page.locator("#module-catalogue article").evaluateAll(els=>els.map(e=>e.dataset.module))).sort(),catalogue.map(m=>m.name));
    await page.locator("#module-query").fill("no-module-matches-this");
    assert.equal(await page.locator("#module-catalogue article").count(),0);
    await page.locator("#module-query").fill("");
    await page.locator("#module-map > summary").click();
    await page.locator("#module-diagram").waitFor();
    assert.deepEqual((await page.locator("#module-diagram [data-module]").evaluateAll(els=>els.map(e=>e.dataset.module))).sort(),catalogue.map(m=>m.name));
    assert.deepEqual(await page.locator("#module-diagram .dependency-edge").evaluateAll(els=>els.map(e=>[e.dataset.source,e.dataset.target]).sort()),moduleEdges);
    await page.locator('#module-diagram [data-module="party"]').focus();await page.keyboard.press("Enter");
    assert.equal(await page.locator("#overview").getAttribute("data-view"),"module:party");
    await page.locator("#view-modules").click();
    for (const mod of catalogue) {
      await page.locator(`#module-catalogue button[data-module="${mod.name}"]`).click();
      assert.equal(await page.locator("#overview > h2").textContent(),mod.label);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
      assert.deepEqual(await page.locator("#module-dependencies [data-reference]").evaluateAll(els=>els.map(e=>e.dataset.reference).sort()),mod.deps);
      assert.deepEqual((await page.locator("#module-used-by [data-module]").evaluateAll(els=>els.map(e=>e.dataset.module))).sort(),moduleEdges.filter(([,to])=>to===mod.name).map(([from])=>from).sort());
      for (const [kind,title] of [["Class","Classes"],["Concept scheme","Concept schemes"],["Property","Properties"],["Individual","Individuals"]]) {
        const group=page.locator(`.term-group[data-group="${title}"]`);
        if (!mod.groups[kind].length) {assert.equal(await group.count(),0);continue;}
        assert.match(await group.locator("summary").textContent(),new RegExp(mod.groups[kind].length.toLocaleString()+"$"));
        if (!(await group.getAttribute("open")!==null)) await group.locator("summary").click();
        await group.locator(".term-group-list button").first().waitFor();
        const visible=await group.locator(".term-group-list button").evaluateAll(els=>els.map(e=>e.dataset.term));
        assert.ok(visible.every(id=>mod.groups[kind].includes(id)));
        if (mod.groups[kind].length>12) {await group.locator(":scope > button").click();assert.equal(await group.locator(".term-group-list button").count(),Math.min(52,mod.groups[kind].length));}
      }
      const term=page.locator(".term-group-list button:visible").first(),id=await term.getAttribute("data-term");
      await term.click();assert.equal(await page.locator("#iri").textContent(),id);
      await page.locator("#return-overview").click();
      assert.equal(await page.locator("#overview").getAttribute("data-view"),"module:"+mod.name);
      await page.locator("#browse-module").click();
      assert.equal(await page.locator("#module").inputValue(),mod.name);
      assert.match(await page.locator("#summary").textContent(),new RegExp("^"+mod.terms.toLocaleString()+" results"));
      await page.reload();assert.equal(await page.locator("#module").inputValue(),mod.name);
      await page.locator("#view-modules").click();
    }
    for (const stream of expectedStreams) {
      const nav=page.locator(`#stream-nav button[data-view="stream:${stream.id}"]`);
      await nav.click();assert.equal(await nav.getAttribute("aria-current"),"page");
      assert.equal(await page.locator("#overview > h2").textContent(),stream.label);
      assert.deepEqual(await page.locator("#stream-overview-stages > li").evaluateAll(els=>els.map(e=>[e.dataset.stage,e.value])),stream.stages.map(s=>[s.id,s.sequence]));
      for (const stage of stream.stages) {
        const card=page.locator(`#stream-overview-stages > li[data-stage="${stage.id}"]`);
        await card.locator("summary").click();
        assert.deepEqual((await card.locator("details [data-term]").evaluateAll(els=>els.map(e=>e.dataset.term))).sort(),stage.processes);
        await card.locator(":scope > button").click();assert.equal(await page.locator("#iri").textContent(),stage.id);
        await page.locator("#return-overview").click();
      }
      await page.reload();assert.equal(await page.locator("#overview").getAttribute("data-view"),"stream:"+stream.id);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    }
  }
  for (const width of [1440, 390]) {
    await page.setViewportSize({width,height:900});
    await page.goto(pathToFileURL(resolve(process.argv[2])).href);
    await checkBrowseContext();
    await page.goto(pathToFileURL(resolve(process.argv[2])).href);
    assert.equal(await page.locator("#overview").getAttribute("data-view"),"modules");
    await page.locator("#module-query").fill("party");
    await page.locator('#module-catalogue button[data-module="party"]').click();
    const classes=page.locator('.term-group[data-group="Classes"]');
    if (!(await classes.evaluate(el=>el.open))) await classes.locator("summary").click();
    await classes.locator(".term-group-list button").first().click();
    const selectedClass = await page.locator("#iri").textContent();
    await page.locator("#view-lifecycle").click(); await page.goBack();
    await page.waitForFunction(id => !document.getElementById("layout").hidden && document.getElementById("iri").textContent === id, selectedClass);
    assert.match(await page.locator("#return-overview").textContent(), /Party/);
    await page.goBack(); assert.equal(await page.locator("#overview").getAttribute("data-view"),"module:party");
    await page.goForward(); await page.locator("#breadcrumbs button").last().click();
    assert.equal(await classes.evaluate(el=>el.open),true);
    await page.locator("#breadcrumbs button").first().click();
    assert.equal(await page.locator("#module-query").inputValue(),"party");
    await page.locator("#view-browse").click();
    await page.locator("#module").selectOption("party");
    await page.locator("#term-type").selectOption("Class");
    await page.locator("#query").fill("customer");
    const expected=await page.evaluate(()=>ordered.filter(n=>n.kind==="Class" && n.modules.some(m=>m.name==="party") && searchText.get(n.id).includes("customer")).map(n=>n.id));
    assert.deepEqual(await page.locator("#results button[data-term]").evaluateAll(els=>els.map(el=>el.dataset.term)),expected);
    await page.locator("#results button[data-term]").first().click();
    await page.locator("#breadcrumbs button").first().click();
    assert.equal(await page.locator("#query").inputValue(),"customer");
    assert.equal(await page.locator("#term-type").inputValue(),"Class");
    await page.locator("#view-model").click();
    await page.locator("#view-browse").click();
    assert.equal(await page.locator("#query").inputValue(),"customer");
    await page.locator("#query").fill(""); await page.locator("#term-type").selectOption("");
    await page.locator("#tree-mode").click();
    const tree=page.locator("#results > details").first();
    await tree.locator(":scope > summary").click();
    await page.locator("#view-model").click();await page.locator("#view-browse").click();
    assert.equal(await tree.evaluate(el=>el.open),true);
    for (const view of ["modules","model","lifecycle"]) {
      await page.locator("#view-"+view).click();await page.locator("#global-search-open").click();
      await page.locator("#global-query").fill("customer");await page.locator("#global-type").selectOption("Class");
      const found=await page.locator("#global-results button[data-result]").evaluateAll(els=>els.map(el=>el.dataset.result).filter(id=>byId.has(id)));
      const expectedGlobal=await page.evaluate(()=>ordered.filter(n=>n.kind==="Class" && searchText.get(n.id).includes("customer")).map(n=>n.id).sort());
      assert.deepEqual(found.sort(),expectedGlobal);
      const first=page.locator('#global-results button[data-result^="https:"]').first(), id=await first.getAttribute("data-result");
      await first.click();assert.equal(await page.locator("#iri").textContent(),id);
      await page.locator("#breadcrumbs button").filter({hasText:"Search results"}).click();
      assert.equal(await page.locator("#global-query").inputValue(),"customer");
      assert.equal(await page.locator("#global-type").inputValue(),"Class");
      await page.locator("#global-search-close").click();
    }
    await page.locator("#global-search-open").click();
    await page.locator("#global-type").selectOption(""); await page.locator("#global-query").fill("process");
    assert.equal(await page.locator('#global-results button[data-result^="https:"]').count(),80);
    await page.locator("#global-more").click();
    assert.equal(await page.locator('#global-results button[data-result^="https:"]').count(),160);
    await page.locator("#global-query").fill("no-such-ontology-term-987654");
    assert.equal(await page.locator("#global-results button").count(),0);
    await page.locator("#global-type").selectOption("Constraint");
    assert.equal(await page.locator("#global-support").isChecked(),true);
    await page.locator("#global-support").uncheck(); assert.equal(await page.locator("#global-type").inputValue(),"");
    await page.locator("#global-query").fill("Order to Cash");
    await page.locator('#global-results button[data-result^="stream:"]').click();
    assert.match(await page.locator("#overview").getAttribute("data-view"),/^stream:/);
    await page.locator("#global-search-open").click();await page.locator("#global-query").fill("party");
    await page.locator('#global-results button[data-result="module:party"]').click();
    assert.equal(await page.locator("#overview").getAttribute("data-view"),"module:party");
    for (const [view,id] of [["model","model-diagram"],["modules","module-diagram"]]) {
      await page.locator("#view-"+view).click();
      if (view==="modules") {
        const map=page.locator("#module-map"); if (!(await map.evaluate(el=>el.open))) await map.locator(":scope > summary").click();
      }
      const shell=page.locator(".diagram-shell").filter({has:page.locator("#"+id)});
      await shell.locator('[data-action="zoom-in"]').click();assert.equal(await shell.locator("output").textContent(),"125%");
      await shell.locator('[data-action="zoom-out"]').click();assert.equal(await shell.locator("output").textContent(),"100%");
      await shell.locator('[data-action="fit"]').click();
      assert.equal(await shell.locator(".model-scroll").evaluate(el=>el.scrollWidth<=el.clientWidth+2),true);
      const zoom=await shell.locator("output").textContent();
      await shell.locator('[data-action="fullscreen"]').click();
      assert.equal(await page.locator(".diagram-dialog").evaluate(el=>el.open),true);
      await page.keyboard.press("Escape");assert.equal(await page.locator(".diagram-dialog").count(),0);
      assert.equal(await shell.locator("output").textContent(),zoom);
      await shell.locator('[data-action="fullscreen"]').click();
      if (view==="modules") {
        await page.locator('#module-diagram [data-module="party"]').click();
        assert.equal(await page.locator(".diagram-dialog").count(),0);
        assert.equal(await page.locator("#overview").getAttribute("data-view"),"module:party");
      } else await shell.locator('[data-action="fullscreen"]').click();
    }
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.screenshot({path:`/tmp/epm-viewer-navigation-review/navigation-${width}.png`});
  }
  assert.deepEqual(errors, []);
  assert.equal(network, 0);
  console.log(
    JSON.stringify({
      fileProtocol: true,
      networkRequests: network,
      pageErrors: errors,
      search: true,
      globalSearch: true,
      termTypeFilters: true,
      preservedNavigation: true,
      diagramControls: true,
      modules: true,
      hierarchy: true,
      valueStreamDrilldown: true,
      customerLifecycle: true,
      customerConceptualModel: true,
      moduleOverviews: true,
      valueStreamOverviews: true,
      graph: true,
      mobile: true,
    }),
  );
} finally {
  await browser.close();
}
