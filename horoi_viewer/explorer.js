"use strict";
let explorerState = null;
const streamModes = {commercial:explorer.streamNamespace+"stream/commercial-hydrocarbon-lifecycle","order-to-cash":explorer.streamNamespace+"stream/order-to-cash"};
const streamNames = {commercial:"Commercial Hydrocarbon Lifecycle","order-to-cash":"Order to Cash"};
const explorerNames = {process:"Process explorer",customer:"Customer lifecycle",measures:"Measures and KPIs",...Object.fromEntries(Object.entries(streamModes).map(([mode,id])=>[mode,nodes.get(id)?.label||streamNames[mode]]))};
const isExplorerRoute = route => Object.hasOwn(explorerNames,route);
const explorerHref = (mode,id="",trail=null) => "#"+mode+"?"+new URLSearchParams({at:id,...(trail?.steps.length?{trail:JSON.stringify({start:trail.start,steps:trail.steps})}:{})});
const explorerLabel = id => {
  const level=explorer.level(id), code=explorer.notation(id);
  return `${level!==""?`<span class="level">L${e(level)}</span> `:""}${e(title(id))}${code && explorer.processes.has(id)?` <span class="quiet">${e(code)}</span>`:""}`;
};
const exploreLink = (mode,id,label=null,trail=null) => nodes.has(id)
  ? `<a href="${e(explorerHref(mode,id,trail))}" title="${e(id)}">${label||e(title(id))}</a>`
  : `<span title="${e(id)}">${label||e(title(id))}</span>`;

function valueStreamTiles() {
  return `<div class="grid">${Object.entries(streamModes).map(([mode,id])=>{
    const node=nodes.get(id), heading=`<span class="eyebrow">Value stream</span><h3>${e(explorerNames[mode])}</h3>`;
    return node
      ? `<a class="tile" href="#${e(mode)}">${heading}<p>${e(definition(node))}</p><span class="go">Explore stages and connections →</span></a>`
      : `<article class="tile">${heading}<p>This value stream is not included in this release.</p></article>`;
  }).join("")}</div>`;
}
function valueStreamsPage() {
  return `${crumb(["Value streams"])}<h1>Value streams</h1><p class="lead">Follow a value stream through its stages, then explore the processes and concepts connected to each stage.</p>${valueStreamTiles()}<p class="note">Stage positions come from the released ontology. Processes within a stage are listed alphabetically. Feedback and other process relationships keep their own labels and directions.</p>`;
}
function streamTrail(stream,stage,process=null) {
  const steps=[{s:stream,p:explorer.streamNamespace+"hasStage",o:stage}];
  if(process) steps.push({s:stage,p:explorer.streamNamespace+"hasProcess",o:process});
  return {start:stream,steps};
}
function streamSidebar(mode,stream,id) {
  const stages=explorer.streamStages(stream), trail=explorerState.trail;
  const visited=[trail.start,...trail.steps.flatMap(r=>[r.s,r.o])];
  return `<aside class="explorer-sidebar" id="explorer-start"><h2>Stages in this stream</h2><p class="quiet">Follow the recorded stage positions. Select a stage, then choose one of its processes.</p><a href="#${e(mode)}">Back to the stream overview</a><ol class="stream-stage-list">${stages.map(stage=>{
    const ps=explorer.stageProcesses(stage.id), active=stage.id===id||visited.includes(stage.id)||ps.includes(id);
    return `<li class="${active?'active-stage':''}"><div class="stream-stage-heading"><span class="level">${stage.position===null?'?':e(stage.position)}</span>${exploreLink(mode,stage.id,null,streamTrail(stream,stage.id))}</div><details ${active?'open':''}><summary>${ps.length} processes</summary><ul>${ps.map(p=>`<li>${exploreLink(mode,p,null,streamTrail(stream,stage.id,p))}</li>`).join("")}</ul></details></li>`;
  }).join("")}</ol><a href="#streams">Choose another value stream</a></aside>`;
}
function streamContext(id) {
  const {mode}=explorerState, stream=streamModes[mode];
  if(!stream) return "";
  const stages=explorer.streamStages(stream), stage=stages.find(s=>s.id===id);
  if(id===stream) {
    const n=nodes.get(id), fields=[["What starts it","trigger"],["What it delivers","outcome"]];
    const known=stages.filter(s=>s.position!==null).map(s=>s.position);
    const ambiguous=known.length!==stages.length||new Set(known).size!==known.length;
    return `<section class="stream-overview"><div class="grid">${fields.map(([label,p])=>`<div class="panel"><h3>${label}</h3>${vals(n,explorer.streamNamespace+p).length?valuesHtml(vals(n,explorer.streamNamespace+p)):"<p>No statement is recorded.</p>"}</div>`).join("")}</div><h2>Walk through the stages</h2><p>Numbers show the recorded stage positions. Open a stage to see its processes and follow their connections.</p>${ambiguous?'<p class="note">Some stage positions are missing, invalid or shared. Equal positions are listed alphabetically; stages without one are listed last. No unique order is implied for those stages.</p>':""}<ol class="stream-map">${stages.map(s=>`<li><span class="stage-number">${s.position===null?'?':e(s.position)}</span><div><h3>${exploreLink(mode,s.id,null,streamTrail(stream,s.id))}</h3><p>${nodes.has(s.id)?e(definition(nodes.get(s.id))):"No description is included in this release."}</p><span class="quiet">${explorer.stageProcesses(s.id).length} processes</span></div></li>`).join("")}</ol></section>`;
  }
  if(stage) {
    const ps=explorer.stageProcesses(id);
    return `<section class="stream-overview"><p class="note">Stage ${stage.position===null?'position not uniquely recorded':e(stage.position)} in ${exploreLink(mode,stream)}.</p><h2>Processes in this stage</h2><p>Choose a process to follow its connected concepts. This list is alphabetical; stage membership does not specify process execution order.</p><div class="grid stage-processes">${ps.map(p=>`<a class="tile" href="${e(explorerHref(mode,p,streamTrail(stream,id,p)))}" title="${e(p)}"><span class="eyebrow">Value-stream process</span><h3>${e(title(p))}</h3><span class="go">Explore connections →</span></a>`).join("")}</div></section>`;
  }
  const memberships=stages.filter(s=>explorer.stageProcesses(s.id).includes(id));
  return memberships.length?`<p class="note">In this stream: ${memberships.map(s=>exploreLink(mode,s.id,`Stage ${s.position===null?'?':e(s.position)} · ${e(title(s.id))}`,streamTrail(stream,s.id))).join(" · ")}. ${exploreLink(mode,stream,"Return to the stream overview")}.</p>`:"";
}
function explorerKind(n) {
  if(explorer.processes.has(n.id)) return "Process-map concept";
  const types=vals(n,RDF+"type").filter(v=>!v.literal).map(v=>v.v);
  if(types.includes(moduleInfo("kpi")?.id+"/MeasureDefinition")) return "Measure definition";
  if(types.includes("http://www.w3.org/ns/org#Role")) return "Role";
  const kinds={ValueStream:"Value stream",Stage:"Value-stream stage",ValueStreamProcess:"Value-stream process",Capability:"Capability",MeasureLink:"Measure link"};
  return Object.entries(kinds).find(([type])=>types.includes(explorer.streamNamespace+type))?.[1]||n.kind;
}

function processTreeItem(id, ancestry=[], expanded=new Set()) {
  const {mode}=explorerState;
  const label=exploreLink(mode,id,explorerLabel(id));
  if (ancestry.includes(id)) return `<li>${label} <span class="quiet">Already on this branch; follow its reference.</span></li>`;
  const children=explorer.children.get(id)||[], path=[...ancestry,id];
  const current=id===explorerState.id?' class="selected-process"':"";
  return children.length
    ? `<li${current}><details class="process-branch" data-path="${e(JSON.stringify(path))}" ${expanded.has(id)?"open":""}><summary>${label}<span class="quiet"> · ${children.length} below</span></summary><ul data-children="${e(id)}" ${expanded.has(id)?'data-loaded="true"':""}>${expanded.has(id)?children.map(child=>processTreeItem(child,path,expanded)).join(""):""}</ul></details></li>`
    : `<li${current}><span class="tree-leaf">${label}</span></li>`;
}

function explorerTrail() {
  const {mode,trail}=explorerState;
  if (!trail.steps.length) return "";
  let at=trail.start;
  const trailLink=(id,prefix=null)=>exploreLink(mode,id,`${e(title(id))}<span class="quiet"> · ${e(explorerKind(nodes.get(id)))}</span>`,prefix);
  const parts=[`<li>${trailLink(at)}</li>`];
  trail.steps.forEach((r,i)=>{
    const forward=r.s===at, next=forward?r.o:r.s;
    const prefix={start:trail.start,steps:trail.steps.slice(0,i+1)};
    parts.push(`<li class="trail-edge"><span aria-label="${forward?'outgoing':'incoming'} relationship">${forward?'→':'←'} ${e(title(r.p))} ${forward?'→':'←'}</span> ${trailLink(next,prefix)}</li>`);
    at=next;
  });
  return `<details class="reading-trail" open><summary>Your connection trail</summary><ol>${parts.join("")}</ol><p class="quiet">Arrows retain the direction of each recorded statement. Select an earlier item to return there.</p></details>`;
}

function explorerFollow(row) {
  const {mode,id,trail}=explorerState, next=row.s===id?row.o:row.s;
  // Returning to an earlier node closes a cycle instead of growing the URL forever.
  let at=trail.start;
  if (next===at) return {href:explorerHref(mode,next),returning:true};
  for (let i=0;i<trail.steps.length;i++) {
    const r=trail.steps[i];at=r.s===at?r.o:r.s;
    if (next===at) return {href:explorerHref(mode,next,{start:trail.start,steps:trail.steps.slice(0,i+1)}),returning:true};
  }
  if (trail.steps.length>=100) return {href:explorerHref(mode,next),restart:true};
  return {href:explorerHref(mode,next,{start:trail.start,steps:[...trail.steps,row]})};
}

function connectionGroup(row,id) {
  const other=nodes.get(row.s===id?row.o:row.s), p=row.p;
  if (!other || other.id.startsWith("_:") || data.supportingKinds.includes(other.kind) || other.kind==="Metadata"
      || p.startsWith("http://purl.org/dc/terms/")) return "Sources, rules and evidence";
  if ([RDF+"type",RDFS+"subClassOf",RDFS+"subPropertyOf",RDFS+"domain",RDFS+"range",SKOS+"inScheme",SKOS+"topConceptOf",SKOS+"hasTopConcept"].includes(p)) return "Vocabulary and types";
  if (explorer.processes.has(other.id)) return "Processes";
  const ms=moduleNames(other);
  const party=moduleInfo("party");
  if (ms.includes("system") || (party && (vals(other,SKOS+"inScheme").some(v=>!v.literal && v.v===party.id+"/system-stage") || p===party.id+"/stageSystem"))) return "Systems and system stages";
  if (ms.includes("organization") || vals(other,RDF+"type").some(v=>!v.literal && v.v==="http://www.w3.org/ns/org#Role")) return "People and responsibilities";
  if (ms.includes("kpi")) return "Measures";
  if (ms.includes("data-product")||ms.includes("logical-model")||ms.includes("integration")||ms.includes("technical-graph")) return "Data and integration";
  if (ms.includes("value-stream")) {
    if (explorerKind(other)==="Capability") return "Capabilities";
    if (explorerKind(other)==="Measure link") return "Measures";
    return "Value streams";
  }
  if (ms.includes("party")) return "Customer domain";
  return "Business context";
}

function explorerCard(row) {
  const {mode,id}=explorerState, next=row.s===id?row.o:row.s, other=nodes.get(next), follow=explorerFollow(row);
  const endpoint=which => which===id?`<strong>${e(title(which))}</strong>`:nodes.has(which)?`<a href="${e(follow.href)}" title="${e(which)}">${e(title(which))}</a>`:`<span title="${e(which)}">${e(title(which))}</span>`;
  return `<article class="connection-card" data-subject="${e(row.s)}" data-predicate="${e(row.p)}" data-object="${e(row.o)}">
    <div class="statement"><div><span class="quiet">From</span>${endpoint(row.s)}</div><div class="statement-relation"><span class="quiet">Relationship →</span>${exploreLink(mode,row.p)}${relationshipExplanation(row.p)}</div><div><span class="quiet">To</span>${endpoint(row.o)}</div></div>
    <div class="connection-meta"><span>${other?e(moduleNames(other).join(", ")+" · "+explorerKind(other)):"External reference"}</span>${other?`<a href="${e(follow.href)}">${follow.returning?'Return to this item':follow.restart?'Start a new trail here':'Follow connection'} →</a>`:"<span>No description is included in this release.</span>"}</div>
    ${other && definitions(other).length?`<details class="connection-definition"><summary>Read the connected item's definition</summary><p>${e(definition(other))}</p></details>`:""}</article>`;
}

function explorerConnections() {
  const {id}=explorerState, rows=explorer.adjacent(id), groups=new Map();
  for (const r of rows) {
    const group=connectionGroup(r,id);
    if (!groups.has(group)) groups.set(group,[]);
    groups.get(group).push(r);
  }
  const order=["Processes","Customer domain","Systems and system stages","People and responsibilities","Data and integration","Measures","Capabilities","Value streams","Business context","Vocabulary and types","Sources, rules and evidence"];
  const visible=order.filter(g=>groups.has(g));
  return `<section class="section" id="explorer-connections"><h2>Connected to this item</h2><p>Read each card from <strong>From</strong> to <strong>To</strong>. Follow either end to continue across the ontology. These groups organize recorded connections by the other item's kind and module. Only groups with recorded connections appear. Follow the available connections to explore further.</p>
    ${rows.length?`<nav class="connection-shortcuts" aria-label="Connection groups">${visible.map((g,i)=>`<button type="button" data-jump="connection-group-${i}">${e(g)} (${groups.get(g).length})</button>`).join("")}</nav>`:""}
    ${rows.length?visible.map((g,i)=>{
      const rs=groups.get(g), closed=["Sources, rules and evidence","Vocabulary and types","Business context"].includes(g);
      return `<details id="connection-group-${i}" class="connection-group" ${closed?"":"open"}><summary>${e(g)} <span class="quiet">${rs.length} statements</span></summary>${rs.slice(0,6).map(explorerCard).join("")}${rs.length>6?`<details><summary>Show ${rs.length-6} more statements</summary>${rs.slice(6).map(explorerCard).join("")}</details>`:""}</details>`;
    }).join(""):"<p>No connection to another term is recorded.</p>"}</section>`;
}

function processPosition(id) {
  if (!explorer.processes.has(id)) return "";
  const {mode}=explorerState, parents=explorer.parents.get(id)||[], children=explorer.children.get(id)||[];
  const path=explorer.ancestry(id);
  const hierarchyLink=(other,row)=>`<a href="${e(explorerFollow(row).href)}" title="${e(other)}">${explorerLabel(other)}</a>`;
  return `<section class="process-position"><h2>Where this sits in the process tree</h2><nav aria-label="Process ancestry"><ol class="ancestry">${path.map(p=>`<li>${exploreLink(mode,p,explorerLabel(p))}</li>`).join("")}</ol></nav>
    <p class="quiet">Each step down follows a child's recorded broader concept. This shows the hierarchy; workflow order uses its own named relationships.</p>
    ${parents.length>1?`<p>This process has multiple parents. The path above is one route to a root.</p>`:""}
    <div class="position-grid"><div><h3>${parents.length>1?'Parents':'Parent'}</h3>${parents.length?`<ul>${parents.map(p=>`<li>${hierarchyLink(p,{s:id,p:SKOS+"broader",o:p})}</li>`).join("")}</ul>`:"<p>No parent process is recorded.</p>"}</div>
    <div><h3>Go deeper</h3>${children.length?`<ul>${children.map(c=>`<li>${hierarchyLink(c,{s:c,p:SKOS+"broader",o:id})}</li>`).join("")}</ul>`:"<p>This is the lowest recorded level on this branch. Its other connections remain below.</p>"}</div></div></section>`;
}

function measureContext(n) {
  const info=moduleInfo("kpi");
  if (!info) return "";
  const ns=info.id+"/";
  if (!vals(n,RDF+"type").some(v=>!v.literal && v.v===ns+"MeasureDefinition")) return "";
  const fields=[["Recorded kind",ns+"measureKind"],["Identifier","http://purl.org/dc/terms/identifier"],["Notation",SKOS+"notation"],["Basis",ns+"basis"],["Grain",ns+"grain"],["Compared against",ns+"comparedAgainst"],["KPI candidate",ns+"kpiCandidate"]];
  const value = v => {
    if (v.literal) return e(v.v);
    if (!nodes.has(v.v)) return `<span title="${e(v.v)}">${e(title(v.v))}</span>`;
    const follow=explorerFollow({s:n.id,p:v.p,o:v.v});
    return `<a href="${e(follow.href)}" title="${e(v.v)}">${e(title(v.v))}${follow.restart?' (start a new trail)':''}</a>`;
  };
  return `<section class="section measure-context"><h3>About this measure</h3><dl>${fields.filter(([,p])=>vals(n,p).length).map(([label,p])=>`<dt>${e(label)}</dt><dd>${vals(n,p).map(value).join("; ")}</dd>`).join("")}</dl><p class="quiet">The recorded kind determines its classification. An identifier or candidate flag does not change that kind. Connections below retain their own meanings; informing a process does not mean owning or computing it.</p></section>`;
}

function explorerSelection() {
  const {id,mode,trail}=explorerState, n=nodes.get(id);
  if (!n) return `<section class="panel"><h2>Choose a ${mode==='customer'?'lifecycle stage':mode==='measures'?'measure':'process'}</h2><p>Select an item to read its definition and follow its connections.</p></section>`;
  return `<section class="explorer-selection" aria-label="Selected item">
    ${!trail.valid?'<p class="note">This saved trail contains an unavailable or unconnected statement. Showing the selected item without that trail.</p>':""}${explorerTrail()}
    <div class="eyebrow">${e(moduleNames(n).join(" · "))} · ${e(explorerKind(n))}</div><h2 id="selected-title">${explorerLabel(id)}</h2>
    <div class="term-definition">${valuesHtml(definitions(n))||"<p>No definition is recorded.</p>"}</div>
    ${vals(n,SKOS+"scopeNote").length?`<div class="note">${valuesHtml(vals(n,SKOS+"scopeNote"))}</div>`:""}
    <div class="actions"><a href="#explorer-connections" data-jump="explorer-connections">See connections</a><a href="#explorer-start" data-jump="explorer-start">Choose another ${mode==='process'?'process':mode==='measures'?'measure':'stage'}</a><a href="${e(termHref(id))}">Open reference page</a></div>
    ${measureContext(n)}${streamContext(id)}${processPosition(id)}${explorerConnections()}
    <details><summary>All recorded facts, types and sources</summary><code class="explorer-iri">${e(id)}</code>${facts(n)}</details></section>`;
}

function explorerSidebar(mode,id) {
  if (mode==="measures") return `<aside class="explorer-sidebar measure-sidebar" id="explorer-start"><h2>Choose a starting measure</h2>${measureCatalogue("measures")}</aside>`;
  if (streamModes[mode]) return streamSidebar(mode,streamModes[mode],id);
  if (mode==="process") {
    const expanded=new Set(explorer.ancestry(id));
    return `<aside class="explorer-sidebar" id="explorer-start"><h2>Process tree</h2><p class="quiet">Expand a branch, then select a process. L labels show the recorded depth.</p><label>Find a process<input type="search" id="process-search" placeholder="Name, definition or code" value="${e(explorerState.query)}"></label><div id="process-search-results" aria-live="polite"></div><ul class="process-tree">${explorer.roots.map(r=>processTreeItem(r,[],expanded)).join("")}</ul>${explorer.unplaced.length?`<details><summary>Processes without a route from a root</summary><ul>${explorer.unplaced.map(r=>processTreeItem(r)).join("")}</ul></details>`:""}</aside>`;
  }
  return `<aside class="explorer-sidebar" id="explorer-start"><h2>Lifecycle stages</h2><p class="quiet">Choose any stage. The source records these stages without a sequence; the list is alphabetical.</p><ul class="stage-list">${explorer.stages.map(s=>`<li${s===id?' class="selected-stage"':""}>${exploreLink(mode,s)}<p>${e(definition(nodes.get(s)))}</p></li>`).join("")}</ul><a href="#module=party">Read the customer domain reference</a></aside>`;
}
function explorerLead(mode) {
  if (mode==="measures") return "Start with a KPI, operational metric or another recorded entry. Follow its connections to processes, planning users, data and systems. Each step stays in your connection trail.";
  if (streamModes[mode]) return "Follow the stages, choose a process, and explore its connected concepts. Your trail keeps the path back to this value stream.";
  if (mode==="process") return "Start at the top of the process tree. Walk down each branch, then follow the people, systems, data and other items connected to it.";
  return "Start with a customer lifecycle stage. Follow its processes and system stages, then explore the connections around each one.";
}

function explorerPage(mode,params) {
  const requested=params.get("at"), id=requested===null?(streamModes[mode]||(mode==="process"?explorer.roots[0]||"":"")):requested;
  if (id && !nodes.has(id)) return missing("This item is not included in the release. Choose a process, measure, customer lifecycle stage or value stream.");
  const trail=explorer.readTrail(params.get("trail"),id);
  const origin=trail.valid && trail.steps.length ? Object.keys(streamModes).find(key=>streamModes[key]===trail.start) : null;
  if(Object.hasOwn(streamModes,mode) && origin && origin!==mode) {
    mode=origin;params.set("at",id);
    history.replaceState(null,"","#"+mode+"?"+params);
  }
  explorerState={mode,id,query:params.get("q")||"",trail};
  return `${crumb([e(explorerNames[mode])])}<h1>${e(explorerNames[mode])}</h1><p class="lead">${explorerLead(mode)}</p>
    <div class="actions"><a href="#process" ${mode==="process"?'aria-current="page"':""}>Process explorer</a><a href="#customer" ${mode==="customer"?'aria-current="page"':""}>Customer lifecycle</a><a href="#measures" ${mode==="measures"?'aria-current="page"':""}>Measures and KPIs</a><a href="#streams" ${streamModes[mode]?'aria-current="page"':""}>Value streams</a></div>
    <div class="explorer-layout">${explorerSidebar(mode,id)}<div>${explorerSelection()}</div></div>`;
}

function bindExplorer() {
  for (const jump of main.querySelectorAll("[data-jump]")) jump.onclick=event=>{
    event.preventDefault();const target=document.getElementById(jump.dataset.jump);
    if (!target) return;
    if (target.matches("details")) target.open=true;
    const focus=target.matches("details")?target.querySelector("summary"):target;
    if (!target.matches("details")) focus.tabIndex=-1;
    focus.focus();target.scrollIntoView({block:"start"});
  };
  const input=document.getElementById("process-search");
  if (input) {
    const search=()=>{
    const q=input.value.trim().toLowerCase(), result=document.getElementById("process-search-results");
    if (!q) { result.innerHTML="";return; }
    const found=[...explorer.processes].filter(id=>(title(id)+" "+id+" "+definition(nodes.get(id))).toLowerCase().includes(q)).sort(explorer.compare);
    result.innerHTML=`<p class="quiet">${found.length} matches${found.length>30?". Showing the first 30; refine your search for more.":"."}</p><ul>${found.slice(0,30).map(id=>`<li>${exploreLink(explorerState.mode,id,explorerLabel(id))}</li>`).join("")}</ul>`;
    };
    input.oninput=()=>{
      const params=new URLSearchParams(location.hash.split("?")[1]||"");
      if(input.value) params.set("q",input.value);else params.delete("q");
      history.replaceState(null,"","#process?"+params);search();
    };
    search();
  }
}
main.addEventListener("toggle",event=>{
  const branch=event.target;
  if (!branch.matches("details.process-branch")||!branch.open) return;
  const list=branch.querySelector(":scope > ul");
  if (list.dataset.loaded) return;
  const path=JSON.parse(branch.dataset.path);
  list.innerHTML=(explorer.children.get(list.dataset.children)||[]).map(id=>processTreeItem(id,path)).join("");
  list.dataset.loaded="true";
},true);
