"use strict";

// Index existing assertions only. Kept separate from the UI for counterexample tests.
function createExplorerIndex(data) {
  const skos = "http://www.w3.org/2004/02/skos/core#";
  const byId = new Map(data.nodes.map(n => [n.id, n]));
  const namespace = name => data.moduleInfo.find(m => m.name === name)?.id + "/";
  const levelPredicate = namespace("core") + "taxonomyLevel";
  const stageScheme = namespace("party") + "lifecycle-stage";
  const streamNamespace = namespace("value-stream");
  const values = (id, p) => (byId.get(id)?.values || []).filter(v => v.p === p);
  const compare = (a,b) => (byId.get(a)?.label || a).localeCompare(byId.get(b)?.label || b) || a.localeCompare(b);
  const sorted = ids => [...new Set(ids)].sort(compare);
  const objects = (id,p) => sorted(values(id,p).filter(v=>!v.literal).map(v=>v.v));
  function streamStages(id) {
    return objects(id,streamNamespace+"hasStage").map(stage=>{
      const recorded=values(stage,streamNamespace+"sequence").filter(v=>v.literal).map(v=>v.v);
      const numbers=recorded.map(v=>/^\+?\d+$/.test(v)?Number(v):NaN);
      const position=recorded.length===1 && Number.isSafeInteger(numbers[0]) && numbers[0]>0?numbers[0]:null;
      return {id:stage,position,recorded};
    }).sort((a,b)=>(a.position??Infinity)-(b.position??Infinity)||compare(a.id,b.id));
  }
  const stageProcesses = id => objects(id,streamNamespace+"hasProcess");
  const processes = new Set(data.nodes.filter(n => values(n.id,levelPredicate).some(v => v.literal)).map(n => n.id));
  const stages = sorted(data.nodes.filter(n => values(n.id,skos+"inScheme").some(v => !v.literal && v.v === stageScheme)).map(n => n.id));
  const parents = new Map(), children = new Map(), incoming = new Map();
  for (const n of data.nodes) {
    for (const v of n.values) if (!v.literal) {
      if (!incoming.has(v.v)) incoming.set(v.v,[]);
      incoming.get(v.v).push({s:n.id,p:v.p,o:v.v});
    }
    if (!processes.has(n.id)) continue;
    parents.set(n.id, sorted(values(n.id,skos+"broader").filter(v => !v.literal && processes.has(v.v)).map(v => v.v)));
    for (const p of parents.get(n.id)) {
      if (!children.has(p)) children.set(p,[]);
      children.get(p).push(n.id);
    }
  }
  for (const [p, ids] of children) children.set(p,sorted(ids));
  const roots = sorted([...processes].filter(id => !parents.get(id).length));
  const reached = new Set(), pending = [...roots];
  while (pending.length) {
    const id = pending.pop();
    if (reached.has(id)) continue;
    reached.add(id);pending.push(...children.get(id)||[]);
  }
  const unplaced = sorted([...processes].filter(id => !reached.has(id)));
  function ancestry(id) {
    const queue = [[id]], seen = new Set([id]);
    for (let i=0;i<queue.length;i++) {
      const path=queue[i], ps=parents.get(path[0])||[];
      if (!ps.length) return path;
      for (const p of ps) if (!seen.has(p)) { seen.add(p);queue.push([p,...path]); }
    }
    return [id]; // A closed cycle has no root; do not manufacture one.
  }
  function adjacent(id) {
    const out=(byId.get(id)?.values||[]).filter(v=>!v.literal).map(v=>({s:id,p:v.p,o:v.v}));
    const unique=new Map([...out,...incoming.get(id)||[]].map(r=>[JSON.stringify(r),r]));
    return [...unique.values()];
  }
  const asserted = r => byId.get(r.s)?.values.some(v => !v.literal && v.p===r.p && v.v===r.o);
  // A route is untrusted input. Each hop must be an asserted, connected edge.
  function readTrail(serialized, selected) {
    if (!serialized) return {start:selected, steps:[], valid:true};
    try {
      const trail=JSON.parse(serialized);
      if (!byId.has(trail.start) || !Array.isArray(trail.steps) || trail.steps.length>100) throw Error();
      let at=trail.start;
      for (const r of trail.steps) {
        if (!r || !asserted(r) || (r.s!==at && r.o!==at)) throw Error();
        at=r.s===at?r.o:r.s;
        if (!byId.has(at)) throw Error();
      }
      if (at!==selected) throw Error();
      return {...trail,valid:true};
    } catch { return {start:selected,steps:[],valid:false}; }
  }
  return {byId, incoming, processes, stages, parents, children, roots, unplaced, ancestry, adjacent, asserted, readTrail, streamStages, stageProcesses, streamNamespace,
    level:id=>values(id,levelPredicate).filter(v=>v.literal).map(v=>v.v).join(", "),
    notation:id=>values(id,skos+"notation").find(v=>v.literal)?.v || "", compare};
}
