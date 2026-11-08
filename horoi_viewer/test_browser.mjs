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
  const themeCases=[];
  for(const systemTheme of ['light','dark']) {
    await page.emulateMedia({colorScheme:systemTheme});
    await page.goto(pathToFileURL(file).href);
    for(let clicks=0;clicks<3;clicks++) {
      if(clicks) await page.getByRole('button',{name:'Switch colour theme'}).click();
      const colors=await page.evaluate(()=>{
        const root=getComputedStyle(document.documentElement);
        const primary=getComputedStyle(document.querySelector('.actions a.primary'));
        return {accent:root.getPropertyValue('--accent').trim(),background:primary.backgroundColor,text:primary.color};
      });
      themeCases.push({systemTheme,clicks,...colors});
      if(evidence && clicks===0) await page.screenshot({path:resolve(evidence,`system-${systemTheme}.png`),fullPage:true});
    }
  }
  if(evidence) await writeFile(resolve(evidence,'theme-results.json'),JSON.stringify(themeCases,null,2));
  const luminance=color=>color.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
  for(const state of themeCases) {
    const expected=state.clicks===1?(state.systemTheme==='dark'?'light':'dark'):state.systemTheme;
    assert.equal(state.accent,expected==='dark'?'#8bd6c9':'#17665d',`Custom palette under ${state.systemTheme} system theme after ${state.clicks} clicks`);
    const values=[luminance(state.background),luminance(state.text)].sort((a,b)=>a-b);
    assert.ok((values[1]+.05)/(values[0]+.05)>=4.5,'Primary link text meets 4.5:1 contrast in each effective theme');
  }
  await page.emulateMedia({colorScheme:'light'});
  await page.goto(pathToFileURL(file).href);
  await page.emulateMedia({colorScheme:'dark'});
  await page.waitForFunction(()=>document.documentElement.dataset.theme==='dark');
  assert.equal(await page.evaluate(()=>getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()),'#8bd6c9');
  await page.getByRole('button',{name:'Switch colour theme'}).click();
  await page.emulateMedia({colorScheme:'light'});
  await page.emulateMedia({colorScheme:'dark'});
  assert.equal(await page.locator('html').getAttribute('data-theme'),'light','An explicit reader choice survives later system preference changes');
  await page.emulateMedia({colorScheme:'light'});
  await page.goto(pathToFileURL(file).href);
  if(evidence) await page.screenshot({path:resolve(evidence,'overview-desktop.png'),fullPage:true});
  await page.getByRole('link',{name:'Explore the customer domain'}).click();
  await page.getByRole('heading',{name:'Party · Customer domain',exact:true}).waitFor();
  await page.getByRole('link',{name:'customer account',exact:false}).first().click();
  await page.locator('#term-iri').waitFor();
  assert.match(await page.locator('#term-iri').innerText(),/\/CustomerAccount$/);
  assert.match(await page.locator('.term-definition').innerText(),/account/i);
  await page.getByText('All recorded facts, types and sources',{exact:true}).click();
  const factRows=await page.locator('#facts tbody tr').evaluateAll(rows=>rows.map(row=>{
    const [property,value]=row.cells;
    return {p:property.querySelector('code').textContent,value:value.textContent.replace(/\s+/g,' ').trim(),target:value.querySelector('[title]')?.title||null};
  }));
  const rawFacts=await page.evaluate(()=>nodes.get(document.getElementById('term-iri').textContent).values);
  assert.equal(factRows.length,rawFacts.length);
  for(let i=0;i<rawFacts.length;i++) {
    const value=rawFacts[i];assert.equal(factRows[i].p,value.p);
    if(value.literal) assert.equal(factRows[i].value,[value.v,value.lang?'Language: '+value.lang:'',value.datatype?'Datatype: '+value.datatype:''].filter(Boolean).join(' ').replace(/\s+/g,' ').trim());
    else assert.equal(factRows[i].target,value.v);
  }
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
  // Paging survives term navigation and reload, including keyboard focus.
  await page.goto(pathToFileURL(file).href+'#browse');
  await page.locator('#next').focus();
  await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>document.activeElement.id),'next');
  const secondPage=await page.locator('#result-count').innerText();
  const secondResult=await page.locator('#results a').first().getAttribute('href');
  await page.locator('#results a').first().click();
  await page.locator('#term-iri').waitFor();
  await page.goBack();
  assert.equal(await page.locator('#result-count').innerText(),secondPage);
  assert.equal(await page.locator('#results a').first().getAttribute('href'),secondResult);
  await page.reload();
  assert.equal(await page.locator('#result-count').innerText(),secondPage);
  await page.locator('#prev').focus();
  await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>document.activeElement.id),'next','Move focus to an enabled control at the first page');
  for(const value of ['-1','NaN','999999']) {
    await page.goto(pathToFileURL(file).href+'#browse?page='+value);
    assert.ok(await page.locator('#results li').count()>0,'Invalid or excessive page values stay usable');
  }
  await page.locator('#prev').focus();
  await page.keyboard.press('Enter');
  await page.locator('#next').focus();
  await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>document.activeElement.id),'prev','Move focus to an enabled control at the last page');
  // A delayed clipboard result belongs only to the page that started it.
  const copyTerms=await page.evaluate(()=>data.pilotTerms.slice(0,2));
  for(const outcome of ['resolve','reject']) {
    for(const destination of ['#term='+encodeURIComponent(copyTerms[1]),'#overview']) {
      await page.goto(pathToFileURL(file).href+'#term='+encodeURIComponent(copyTerms[0]));
      await page.locator('#term-iri').waitFor();
      await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:()=>new Promise((resolve,reject)=>{window.settleCopy={resolve,reject};})}}));
      await page.locator('#copy-iri').click();
      await page.goto(pathToFileURL(file).href+destination);
      await page.locator('h1').waitFor();
      await page.evaluate(outcome=>window.settleCopy[outcome](),outcome);
      if(destination.startsWith('#term')) assert.equal(await page.locator('#copy-status').innerText(),'');
      assert.equal(await page.evaluate(()=>String(getSelection())),'');
    }
  }
  await page.goto(termURL);
  await page.locator('#term-iri').waitFor();
  await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:()=>Promise.reject(new Error('Clipboard unavailable'))}}));
  await page.locator('#copy-iri').click();
  assert.match(await page.locator('#copy-status').innerText(),/Identifier selected/);
  assert.equal(await page.evaluate(()=>String(getSelection())),await page.locator('#term-iri').innerText());
  // Group filters must show the complete expected population from raw kinds.
  for(const group of ['Business concepts','Vocabulary','Rules and evidence']) {
    await page.goto(pathToFileURL(file).href+'#browse');
    await page.locator('#layer-filter').selectOption(group);
    const expected=await page.evaluate(group=>data.nodes.filter(n=>{
      const local=n.modules.some(m=>data.pilotModules.includes(m.name));
      const vocabulary=['Class','Property'].includes(n.kind);
      const supporting=[...data.supportingKinds,'Metadata'].includes(n.kind);
      return local&&(group==='Vocabulary'?vocabulary:group==='Rules and evidence'?supporting:!vocabulary&&!supporting);
    }).map(n=>n.id).sort(),group);
    const shown=[];
    while(true) {
      shown.push(...await page.locator('#results a').evaluateAll(links=>links.map(a=>a.title)));
      if(await page.locator('#next').isDisabled()) break;
      await page.locator('#next').click();
    }
    assert.deepEqual(shown.sort(),expected,group+' covers each matching term once');
  }
  // Compare every displayed cross-module tuple with the source statements.
  for(const module of ['party','core']) {
    await page.goto(pathToFileURL(file).href+'#connections='+module);
    const expected=await page.evaluate(module=>{
      const terms=new Map(data.nodes.map(n=>[n.id,n]));const rows=[];
      for(const source of data.nodes.filter(n=>data.pilotTerms.includes(n.id)&&n.modules.some(m=>m.name===module))) {
        for(const statement of source.values.filter(v=>!v.literal)) {
          const target=terms.get(statement.v);
          if(!target||[...data.supportingKinds,'Metadata'].includes(target.kind)) continue;
          for(const other of target.modules) if(other.name!=='Release metadata'&&other.name!==module&&!source.modules.some(m=>m.name===other.name)) rows.push([source.id,statement.p,statement.v]);
        }
      }
      return rows.map(row=>JSON.stringify(row)).sort();
    },module);
    const actual=await page.locator('.relationship-table tbody tr').evaluateAll(rows=>rows.map(row=>JSON.stringify([...row.cells].map(cell=>cell.querySelector('[title]').title))).sort());
    assert.deepEqual(actual,expected,module+' shows every recorded cross-module tuple');
  }
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
  await page.locator('.graph svg:visible').waitFor();
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
  // Direct term routes into the existing viewer must select the exact term.
  await page.goto(termURL);
  const expectedTerm=await page.locator('#term-iri').innerText();
  await page.getByRole('link',{name:'Open this term in the full viewer'}).click();
  await page.waitForFunction(id=>document.getElementById('iri')?.textContent===id,expectedTerm);
  await page.goto(pathToFileURL(file).href+'#connections=party');
  const externalTerm=page.locator('td a[href^="../viewer/index.html#"]').first();
  const externalId=decodeURIComponent((await externalTerm.getAttribute('href')).split('#')[1]);
  await externalTerm.click();
  await page.waitForFunction(id=>document.getElementById('iri')?.textContent===id,externalId);
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
    await page.goto(pathToFileURL(file).href+'#connections=party');
    assert.ok(await page.locator('.relationship-table tbody tr').count()>0);
    assert.ok(await page.locator('.relationship-table').evaluateAll(tables=>tables.every(t=>t.scrollWidth<=t.clientWidth+1)));
    if(evidence) await page.screenshot({path:resolve(evidence,`connections-${width}.png`),fullPage:true});
    await page.goto(pathToFileURL(file).href+'#term='+encodeURIComponent(connected));
    await page.locator('.graph svg:visible').waitFor();
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
    assert.ok(await page.locator('.relationship-table tbody tr').count()>0);
    if(evidence) await page.screenshot({path:resolve(evidence,`graph-${width}.png`),fullPage:true});

  }
  assert.deepEqual(errors,[],'No JavaScript errors');
  assert.deepEqual(requests,[],'No network requests, even when navigating');
  const result={passed:true,coverage,themeCases,requests,errors,viewports:[1440,768,390]};
  if(evidence) await writeFile(resolve(evidence,'browser-results.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify(result,null,2));
} finally {await browser.close();}
