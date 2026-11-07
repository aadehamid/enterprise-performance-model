import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
import {writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const {chromium}=createRequire(import.meta.url)('playwright-core');
const file=resolve(process.argv[2]);
const evidence=process.argv[3];
assert.ok(process.argv[2], 'Pass the generated horoi_viewer/index.html');
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const errors=[], requests=[];
try {
  const context=await browser.newContext({viewport:{width:1440,height:1000}});
  await context.route(/^https?:/,r=>{requests.push(r.request().url());return r.abort();});
  const page=await context.newPage();
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(file).href);
  await page.getByRole('heading',{name:'Understand the concepts. Follow their connections.'}).waitFor();
  if(evidence) await page.screenshot({path:resolve(evidence,'overview-desktop.png'),fullPage:true});
  await page.getByRole('link',{name:'Explore the customer domain'}).click();
  await page.getByRole('heading',{name:'Party · Customer domain',exact:true}).waitFor();
  await page.getByRole('link',{name:'customer account',exact:false}).first().click();
  await page.locator('#term-iri').waitFor();
  assert.match(await page.locator('#term-iri').innerText(),/\/CustomerAccount$/);
  assert.match(await page.locator('.term-definition').innerText(),/account/i);
  await page.getByText('All recorded facts, types and sources',{exact:true}).click();
  assert.ok(await page.locator('#facts td').count()>0);
  await page.getByRole('button',{name:'Copy identifier'}).click();
  await page.waitForFunction(()=>/Copied|selected/.test(document.getElementById('copy-status').textContent));
  assert.match(await page.locator('#copy-status').innerText(),/Copied|selected/);
  await page.locator('#facts summary').click();
  assert.equal(await page.locator('a[href*="rdf-schema"]').count(),0,'Undescribed vocabulary predicates must not link to missing viewer terms');
  if(evidence) await page.screenshot({path:resolve(evidence,'term-desktop.png'),fullPage:true});
  const termURL=page.url();
  await page.reload();
  assert.equal(page.url(),termURL);
  assert.match(await page.locator('#term-iri').innerText(),/\/CustomerAccount$/);
  await page.locator('.skip').focus();
  await page.keyboard.press('Enter');
  assert.equal(page.url(),termURL,'Skip navigation preserves the current term');
  assert.equal(await page.evaluate(()=>document.activeElement.id),'content');
  await page.getByRole('link',{name:'Find a term',exact:true}).click();
  await page.locator('#search').fill('customer account');
  await page.locator('#module-filter').selectOption('party');
  assert.ok(await page.locator('#results li').count()>0);
  await page.locator('#results a').first().click();
  await page.locator('#term-iri').waitFor();
  await page.goBack();
  assert.equal(await page.locator('#search').inputValue(),'customer account');
  assert.equal(await page.locator('#module-filter').inputValue(),'party');
  await page.locator('#search').fill('this term cannot exist 5789');
  assert.equal(await page.locator('#results li').count(),0);
  assert.match(await page.locator('#result-count').innerText(),/No matching/);
  await page.goto(pathToFileURL(file).href+'#connections=party');
  await page.getByRole('heading',{name:'Connections from Party · Customer domain'}).waitFor();
  assert.ok(await page.locator('tbody tr').count()>0);
  assert.ok(await page.locator('h2').allTextContents().then(t=>t.some(x=>x.includes('Core'))));
  const coreLink=page.locator('td a[href^="#term="]').filter({hasText:/./}).first();
  assert.ok(await coreLink.count());
  if(evidence) await page.screenshot({path:resolve(evidence,'connections-desktop.png')});
  // Every term and predicate row is bound to the raw release data, not inferred.
  const coverage=await page.evaluate(()=>({
    terms:data.pilotTerms.length,
    definitions:data.nodes.filter(n=>pilot.has(n.id)&&definitions(n).length).length,
    modules:data.moduleInfo.map(m=>m.name),
    connectionRows:connectionRows('party').length,
    invalidConnections:connectionRows('party').filter(r=>!nodes.get(r.s).values.some(v=>!v.literal&&v.p===r.p&&v.v===r.o)).length
  }));
  assert.equal(coverage.invalidConnections,0);
  assert.equal(new Set(coverage.modules).size,coverage.modules.length);
  const connected=await page.evaluate(()=>data.nodes.find(n=>pilot.has(n.id)&&n.values.filter(v=>!v.literal&&v.p!==RDF+'type'&&nodes.has(v.v)&&!v.v.startsWith('_:')&&!data.supportingKinds.includes(nodes.get(v.v).kind)).length>=3).id);
  await page.goto(pathToFileURL(file).href+'#term='+encodeURIComponent(connected));
  await page.locator('.graph svg').waitFor();
  if(evidence) await page.screenshot({path:resolve(evidence,'connected-term-desktop.png'),fullPage:true});
  const unknownTargets=await page.locator('a[href^="../viewer/index.html#"]').evaluateAll(links=>links.filter(a=>!nodes.has(decodeURIComponent(a.getAttribute('href').split('#')[1]))).map(a=>a.href));
  assert.deepEqual(unknownTargets,[],'Every linked full-viewer term exists');
  await page.goto(pathToFileURL(file).href+'#term=%ZZ');
  await page.getByRole('heading',{name:'Choose a starting point'}).waitFor();
  // Local links must stay in the release and point to existing files.
  for(const hash of ['#overview','#modules','#guide','#module=party','#module=core','#about']) {
    await page.goto(pathToFileURL(file).href+hash);
    await page.locator('h1').waitFor();
    const hrefs=await page.locator('a[href]').evaluateAll(as=>as.map(a=>a.getAttribute('href')));
    const {stat}=await import('node:fs/promises');
    for(const href of hrefs.filter(h=>!h.startsWith('#')&&!/^https?:/.test(h))) {
      const path=new URL(href,page.url());
      await stat(decodeURIComponent(path.pathname));
    }
  }
  // Following a cross-module destination reaches the expected full-viewer view.
  await page.goto(pathToFileURL(file).href+'#modules');
  const externalModule=page.locator('a.tile[href*="view=module:"]').first();
  const expected=(await externalModule.getAttribute('href')).split('view=')[1];
  await externalModule.click();
  await page.locator('#overview').waitFor();
  assert.equal(await page.locator('#overview').getAttribute('data-view'),decodeURIComponent(expected));
  for(const width of [768,390]) {
    await page.setViewportSize({width,height:844});
    await page.goto(pathToFileURL(file).href);
    await page.locator('h1').waitFor();
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    await page.getByRole('link',{name:'Find a term',exact:true}).click();
    await page.locator('#search').fill('customer account');
    await page.locator('#results a').first().click();
    await page.locator('#term-iri').waitFor();
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    if(width===390) assert.ok(await page.locator('.relationship-table').evaluateAll(tables=>tables.every(t=>t.scrollWidth<=t.clientWidth+1)),'Connections fit the phone width');
    const oldTheme=await page.locator('html').getAttribute('data-theme');
    await page.getByRole('button',{name:'Switch colour theme'}).click();
    assert.equal(await page.locator('html').getAttribute('data-theme'),oldTheme==='dark'?'light':'dark');
    if(evidence) await page.screenshot({path:resolve(evidence,`term-${width}.png`),fullPage:true});
  }
  assert.deepEqual(errors,[],'No JavaScript errors');
  assert.deepEqual(requests,[],'No network requests, even when navigating');
  const result={passed:true,coverage,requests,errors,viewports:[1440,768,390]};
  if(evidence) await writeFile(resolve(evidence,'browser-results.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify(result,null,2));
} finally {await browser.close();}
