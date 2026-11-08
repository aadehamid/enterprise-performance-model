import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const engines=createRequire(import.meta.url)('playwright-core');
const engine=process.env.TEST_BROWSER||'chromium';
assert.ok(process.argv[2] && process.argv[3],'Pass an artifact and evidence directory');
const artifact=resolve(process.argv[2]), evidence=resolve(process.argv[3]);
await mkdir(evidence,{recursive:true});
const browser=await engines[engine].launch(engine==='chromium'?{executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true}:{headless:true});
const errors=[],requests=[],results=[];
const base=pathToFileURL(artifact).href;
const k='https://w3id.org/mpc/ontology/modules/kpi/',dp='https://w3id.org/mpc/ontology/modules/data-product/',sys='https://w3id.org/mpc/ontology/modules/system/';
const crack=k+'measure/crack-spreads',crude=k+'measure/crude-value-to-breakeven';
try {
 const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
 await context.route(/^https?:/,r=>{requests.push(r.request().url());return r.abort();});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base);
 await page.getByRole('navigation',{name:'Primary'}).getByRole('link',{name:'Measures and KPIs',exact:true}).click();
 await page.getByRole('heading',{name:'Choose a measure',exact:true}).waitFor();
 const catalogue=await page.locator('#measure-catalogue a[title]').evaluateAll(as=>as.map(a=>a.title).sort());
 const source=await page.evaluate(k=>data.nodes.filter(n=>n.values.some(v=>v.p==='http://www.w3.org/1999/02/22-rdf-syntax-ns#type' && !v.literal && v.v===k+'MeasureDefinition')).map(n=>n.id).sort(),k);
 assert.deepEqual([...new Set(catalogue)],source,'Every recorded definition is available, including non-KPI entries');
 results.push('complete measure catalogue');
 const choose=async id=>{
  const a=page.locator(`#measure-catalogue a[title="${id}"]`).first();
  await a.evaluate(el=>{for(let p=el.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;});
  await a.focus();await page.keyboard.press('Enter');
  await page.waitForFunction(id=>explorerState.id===id,id);
 };
 const follow=async(s,p,o)=>{
  const card=page.locator(`.connection-card[data-subject="${s}"][data-predicate="${p}"][data-object="${o}"]`);
  assert.equal(await card.count(),1,'Exact asserted edge is visible once');
  await card.evaluate(el=>{for(let p=el.parentElement;p;p=p.parentElement)if(p.tagName==='DETAILS')p.open=true;});
  const next=await page.evaluate(({s,o})=>explorerState.id===s?o:s,{s,o});
  await card.getByRole('link',{name:/^(Follow connection|Return to this item)/}).click();
  await page.waitForFunction(id=>explorerState.id===id,next);
 };
 await choose(crack);
 assert.match(await page.locator('.measure-context').innerText(),/market indicator/i);
 assert.match(await page.locator('.measure-context').innerText(),/KPI-0001/);
 assert.equal(await page.locator('#measure-catalogue .selected-measure a').getAttribute('title'),crack);
 assert.ok(await page.getByRole('navigation',{name:'Connection groups'}).getByRole('button',{name:/^People and responsibilities/}).count());
 const before=page.url();
 await page.getByRole('navigation',{name:'Connection groups'}).getByRole('button',{name:/^Processes \(/}).focus();
 await page.keyboard.press('Enter');
 assert.equal(page.url(),before,'Group jump preserves the saved route');
 assert.match(await page.evaluate(()=>document.activeElement.textContent),/^Processes/);
 const process='https://w3id.org/mpc/ontology/process/CM-1-1-4-7-4';
 const relation=page.locator(`.connection-card[data-predicate="${k}informsProcess"] .relationship-definition`);
 await relation.locator('summary').click();
 assert.equal(await relation.locator('p').innerText(),'A process the measure informs. The link is context for where the measure is used, not a certification that the process owns or computes it.');
 assert.equal(page.url(),before,'Explanation stays in context');
 const kind=k+'measure-kind/market-indicator';
 await page.locator(`.measure-context a[title="${kind}"]`).click();
 await page.waitForFunction(id=>explorerState.id===id,kind);
 assert.deepEqual(await page.evaluate(()=>explorerState.trail.steps),[{s:crack,p:k+'measureKind',o:kind}]);
 assert.equal(await page.evaluate(()=>explorerState.trail.start),crack,'Recorded-kind links retain the starting measure');
 await page.reload();assert.equal(await page.evaluate(()=>explorerState.trail.start),crack);
 await page.goBack();await page.waitForFunction(id=>explorerState.id===id,crack);
 await follow(crack,k+'informsProcess',process);
 assert.equal(await page.evaluate(()=>explorerState.trail.start),crack);
 await page.goBack();await page.waitForFunction(id=>explorerState.id===id,crack);
 const product=dp+'table/view-mpr-mips-crack-spread-price-fact-metrics-vw';
 await follow(product,dp+'servesMeasure',crack);
 await page.reload();
 assert.equal(await page.evaluate(()=>explorerState.trail.start),crack);
 assert.deepEqual(await page.evaluate(()=>explorerState.trail.steps),[{s:product,p:dp+'servesMeasure',o:crack}]);
 assert.match(await page.locator('.reading-trail').innerText(),/←/);
 results.push('recorded classification, exact explanation, keyboard shortcuts, measure to process and data product, saved incoming trail');
 await choose(crude);
 const crudeProcess='https://w3id.org/mpc/ontology/process/CM-1-1-2-6',system=sys+'system/planning-db';
 await follow(crude,k+'informsProcess',crudeProcess);
 await follow(system,sys+'supports',crudeProcess);
 assert.deepEqual(await page.evaluate(()=>explorerState.trail.steps),[{s:crude,p:k+'informsProcess',o:crudeProcess},{s:system,p:sys+'supports',o:crudeProcess}]);
 await page.reload();assert.equal(await page.evaluate(()=>explorerState.trail.start),crude);
 await page.goBack();await page.waitForFunction(id=>explorerState.id===id,crudeProcess);
 await page.goForward();await page.waitForFunction(id=>explorerState.id===id,system);
 results.push('measure to process to system, exact source direction, reload and history');
 for(const width of [1440,720,390]) {
  await page.setViewportSize({width,height:1000});
  for(const theme of ['light','dark']) {
   await page.emulateMedia({colorScheme:theme});
   await page.goto(base+'#measures?at='+encodeURIComponent(crack));
   await page.locator('#selected-title').waitFor();
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`No horizontal page overflow at ${width} in ${theme}`);
   await page.screenshot({path:resolve(evidence,`${engine}-${width}-${theme}.png`),fullPage:true});
  }
 }
 // A half-width CSS viewport exercises the reflow expected at 200% browser zoom.
 // This is not a claim that the browser's native zoom control was exercised.
 results.push('desktop, half-width reflow and phone layouts in both themes');
 await page.goto(base+'#module=kpi');
 await page.getByRole('heading',{name:'Measures and KPIs',exact:true}).waitFor();
 await page.locator('#measure-catalogue').waitFor();
 // Exercise a release without Party before startup, including its absent metadata.
 const original=await readFile(artifact,'utf8'),marker='<script id="ontology-data" type="application/json">';
 const start=original.indexOf(marker)+marker.length,end=original.indexOf('</script>',start);
 const payload=JSON.parse(original.slice(start,end));
 payload.nodes=payload.nodes.filter(n=>!n.modules.some(m=>m.name==='party'));
 payload.moduleInfo=payload.moduleInfo.filter(m=>m.name!=='party');
 payload.referenceModules=payload.referenceModules.filter(m=>m!=='party');
 const fixture=resolve(evidence,'without-party.html');
 await writeFile(fixture,original.slice(0,start)+JSON.stringify(payload).replace(/</g,'\\u003c')+original.slice(end));
 await page.goto(pathToFileURL(fixture).href+'#measures?at='+encodeURIComponent(crack));
 await page.locator('#selected-title').waitFor();
 assert.ok(await page.locator('.connection-card').count()>0,'Measures remain usable without the Party module');
 results.push('recorded-kind trail survives navigation and reload; missing Party module does not break measure connections');
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
 await writeFile(resolve(evidence,'results.json'),JSON.stringify({engine,version:browser.version(),artifact,results,errors,requests,limits:['Half-width reflow is tested; native browser zoom is a separate manual check.','WebKit is engine coverage, not Safari application coverage.']},null,2));
 console.log(JSON.stringify({engine,results,errors,requests}));
} finally {await browser.close();}
