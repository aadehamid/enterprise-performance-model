import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
import {writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const {chromium}=createRequire(import.meta.url)('playwright-core');
assert.ok(process.argv[2], 'Pass the generated index.html and an existing evidence directory');
const base=pathToFileURL(resolve(process.argv[2])).href, evidence=process.argv[3];
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const errors=[],requests=[],screens=[];
try {
  const context=await browser.newContext({viewport:{width:1440,height:1000}});
  await context.route(/^https?:/,r=>{requests.push(r.request().url());return r.abort();});
  const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
  const go=async(mode,id)=>{
    await page.goto(base+'#'+mode+(id?'?at='+encodeURIComponent(id):''));
    await page.locator('.explorer-layout').waitFor();
    await page.waitForFunction(({mode,id})=>explorerState.mode===mode && explorerState.id===(id||streamModes[mode]||(mode==='process'?explorer.roots[0]:'')),{mode,id});
  };
  const snap=async name=>{if(evidence){await page.screenshot({path:resolve(evidence,name+'.png'),fullPage:true});screens.push(name+'.png');}};
  const actualRows=async()=>page.locator('.connection-card').evaluateAll(cs=>cs.map(c=>({s:c.dataset.subject,p:c.dataset.predicate,o:c.dataset.object})));
  const assertConnections=async()=>{
    const expected=await page.evaluate(()=>{
      const id=explorerState.id, rows=[];
      for (const n of data.nodes) for (const v of n.values) if (!v.literal && (n.id===id || v.v===id)) rows.push({s:n.id,p:v.p,o:v.v});
      return [...new Set(rows.map(r=>JSON.stringify(r)))].sort();
    });
    const rendered=(await actualRows()).map(r=>JSON.stringify(r)).sort();
    assert.deepEqual(rendered,expected,'Every incoming and outgoing assertion appears once, with its original direction');
  };
  await go('process');
  await assertConnections();
  await snap('process-root-desktop');
  const index=await page.evaluate(()=>({
    roots:explorer.roots,levels:[...new Set([...explorer.processes].map(id=>explorer.level(id)))],
    leaf:[...explorer.processes].find(id=>explorer.level(id)==='6'),stages:explorer.stages,
    path:explorer.ancestry([...explorer.processes].find(id=>explorer.level(id)==='6'))
  }));
  assert.ok(index.leaf,'The pinned source supplies a real L6 path');
  // Walk down the hierarchy through the visible child links, one level at a time.
  await go('process',index.path[0]);
  for(const id of index.path.slice(1)) {
    await page.locator('.position-grid a').evaluateAll((links,id)=>links.find(a=>a.title===id).click(),id);
    await page.waitForFunction(id=>explorerState.id===id,id);
  }
  assert.equal(await page.locator('.ancestry li').count(),index.path.length);
  await assertConnections();await snap('process-deep-desktop');
  await page.reload();assert.equal(await page.evaluate(()=>explorerState.id),index.leaf);
  await page.locator('#process-search').fill('Establish Credit Limit');
  assert.ok(await page.locator('#process-search-results a').count()>0);
  await page.locator('#process-search-results a').first().focus();await page.keyboard.press('Enter');
  await page.waitForFunction(()=>document.getElementById('selected-title').textContent.includes('Establish Credit Limit'));
  await assertConnections();
  await page.goBack();
  assert.equal(await page.locator('#process-search').inputValue(),'Establish Credit Limit','Search is restored on Back');
  // Keyboard expansion loads children only when needed.
  await go('process');
  const collapsed=page.locator('.process-branch:not([open]) > summary').first();
  await collapsed.focus();await page.keyboard.press('Enter');
  await page.waitForFunction(()=>[...document.querySelectorAll('.process-branch[open] > ul')].every(x=>x.dataset.loaded));
  const party='https://w3id.org/mpc/ontology/modules/party/', core='https://w3id.org/mpc/ontology/process/';
  const stage=party+'lifecycle-stage/onboarding', process=core+'CM-1-3-7-4-2';
  await go('customer');
  assert.equal(await page.locator('.stage-list li').count(),index.stages.length);
  assert.match(await page.locator('.explorer-sidebar').innerText(),/without a sequence/);
  await page.locator('.stage-list a').evaluateAll((links,id)=>links.find(a=>a.title===id).click(),stage);
  await page.waitForFunction(id=>explorerState.id===id,stage);
  await assertConnections();await snap('customer-onboarding-desktop');
  const toProcess=page.locator(`.connection-card[data-predicate="${party}stageProcess"][data-object="${process}"]`);
  await toProcess.getByRole('link',{name:'Follow connection',exact:false}).click();
  await page.waitForFunction(id=>explorerState.id===id,process);
  await assertConnections();
  const system=await page.locator('.connection-card').evaluateAll(cards=>cards.find(c=>c.dataset.predicate==='https://w3id.org/mpc/ontology/modules/system/supports').dataset.subject);
  await page.locator(`.connection-card[data-subject="${system}"][data-predicate$="/supports"]`).getByRole('link',{name:'Follow connection',exact:false}).click();
  await page.waitForFunction(id=>explorerState.id===id,system);
  assert.equal(await page.locator('.reading-trail li').count(),3);
  assert.match(await page.locator('.reading-trail').innerText(),/← supports ←/);
  await assertConnections();await snap('customer-process-system-trail');
  const trailURL=page.url();await page.reload();assert.equal(page.url(),trailURL);assert.equal(await page.locator('.reading-trail li').count(),3);
  await page.goBack();await page.waitForFunction(id=>explorerState.id===id,process);
  await page.goForward();await page.waitForFunction(id=>explorerState.id===id,system);
  await page.locator('.reading-trail a').first().click();await page.waitForFunction(id=>explorerState.id===id,stage);
  assert.equal(await page.locator('.reading-trail').count(),0);
  // A second real path follows a system stage to a specific system.
  const master=party+'system-stage/master';
  await page.locator(`.connection-card[data-predicate="${party}correspondsTo"][data-object="${master}"]`).getByRole('link',{name:'Follow connection',exact:false}).click();
  await page.waitForFunction(id=>explorerState.id===id,master);await assertConnections();
  await page.locator(`.connection-card[data-predicate="${party}stageSystem"]`).first().getByRole('link',{name:'Follow connection',exact:false}).click();
  await page.waitForFunction(()=>document.getElementById('selected-title').textContent.includes('SAP MDG'));
  await assertConnections();
  // Malformed, invented and disconnected trails do not become diagrammed assertions.
  await page.goto(base+'#customer?'+new URLSearchParams({at:stage,trail:JSON.stringify({start:stage,steps:[{s:stage,p:'urn:invented',o:stage}]})}));
  await page.getByText('This saved trail contains an unavailable or unconnected statement.',{exact:false}).waitFor();
  assert.equal(await page.locator('.reading-trail').count(),0);
  await page.goto(base+'#process?at=urn:missing');await page.getByRole('heading',{name:'Choose a starting point'}).waitFor();
  const vs='https://w3id.org/mpc/ontology/modules/value-stream/';
  const streamProcesses={commercial:vs+'process/market-intelligence-planning','order-to-cash':vs+'process/otc-establish-credit-limit-risk-code'};
  const follow=async(s,p,o)=>{
    const selected=await page.evaluate(()=>explorerState.id), next=selected===s?o:s;
    const card=page.locator(`.connection-card[data-subject="${s}"][data-predicate="${p}"][data-object="${o}"]`);
    // Supporting statements may be behind a collapsed group or remainder list.
    await card.evaluate(x=>{for(let p=x.parentElement;p;p=p.parentElement) if(p.tagName==='DETAILS') p.open=true;});
    await card.locator('.connection-meta a').click();
    await page.waitForFunction(id=>explorerState.id===id,next);
    await assertConnections();
  };
  for(const mode of ['commercial','order-to-cash']) {
    await go(mode);await assertConnections();await snap(mode+'-overview-desktop');
    const stageIds=await page.evaluate(()=>{
      const vs=explorer.streamNamespace, n=nodes.get(explorerState.id);
      return n.values.filter(v=>!v.literal&&v.p===vs+'hasStage').map(v=>v.v).sort((a,b)=>Number(nodes.get(a).values.find(v=>v.p===vs+'sequence').v)-Number(nodes.get(b).values.find(v=>v.p===vs+'sequence').v));
    });
    assert.deepEqual(await page.locator('.stream-map h3 a').evaluateAll(xs=>xs.map(x=>x.title)),stageIds,'All stages appear in the exact recorded numeric order');
    for(const stageId of stageIds) {
      await page.locator('.stream-stage-heading').getByTitle(stageId,{exact:true}).click();
      await page.waitForFunction(id=>explorerState.id===id,stageId);
      const expected=await page.evaluate(()=>nodes.get(explorerState.id).values.filter(v=>!v.literal&&v.p===explorer.streamNamespace+'hasProcess').map(v=>v.v).sort());
      assert.deepEqual((await page.locator('.stage-processes a').evaluateAll(xs=>xs.map(x=>x.title))).sort(),expected,'Every member process is reachable from its stage');
      await assertConnections();
    }
    const processId=streamProcesses[mode];
    const containing=await page.evaluate(id=>data.nodes.find(n=>n.values.some(v=>!v.literal&&v.p===explorer.streamNamespace+'hasProcess'&&v.v===id)).id,processId);
    await page.locator('.stream-stage-heading').getByTitle(containing,{exact:true}).focus();
    await page.keyboard.press('Enter');
    await page.waitForFunction(id=>explorerState.id===id,containing);
    await page.locator('.stage-processes').getByTitle(processId,{exact:true}).click();
    await page.waitForFunction(id=>explorerState.id===id,processId);
    assert.equal(await page.locator('.reading-trail li').count(),3);
    assert.match(await page.locator('.explorer-selection > .eyebrow').innerText(),/Value-stream process/i);
    const target=await page.evaluate(()=>nodes.get(explorerState.id).values.find(v=>v.p===explorer.streamNamespace+'realizes').v);
    await follow(processId,vs+'realizes',target);
    await page.waitForFunction(id=>explorerState.id===id,target);
    assert.ok(await page.locator('.process-position').isVisible(),'A realized process leads into its process hierarchy');
    assert.equal(await page.locator('.reading-trail li').count(),4);
    assert.match(await page.locator('.reading-trail').innerText(),/Value-stream process/);
    assert.match(await page.locator('.reading-trail').innerText(),/Process-map concept/,'Same-label concepts remain distinguishable in the trail');
    assert.match(await page.locator('h1').innerText(),mode==='commercial'?/Commercial Hydrocarbon Lifecycle/:/Order to Cash/);
    const url=page.url();await page.reload();assert.equal(page.url(),url);
    await snap(mode+'-process-trail');
    await page.goBack();await page.waitForFunction(id=>explorerState.id===id,processId);
    if(mode==='commercial') {
      const dataProduct=await page.evaluate(()=>nodes.get(explorerState.id).values.find(v=>v.p===explorer.streamNamespace+'consumes').v);
      await follow(processId,vs+'consumes',dataProduct);await page.waitForFunction(id=>explorerState.id===id,dataProduct);
      assert.ok(await page.locator('.reading-trail').innerText().then(t=>t.includes('consumes')));
    }
  }
  // The feedback and measure paths keep their predicates and do not become stage order.
  const loop=await page.evaluate(()=>{
    const n=data.nodes.find(n=>n.values.some(v=>!v.literal&&v.p===explorer.streamNamespace+'loopsTo'));
    const v=n.values.find(v=>v.p===explorer.streamNamespace+'loopsTo');return {s:n.id,p:v.p,o:v.v};
  });
  await go('commercial',loop.s);await follow(loop.s,loop.p,loop.o);
  assert.match(await page.locator('.reading-trail').innerText(),/loops to/);
  const performance=vs+'process/performance-tracking-analysis';
  await go('commercial',performance);
  const measureLink=await page.evaluate(()=>nodes.get(explorerState.id).values.find(v=>v.p===explorer.streamNamespace+'measureLink').v);
  await follow(performance,vs+'measureLink',measureLink);await page.waitForFunction(id=>explorerState.id===id,measureLink);
  const measure=await page.evaluate(()=>nodes.get(explorerState.id).values.find(v=>v.p===explorer.streamNamespace+'measure').v);
  await follow(measureLink,vs+'measure',measure);await page.waitForFunction(id=>explorerState.id===id,measure);
  assert.match(await page.locator('.reading-trail').innerText(),/measure link/);
  // Real controls and both relationship endpoints remain available at each width.
  for(const width of [1440,768,390]) {
    await page.setViewportSize({width,height:1000});
    for(const mode of ['process','customer','commercial','order-to-cash']) {
      await go(mode,streamProcesses[mode]||(mode==='process'?process:stage));
      assert.ok(await page.locator('.explorer-sidebar').isVisible(),`Navigation visible at ${width}`);
      if(width<=900) await page.waitForFunction(()=>{
        const top=document.getElementById('selected-title').getBoundingClientRect().top;
        return top>=-1 && top<120;
      },null,{timeout:5000}); // Wait for the page's smooth scroll to finish.
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`No page overflow at ${width}`);
      const card=page.locator('.connection-card').first();await card.scrollIntoViewIfNeeded();
      const boxes=await card.locator('.statement > div').evaluateAll(xs=>xs.map(x=>x.getBoundingClientRect().toJSON()));
      assert.ok(boxes.every(r=>r.left>=0 && r.right<=width),'All statement endpoints fit the screen');
      for(const theme of ['light','dark']) {
        await page.emulateMedia({colorScheme:theme});await page.reload();
        await snap(`${mode}-${width}-${theme}`);
      }
    }
  }
  assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
  const result={status:'passed',levels:index.levels,deepPath:index.path,errors,requests,screens};
  if(evidence) await writeFile(resolve(evidence,'explorer-results.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify(result));
} finally {await browser.close();}
