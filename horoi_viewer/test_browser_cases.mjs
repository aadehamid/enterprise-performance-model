import {readFile,writeFile,mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';

export async function browserCounterexamples(browser,file) {
  const original=await readFile(file,'utf8'), marker='<script id="ontology-data" type="application/json">';
  const start=original.indexOf(marker)+marker.length,end=original.indexOf('</script>',start);
  const payload=JSON.parse(original.slice(start,end));
  const folder=await mkdtemp(join(tmpdir(),'horoi-browser-cases-'));
  const context=await browser.newContext(), errors=[],requests=[],passed=[];
  try {
    await context.route(/^https?:/,r=>{requests.push(r.request().url());return r.abort();});
    const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
    const fixture=async(name,mutate)=>{
      const d=structuredClone(payload);mutate(d);const path=join(folder,name+'.html');
      await writeFile(path,original.slice(0,start)+JSON.stringify(d).replace(/</g,'\\u003c')+original.slice(end));
      return pathToFileURL(path).href;
    };
    const ns=payload.moduleInfo.find(m=>m.name==='value-stream').id+'/';
    const streams={commercial:ns+'stream/commercial-hydrocarbon-lifecycle','order-to-cash':ns+'stream/order-to-cash'};
    const hostile='<img src="data:," onerror="window.__rdfXss=1">';
    const labels=await fixture('labels',d=>{for(const id of Object.values(streams))d.nodes.find(n=>n.id===id).label=hostile;});
    for(const mode of Object.keys(streams)) {
      await page.goto(labels+'#'+mode);
      assert.equal(await page.locator('h1').textContent(),hostile,'A stream label must remain literal text');
      assert.ok((await page.locator('.crumb').textContent()).endsWith(hostile));
      assert.equal(await page.locator('.crumb img,h1 img').count(),0);
      assert.equal(await page.evaluate(()=>window.__rdfXss),undefined);
    }
    passed.push('Both stream labels render as text');
    const integer='http://www.w3.org/2001/XMLSchema#integer';
    const ordered=[['z-first',' 1 '],['m-second','\t+2\n'],['a-invalid','1 2']];
    const stageId=name=>'urn:stage-fixture:'+name;
    const ordering=await fixture('integer-stages',d=>{
      const source=d.nodes.find(n=>n.id===streams.commercial);
      source.values=source.values.filter(v=>v.p!==ns+'hasStage');
      source.values.push(...ordered.map(([name])=>({p:ns+'hasStage',v:stageId(name),literal:false})));
      d.nodes.push(...ordered.map(([name,value])=>({id:stageId(name),label:name,kind:'Concept',modules:source.modules,values:[{p:ns+'sequence',v:value,literal:true,datatype:integer}]})));
    });
    await page.goto(ordering+'#commercial');
    assert.deepEqual(await page.locator('.stream-map h3 a').evaluateAll(as=>as.map(a=>a.title)),ordered.map(([name])=>stageId(name)));
    assert.deepEqual(await page.locator('.stream-map .stage-number').allTextContents(),['1','2','?']);
    assert.deepEqual(await page.locator('.stream-stage-heading .level').allTextContents(),['1','2','?']);
    assert.match(await page.locator('.stream-overview').innerText(),/positions are missing, invalid or shared/);
    for(const [name,value] of ordered) {
      await page.goto(ordering+'#commercial?'+new URLSearchParams({at:stageId(name)}));
      await page.getByText('All recorded facts, types and sources',{exact:true}).click();
      const cell=page.locator('.explorer-selection > details tbody td').nth(1);
      assert.equal(await cell.evaluate(el=>el.firstChild.textContent),value+' ','Recorded literal text retains its lexical form');
      assert.equal(await cell.locator('code').innerText(),'Datatype: '+integer);
    }
    passed.push('Typed integer stages render in numeric order and preserve recorded literals');
    for(const removed of [...Object.values(streams).map(id=>[id]),Object.values(streams)]) {
      const url=await fixture('missing-'+removed.length+'-'+removed[0].split('/').pop(),d=>{d.nodes=d.nodes.filter(n=>!removed.includes(n.id));});
      for(const route of ['overview','streams']) {
        await page.goto(url+'#'+route);
        assert.deepEqual(errors,[],'A missing stream must not break the reference');
        assert.equal(await page.locator('h1').count(),1);
        for(const [mode,id] of Object.entries(streams))if(removed.includes(id))assert.equal(await page.locator(`a.tile[href="#${mode}"]`).count(),0,'An unavailable stream is not offered as a working entry');
      }
      for(const [mode,id] of Object.entries(streams))if(removed.includes(id)) {
        await page.goto(url+'#'+mode);
        assert.equal(await page.locator('h1').innerText(),'Choose a starting point');
      }
    }
    const absentModule=await fixture('missing-module',d=>{
      d.nodes=d.nodes.filter(n=>!n.modules.some(m=>m.name==='value-stream'));
      d.moduleInfo=d.moduleInfo.filter(m=>m.name!=='value-stream');
      d.referenceModules=d.referenceModules.filter(m=>m!=='value-stream');
    });
    await page.goto(absentModule+'#overview');assert.deepEqual(errors,[]);assert.equal(await page.locator('h1').count(),1);
    passed.push('Missing streams and module leave the reference usable');
    const base=pathToFileURL(file).href;
    await page.goto(base+'#browse');const expected=await page.locator('#result-count').innerText();
    for(const hash of ['#browse?module=unknown','#browse?layer=unknown','#browse?module=%ZZ&layer=%3Cbad%3E']) {
      await page.goto(base+hash);
      assert.equal(await page.locator('#result-count').innerText(),expected);
      assert.equal(await page.locator('#module-filter').inputValue(),'');
      assert.equal(await page.locator('#layer-filter').inputValue(),'');
    }
    for(const hash of ['#unknown','#unknown?at=anything','#unknown=value']) {
      await page.goto(base+hash);assert.equal(await page.locator('h1').innerText(),'Choose a starting point');
    }
    passed.push('Invalid filters and unknown routes have consistent results');
    const origin=streams['order-to-cash'], stream=payload.nodes.find(n=>n.id===origin);
    const stage=stream.values.find(v=>!v.literal&&v.p===ns+'hasStage').v;
    const saved={start:origin,steps:[{s:origin,p:ns+'hasStage',o:stage}]};
    await page.goto(base+'#commercial?'+new URLSearchParams({at:stage,trail:JSON.stringify(saved)}));
    await page.waitForFunction(()=>explorerState.mode==='order-to-cash');
    assert.equal(await page.locator('h1').innerText(),stream.label);
    assert.ok(new URL(page.url()).hash.startsWith('#order-to-cash?'));
    assert.equal(await page.locator('.reading-trail li').count(),2);
    await page.reload();assert.equal(await page.locator('h1').innerText(),stream.label);
    assert.equal(await page.locator('.reading-trail li').count(),2);
    passed.push('A saved trail restores its originating value-stream view');
    const core=payload.moduleInfo.find(m=>m.name==='core'), broader='http://www.w3.org/2004/02/skos/core#broader';
    const prefix='urn:viewer-fixture:', id=name=>prefix+name;
    const edge=(p,v)=>({p,v,literal:false});
    const hierarchy=await fixture('hierarchy',d=>{
      const process=(name,depth,parents=[])=>({id:id(name),label:name,kind:'Concept',modules:[core],values:[{p:core.id+'/taxonomyLevel',v:String(depth),literal:true},...parents.map(p=>edge(broader,id(p)))]});
      d.nodes.push(process('parent-a',0),process('parent-b',0),process('shared',1,['parent-a','parent-b']),process('cycle-a',1,['cycle-b']),process('cycle-b',2,['cycle-a']));
      for(let i=0;i<=101;i++)d.nodes.push({id:id('trail-'+i),label:'Trail '+i,kind:'Concept',modules:[core],values:i<101?[edge(id('next'),id('trail-'+(i+1)))]:[]});
    });
    await page.goto(hierarchy+'#process?'+new URLSearchParams({at:id('shared')}));
    assert.match(await page.locator('.process-position').innerText(),/multiple parents/);
    assert.deepEqual(await page.locator('.position-grid > div').first().locator('a').evaluateAll(as=>as.map(a=>a.title).sort()),[id('parent-a'),id('parent-b')]);
    await page.goto(hierarchy+'#process?'+new URLSearchParams({at:id('cycle-a')}));
    await page.getByText('Processes without a route from a root',{exact:true}).click();
    const first=page.locator('.process-branch').filter({has:page.locator(':scope > ul[data-children="'+id('cycle-a')+'"]')}).first();
    await first.locator(':scope > summary').click();
    const next=first.locator(':scope > ul > li > .process-branch');
    await next.locator(':scope > summary').click();
    await next.locator(':scope > ul').getByText('Already on this branch; follow its reference.',{exact:true}).waitFor();
    passed.push('Multiple parents remain visible and cycles stop expanding');
    const steps=Array.from({length:101},(_,i)=>({s:id('trail-'+i),p:id('next'),o:id('trail-'+(i+1))}));
    const trail={start:id('trail-0'),steps:steps.slice(0,100)};
    const hundred=hierarchy+'#process?'+new URLSearchParams({at:id('trail-100'),trail:JSON.stringify(trail)});
    await page.goto(hundred);assert.equal(await page.locator('.reading-trail li').count(),101);
    const card=page.locator('.connection-card[data-object="'+id('trail-101')+'"]');
    const group=page.locator('.connection-group').filter({has:card});
    if(!await group.evaluate(el=>el.open))await group.locator(':scope > summary').click();
    await card.getByRole('link',{name:'Start a new trail here',exact:false}).click();
    await page.waitForFunction(selected=>explorerState.id===selected,id('trail-101'));
    assert.equal(await page.locator('.reading-trail').count(),0);
    await page.goBack();await page.waitForFunction(()=>explorerState.trail.steps.length===100);
    assert.equal(await page.locator('.reading-trail li').count(),101);
    await page.goto(hierarchy+'#process?'+new URLSearchParams({at:id('trail-101'),trail:JSON.stringify({start:trail.start,steps})}));
    assert.match(await page.locator('.explorer-selection').innerText(),/saved trail contains an unavailable or unconnected statement/);
    assert.equal(await page.locator('.reading-trail').count(),0);
    passed.push('The 100-hop limit restarts explicitly and rejects longer saved trails');
    await page.goto(hundred.replace('#process?','#order-to-cash?'));
    const streamGroup=page.locator('.connection-group').filter({has:page.locator('.connection-card[data-object="'+id('trail-101')+'"]')});
    if(!await streamGroup.evaluate(el=>el.open))await streamGroup.locator(':scope > summary').click();
    await streamGroup.getByRole('link',{name:'Start a new trail here',exact:false}).click();
    await page.waitForFunction(selected=>explorerState.id===selected,id('trail-101'));
    const incoming=page.locator('.connection-card[data-subject="'+id('trail-100')+'"][data-object="'+id('trail-101')+'"]');
    const incomingGroup=page.locator('.connection-group').filter({has:incoming});
    if(!await incomingGroup.evaluate(el=>el.open))await incomingGroup.locator(':scope > summary').click();
    await incoming.getByRole('link',{name:'Follow connection',exact:false}).click();
    const assertRestart=async()=>{
      await page.waitForFunction(selected=>explorerState.id===selected,id('trail-100'));
      assert.deepEqual(await page.evaluate(()=>({mode:explorerState.mode,start:explorerState.trail.start,steps:explorerState.trail.steps.length,valid:explorerState.trail.valid})),{mode:'order-to-cash',start:id('trail-101'),steps:1,valid:true});
      assert.equal(await page.locator('.reading-trail li').count(),2);
    };
    await assertRestart();await page.reload();await assertRestart();
    passed.push('An arbitrary-concept restart remains usable in a value-stream view after follow and reload');
    assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
    return passed;
  } finally {await context.close();await rm(folder,{recursive:true,force:true});}
}
