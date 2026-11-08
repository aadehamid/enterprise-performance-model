const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const {join} = require('node:path');
const assert = require('node:assert/strict');
const source = readFileSync(join(__dirname,'explorer-model.js'),'utf8');
const makeIndex = runInNewContext(source+'; createExplorerIndex');
const broader='http://www.w3.org/2004/02/skos/core#broader';
const level='urn:core/taxonomyLevel';
const edge=(p,v)=>({p,v,literal:false});
const process=(id,depth,parents=[])=>({id,label:id,values:[{p:level,v:String(depth),literal:true},...parents.map(p=>edge(broader,p))]});
const nodes=[process('root',0)];
for(let i=1;i<=9;i++) nodes.push(process('p'+i,i,[i===1?'root':'p'+(i-1)]));
nodes.push(process('other',1,['root']),process('shared',2,['p1','other']),process('cycle-a',1,['cycle-b']),process('cycle-b',2,['cycle-a']));
nodes.push({id:'duplicate-a',label:'Same name',values:[]},{id:'duplicate-b',label:'Same name',values:[]});
nodes.push({id:'stage',label:'Stage',values:[edge('http://www.w3.org/2004/02/skos/core#inScheme','urn:party/lifecycle-stage'),edge('urn:party/stageProcess','p9')]});
nodes.push({id:'system',label:'System',values:[edge('urn:supports','p9')]});
const data={nodes,moduleInfo:[{name:'core',id:'urn:core'},{name:'party',id:'urn:party'}]};
const before=JSON.stringify(data), ix=makeIndex(data);
assert.equal(JSON.stringify(data),before,'The index does not mutate source facts');
assert.equal(ix.ancestry('p9').join(','),'root,p1,p2,p3,p4,p5,p6,p7,p8,p9','Depth is not limited to L6');
assert.equal(ix.parents.get('shared').join(','),'other,p1','Both recorded parents remain');
assert.equal(ix.children.get('other').join(','),'shared');
assert.equal(ix.unplaced.join(','),'cycle-a,cycle-b','A rootless cycle stays reachable as unplaced processes');
assert.equal(ix.ancestry('cycle-a').join(','),'cycle-a','A cycle cannot recurse forever');
assert.ok(ix.byId.has('duplicate-a')&&ix.byId.has('duplicate-b'),'Duplicate labels retain separate identities');
assert.equal(ix.stages.join(','),'stage');
const steps=[{s:'stage',p:'urn:party/stageProcess',o:'p9'},{s:'system',p:'urn:supports',o:'p9'}];
const trail=JSON.stringify({start:'stage',steps});
assert.ok(ix.readTrail(trail,'system').valid,'Incoming links can be followed without reversing their assertion');
assert.ok(!ix.readTrail(trail,'root').valid,'The selected item must match the trail');
assert.ok(!ix.readTrail(JSON.stringify({start:'stage',steps:[{s:'p9',p:'urn:party/stageProcess',o:'stage'}]}),'p9').valid,'An invented inverse is refused');
assert.ok(!ix.readTrail(JSON.stringify({start:'root',steps}),'system').valid,'Disconnected hops are refused');
assert.ok(!ix.readTrail('null','p9').valid);
assert.ok(!ix.readTrail('{bad','p9').valid);
assert.equal(ix.adjacent('p9').filter(r=>r.p==='urn:supports').length,1);
const rawIncoming=nodes.flatMap(n=>n.values.filter(v=>!v.literal&&v.v==='p9').map(v=>({s:n.id,p:v.p,o:v.v})));
assert.equal(JSON.stringify(ix.incoming.get('p9')),JSON.stringify(rawIncoming),'The shared incoming index preserves raw order and records for both views');
console.log('Explorer model counterexamples passed: depth, multiple parents, cycles, identity and asserted trails.');

const stream='urn:vs/stream', vs='urn:vs/';
const stage=(id,positions)=>({id,label:id,values:positions.map(v=>({p:vs+'sequence',v,literal:true}))});
const streamData={moduleInfo:[{name:'value-stream',id:'urn:vs'}],nodes:[
  {id:stream,label:'Stream',values:['z-first','a-second','ten','tie','missing','conflict','invalid','external'].map(id=>edge(vs+'hasStage',id))},
  stage('z-first',['1']),stage('a-second',['2']),stage('ten',['10']),stage('tie',['2']),
  stage('missing',[]),stage('conflict',['3','4']),stage('invalid',['1.5'])
]};
const streamIndex=makeIndex(streamData), ordered=streamIndex.streamStages(stream);
assert.equal(ordered.slice(0,4).map(s=>s.id).join(','),'z-first,a-second,tie,ten','Numeric positions win over labels and lexical number order');
assert.equal(ordered.find(s=>s.id==='tie').position,2,'A tied position remains tied');
for(const id of ['missing','conflict','invalid','external']) assert.equal(ordered.find(s=>s.id===id).position,null,'Missing or ambiguous positions are not invented');
assert.ok(!streamIndex.asserted({s:'z-first',p:vs+'precedes',o:'a-second'}),'Sequence display does not manufacture a process edge');
assert.equal(streamIndex.stageProcesses('z-first').length,0,'Stage order does not imply process membership');
console.log('Value-stream counterexamples passed: numeric ordering, ties, absent/invalid positions and no invented edges.');
