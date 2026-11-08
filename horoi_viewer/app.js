"use strict";
const data = JSON.parse(document.getElementById("ontology-data").textContent);
const explorer = createExplorerIndex(data);
const nodes = explorer.byId;
const referenceTerms = new Set(data.referenceTerms);
const RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
const RDFS = "http://www.w3.org/2000/01/rdf-schema#";
const SKOS = "http://www.w3.org/2004/02/skos/core#";
const main = document.getElementById("content");
const incoming = explorer.incoming;
const e = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c]);
const short = id => id.replace(/[/#]$/, "").split(/[/#]/).pop();
const title = id => nodes.get(id)?.label || short(id);
const moduleNames = n => n.modules.map(m => m.name).filter(m => m !== "Release metadata");
const isLocal = n => n && moduleNames(n).some(m => data.referenceModules.includes(m));
const viewerHref = id => "../viewer/index.html#" + encodeURIComponent(id);
const termHref = id => isLocal(nodes.get(id)) ? "#term=" + encodeURIComponent(id) : viewerHref(id);
const link = id => nodes.has(id)
  ? `<a href="${e(termHref(id))}" title="${e(id)}">${e(title(id))}</a>`
  : `<span title="${e(id)}">${e(title(id))}</span>`;
const vals = (n, p) => n.values.filter(v => v.p === p);
const definitions = n => vals(n, SKOS+"definition").length ? vals(n, SKOS+"definition") : vals(n, RDFS+"comment");
const definition = n => definitions(n).find(v => !v.lang || v.lang === "en")?.v || definitions(n)[0]?.v || "No definition is recorded.";
const layer = n => ["Class","Property"].includes(n.kind) ? "Vocabulary" : data.supportingKinds.includes(n.kind) || n.kind === "Metadata" ? "Rules and evidence" : "Business concepts";
const moduleLabel = m => ({party:"Party · Customer domain",core:"Core · Process map",
  "data-product":"Data products",integration:"Integration",kpi:"Measures and performance",lane:"Office lanes",
  "logical-model":"Logical models","market-data":"Market data",organization:"Organization and responsibilities",
  "ref-mpc":"MPC reference facts",system:"Systems","technical-graph":"Technical graph","value-stream":"Value streams"})[m] || m;
const pageLink = (m, l="") => "#browse?" + new URLSearchParams({module:m, layer:l});
const moduleLink = m => data.referenceModules.includes(m) ? `#module=${encodeURIComponent(m)}` : `../viewer/index.html#view=module:${encodeURIComponent(m)}`;
const moduleInfo = m => data.moduleInfo.find(i => i.name === m);
const valuesHtml = vs => vs.map(v => `<p>${e(v.v)}${v.lang ? `<span class="lang">${e(v.lang)}</span>` : ""}</p>`).join("");
const crumb = trail => `<div class="crumb"><a href="#overview">Overview</a>${trail.map(x=>` / ${x}`).join("")}</div>`;
const browseState = {q:"",module:"",layer:"",page:0};
const readingGroups = ["Business concepts","Vocabulary","Rules and evidence"];

function intro() {
  return `<div class="eyebrow">MPC Business Process and Architecture Ontology</div>
  <h1>Understand the concepts.<br>Follow their connections.</h1>
  <p class="lead">Start with the customer domain or the process map. Read what a term means, see how it connects to other terms, and follow those links across modules.</p>
  <div class="actions"><a class="primary" href="#module=party">Explore the customer domain</a><a href="#module=core">Explore the process map</a><a href="#guide">Take a guided tour</a></div>
  <section class="section"><h2>Walk through the connections</h2><div class="grid"><a class="tile core" href="#process"><span class="eyebrow">Start with a business process</span><h3>Process explorer</h3><p>Walk from the top of the process tree to its deepest branches. Follow the connections around each process.</p><span class="go">Open the process tree →</span></a><a class="tile party" href="#customer"><span class="eyebrow">Start with the customer</span><h3>Customer lifecycle</h3><p>Choose a lifecycle stage. Follow its processes and systems, and keep your connection trail as you explore.</p><span class="go">Explore lifecycle stages →</span></a></div></section>
  <section class="section"><h2>Follow a value stream</h2>${valueStreamTiles()}</section>
  <section class="section"><h2>Browse the modules</h2><div class="grid module-directory">${data.referenceModules.map(moduleTile).join("")}</div></section>
  <section class="section"><h2>Three ways to read the ontology</h2><p>These are reading groups. They help you distinguish the kinds of information in a module.</p>${layersHtml()}</section>
  <section class="section panel"><h2>How the modules connect</h2><p>Each module describes one part of the business. Recorded relationships connect its terms to terms in other modules. Module dependencies identify the versions it requires.</p><a href="#modules">See the modules and their connections</a></section>
  <p class="quiet section">Every current module in this release is available here. Use Modules and connections or Find a term to explore the full reference.</p>`;
}
function moduleTile(m) {
  const info = moduleInfo(m);
  return `<a class="tile ${e(m)}" href="${e(moduleLink(m))}"><span class="eyebrow">${e(m)} · ${e(info?.version || "")}</span><h2>${e(moduleLabel(m))}</h2><p>${e(info?.description || "Read this module in the full viewer.")}</p><span class="go">Open module →</span></a>`;
}
function layersHtml(m="") {
  const entries = [
    ["Business concepts","The things the model describes","Processes, code-list values and designed individuals give the vocabulary its business content. These are definitions and modelled concepts, not live operational records."],
    ["Vocabulary","The types and relationships","Classes describe kinds of thing. Properties name the relationships and attributes used to describe them."],
    ["Rules and evidence","How to read the supporting detail","Constraints record validation rules. Evidence and source references explain where statements come from. They are available from a term's detail."]
  ];
  return `<div class="grid layers">${entries.map(([l,t,d])=>`<div class="panel"><span class="eyebrow">${e(l)}</span><h3>${e(t)}</h3><p>${e(d)}</p><a href="${e(pageLink(m,l))}">Browse ${e(l.toLowerCase())}</a></div>`).join("")}</div>`;
}
function modulePage(m) {
  const info = moduleInfo(m);
  if (!info || !data.referenceModules.includes(m)) return missing("Choose a module included in this reference.");
  const candidates = data.nodes.filter(n => referenceTerms.has(n.id) && moduleNames(n).includes(m));
  const preferred = {
    party:["Party","CustomerAccount","PartyRole","Person","Organization"],
    "data-product":["DataProduct","DataProductLine","PlatformDataProduct"],
    "value-stream":["ValueStream","Stage","ValueStreamProcess","Capability"],
    "technical-graph":["TechnicalObject","DataObject","PipelineStep","Agent"],
    organization:["ResponsibilityAssignment","ControlRelationship"],
    "market-data":["MarketPrice","Benchmark","BenchmarkSeries"],
    kpi:["MeasureDefinition"],system:["System"],lane:["OfficeLane"],"logical-model":["LogicalModel"]
  };
  const owned=candidates.filter(n=>n.id.startsWith(info.id+"/"));
  const selected=m==="core" ? candidates.filter(n=>vals(n,info.id+"/taxonomyLevel").some(v=>v.literal&&v.v==="0"))
    : (preferred[m]||[]).map(name=>owned.find(n=>short(n.id)===name)).filter(Boolean);
  const featured=selected.length?selected:owned.filter(n=>n.kind!=="Property").slice(0,5);
  if(!featured.length) featured.push(...candidates.slice(0,5));
  return `${crumb([e(moduleLabel(m))])}<div class="eyebrow">${e(m)} · ${e(info.version)}</div><h1>${e(moduleLabel(m))}</h1><p class="lead">${e(info.description)}</p>
  <div class="actions"><a class="primary" href="${e(pageLink(m))}">Browse this module</a><a href="#connections=${e(m)}">Follow connections to other modules</a></div>
  ${m==="core"?'<p><a href="#process">Walk the process tree in the Process explorer</a></p>':m==="party"?'<p><a href="#customer">Walk through the Customer lifecycle</a></p>':""}
  <section class="section"><h2>Start here</h2><div class="grid">${featured.map(n=>`<a class="tile" href="${e(termHref(n.id))}"><h3>${e(n.label)}</h3><p>${e(definition(n))}</p><span class="go">Read ${e(n.label)} →</span></a>`).join("")}</div></section>
  <section class="section"><h2>Read the module in layers</h2>${layersHtml(m)}</section>
  <section class="section"><h2>Required modules</h2><p>These are declared package dependencies. They do not by themselves describe a business relationship.</p>${dependencies(info)}</section>`;
}
function dependencies(info) {
  return info.requires.length ? `<ul>${info.requires.map(id=>{
    const match = data.moduleInfo.find(m=>id===m.id || id.startsWith(m.id+"/"));
    return `<li>${match ? `<a href="${e(moduleLink(match.name))}">${e(moduleLabel(match.name))}</a>` : e(id)} <code>${e(id)}</code></li>`;
  }).join("")}</ul>` : "<p>No package dependency is declared in this module's ontology header.</p>";
}
function modulesPage() {
  return `${crumb(["Modules and connections"])}<h1>Modules and connections</h1><p class="lead">A module groups terms for one part of the model. Follow a term's relationship to see how those parts connect.</p>
  <div class="grid">${data.referenceModules.map(moduleTile).join("")}</div>
  <section class="section"><h2>Follow a recorded connection</h2><p>These views show actual statements from the released RDF, grouped by the module at the other end.</p><div class="actions">${data.referenceModules.map(m=>`<a href="#connections=${e(m)}">Connections from ${e(moduleLabel(m))}</a>`).join("")}</div></section>
  <p class="quiet section">All modules in this source release have local reference pages. The original ontology viewer remains available from the footer.</p>`;
}
function connectionRows(module) {
  const rows = [];
  for (const n of data.nodes) {
    if (!referenceTerms.has(n.id) || !moduleNames(n).includes(module)) continue;
    for (const v of n.values) {
      const target = !v.literal && nodes.get(v.v);
      if (!target || ["Metadata",...data.supportingKinds].includes(target.kind)) continue;
      for (const m of moduleNames(target)) if (m !== module && !moduleNames(n).includes(m))
        rows.push({s:n.id,p:v.p,o:v.v,module:m});
    }
  }
  return rows.sort((a,b)=>a.module.localeCompare(b.module)||title(a.s).localeCompare(title(b.s))||a.p.localeCompare(b.p)||a.o.localeCompare(b.o));
}
function connectionsPage(module) {
  if (!data.referenceModules.includes(module)) return missing("Choose a module to inspect its outgoing connections.");
  const rows = connectionRows(module);
  const groups = [...new Set(rows.map(r=>r.module))];
  return `${crumb([`<a href="${e(moduleLink(module))}">${e(moduleLabel(module))}</a>`,"Connections"])}<h1>Connections from ${e(moduleLabel(module))}</h1>
  <p class="lead">Read each row as a statement: the first term has the named relationship to the second term. Follow either term to read its definition and continue through the reference.</p>
  <p class="note">This view shows outgoing statements to named terms in other modules. It excludes evidence and package metadata. A property domain or range describes vocabulary; it does not assert a relationship between individual records.</p>
  ${groups.length ? groups.map(m=>`<section class="section"><h2>To ${e(moduleLabel(m))}</h2>${relationshipList(rows.filter(r=>r.module===m))}</section>`).join("") : '<p class="empty">No outgoing connection to another module is recorded for the terms in this view. Incoming links remain visible on each term.</p>'}`;
}
function relationshipTable(rows) {
  return `<div class="table-wrap relationship-table"><table><thead><tr><th scope="col">From</th><th scope="col">Relationship</th><th scope="col">To</th></tr></thead><tbody>${rows.map(r=>`<tr><td data-label="From">${link(r.s)}</td><td data-label="Relationship">${link(r.p)}</td><td data-label="To">${link(r.o)}</td></tr>`).join("")}</tbody></table></div>`;
}
function relationshipList(rows) {
  const preview = relationshipTable(rows.slice(0,8));
  return rows.length > 8
    ? preview + `<details><summary>Show ${rows.length-8} more statements (${rows.length} total)</summary>${relationshipTable(rows.slice(8))}</details>`
    : preview;
}
function browsePage(params) {
  browseState.q=params.get("q")||""; browseState.module=params.get("module")||""; browseState.layer=params.get("layer")||"";
  if(!data.referenceModules.includes(browseState.module)) browseState.module="";
  if(!readingGroups.includes(browseState.layer)) browseState.layer="";
  const requestedPage=Number(params.get("page"));
  browseState.page=Number.isSafeInteger(requestedPage)&&requestedPage>=0?requestedPage:0;
  return `${crumb(["Find a term"])}<h1>Find a term</h1><p>Search labels, definitions and identifiers. Filter by module or reading group to narrow the result.</p>
  <div class="filters"><label class="search">Search terms<input id="search" type="search" placeholder="Try customer account or a process name" value="${e(browseState.q)}"></label>
  <label>Module<select id="module-filter"><option value="">All modules</option>${data.referenceModules.map(m=>`<option value="${e(m)}" ${m===browseState.module?"selected":""}>${e(moduleLabel(m))}</option>`).join("")}</select></label>
  <label>Reading group<select id="layer-filter"><option value="">All groups</option>${readingGroups.map(l=>`<option ${l===browseState.layer?"selected":""}>${e(l)}</option>`).join("")}</select></label></div>
  <p id="result-count" role="status" class="quiet"></p><ul class="results" id="results"></ul><div id="pager" class="pager"><button id="prev">Previous</button><button id="next">Next</button></div>`;
}
function refreshResults() {
  const s=browseState;
  const found=data.nodes.filter(n=>isLocal(n) && (s.layer==="Rules and evidence" ? layer(n)===s.layer : referenceTerms.has(n.id))
    && (!s.module||moduleNames(n).includes(s.module)) && (!s.layer||layer(n)===s.layer)
    && (n.label+" "+n.id+" "+definition(n)).toLowerCase().includes(s.q.toLowerCase())).sort((a,b)=>a.label.localeCompare(b.label)||a.id.localeCompare(b.id));
  s.page=Math.min(s.page,Math.max(0,Math.ceil(found.length/40)-1));
  const start=s.page*40;
  document.getElementById("result-count").textContent=found.length ? `${found.length} results. Showing ${start+1} to ${Math.min(start+40,found.length)}.` : "No matching terms. Try a shorter name or clear the filters.";
  document.getElementById("results").innerHTML=found.slice(start,start+40).map(n=>`<li>${link(n.id)}<span class="badge">${e(n.kind)}</span><p>${e(moduleNames(n).join(", "))} · ${e(definition(n))}</p></li>`).join("");
  const prev=document.getElementById("prev"),next=document.getElementById("next");
  const focused=document.activeElement;
  prev.disabled=!s.page;next.disabled=start+40>=found.length;
  if(focused===prev&&prev.disabled&&!next.disabled) next.focus();
  if(focused===next&&next.disabled&&!prev.disabled) prev.focus();
  history.replaceState(null,"","#browse?"+new URLSearchParams({q:s.q,module:s.module,layer:s.layer,page:s.page}));
}
function kindExplanation(kind) {
  const descriptions = {
    Class: "This is a vocabulary class. Its subclasses describe more specific kinds of thing.",
    Property: "This property names a relationship or an attribute. Domain and range describe how it is used; they do not establish required fields or counts.",
    Concept: "This is a concept in the business taxonomy. Broader links identify its recorded parent concepts."
  };
  return descriptions[kind] || "Its types and relationships are recorded below.";
}
function termPage(id) {
  const n=nodes.get(id);
  if (!n || !isLocal(n)) return missing("This term is not included in the reference. Choose a module or search for a term.");
  const primary=moduleNames(n).find(m=>data.referenceModules.includes(m));
  const structural=[RDFS+"subClassOf",RDFS+"subPropertyOf",SKOS+"broader",RDFS+"domain",RDFS+"range"];
  const outgoing=n.values.filter(v=>!v.literal && v.p!==RDF+"type").map(v=>({s:id,p:v.p,o:v.v}));
  const back=incoming.get(id)||[];
  const namedBack=[], supportingBack=[];
  for (const row of back) {
    const named=referenceTerms.has(row.s) || !["Metadata",...data.supportingKinds].includes(nodes.get(row.s).kind);
    (named ? namedBack : supportingBack).push(row);
  }
  const neighbours=outgoing.filter(r=>nodes.has(r.o) && !r.o.startsWith("_:") && !data.supportingKinds.includes(nodes.get(r.o).kind));
  const hierarchy=outgoing.filter(r=>structural.includes(r.p));
  return `${crumb([`<a href="${e(moduleLink(primary))}">${e(moduleLabel(primary))}</a>`,`<a href="${e(pageLink(primary,layer(n)))}">${e(layer(n))}</a>`])}
  <div class="term-head"><div><h1>${e(n.label)}</h1><span class="badge">${e(n.kind)}</span><span class="quiet"> ${e(moduleNames(n).join(", "))}</span></div><a href="${e(pageLink(primary))}">Find another term</a></div>
  <div class="term-definition">${definitions(n).length?valuesHtml(definitions(n)):"<p>No definition is recorded.</p>"}</div>
  ${vals(n,SKOS+"scopeNote").length?`<div class="note"><h3>Scope notes</h3>${valuesHtml(vals(n,SKOS+"scopeNote"))}</div>`:""}
  <div class="iri-row"><code id="term-iri">${e(id)}</code><button id="copy-iri">Copy identifier</button><span id="copy-status" role="status"></span></div>
  <section class="section"><h2>Where this term fits</h2><p>${kindExplanation(n.kind)}</p>${hierarchy.length?relationshipTable(hierarchy):"<p class=quiet>No parent, domain or range statement is recorded on this term.</p>"}</section>
  <section class="section"><h2>Follow its connections</h2><p>Arrows show outgoing statements exactly as recorded. The tables list its outgoing relationships. Types appear under all recorded facts.</p>${neighbours.length?smallGraph(n,neighbours.slice(0,6)):""}${neighbours.length>6?"<p class=quiet>The diagram shows the first six named connections. Expand the tables for all connections.</p>":""}${outgoing.length?relationshipList(outgoing):"<p>No outgoing relationship other than its types is recorded.</p>"}</section>
  <section class="section"><h2>What points to this term</h2><p>These incoming statements show how other terms use this term. Expand the list to see every statement.</p>${namedBack.length?relationshipList(namedBack):"<p>No incoming statement from a named term is recorded.</p>"}${supportingBack.length?`<details><summary>Rules and evidence: ${supportingBack.length} incoming statements</summary>${relationshipTable(supportingBack)}</details>`:""}</section>
  <details id="facts"><summary>All recorded facts, types and sources</summary><p>Literal language and datatype are shown when recorded. Anonymous nodes open their own detail. No inferred statements have been added.</p>${facts(n)}</details>
  <div class="actions"><a href="${e(viewerHref(id))}">Open this term in the full viewer</a></div>`;
}
function smallGraph(n,rows) {
  const height=rows.length*76+32, middle=height/2;
  return `<div class="graph"><svg class="wide-graph" viewBox="0 0 900 ${height}" role="img" aria-label="Outgoing connections from ${e(n.label)}. The same statements appear in the table below.">
  <rect x="8" y="${middle-28}" width="240" height="56" rx="8"/><text x="20" y="${middle+5}" font-size="14">${e(n.label.slice(0,27))}</text>
  ${rows.map((r,i)=>{const y=i*76+48;return `<line x1="248" y1="${middle}" x2="615" y2="${y}"/><polygon points="615,${y} 605,${y-5} 605,${y+5}"/><text class="edge-label" x="395" y="${(middle+y)/2-9}">${e(title(r.p).slice(0,29))}</text><a href="${e(termHref(r.o))}"><rect x="620" y="${y-26}" width="265" height="52" rx="8"/><text x="635" y="${y+5}" font-size="14">${e(title(r.o).slice(0,29))}</text><title>${e(title(r.o))}</title></a>`;}).join("")}</svg>
  <svg class="compact-graph" viewBox="0 0 360 ${rows.length*116+90}" role="img" aria-label="Outgoing connections from ${e(n.label)}. The same statements appear in the cards below.">
  <rect x="12" y="8" width="336" height="50" rx="8"/><text x="24" y="38" font-size="14">${e(n.label.slice(0,38))}</text><title>${e(n.label)}</title>
  ${rows.map((r,i)=>{const y=i*116+106;return `<path d="M 36 58 V ${y+26} H 98" fill="none" stroke="currentColor"/><polygon points="100,${y+26} 90,${y+21} 90,${y+31}"/><text class="edge-label" x="100" y="${y-12}">${e(title(r.p).slice(0,29))}</text><a href="${e(termHref(r.o))}"><rect x="100" y="${y}" width="248" height="52" rx="8"/><text x="112" y="${y+31}" font-size="14">${e(title(r.o).slice(0,27))}</text><title>${e(title(r.o))}</title></a>`;}).join("")}</svg></div>`;
}
function facts(n) {
  return `<div class="table-wrap"><table><thead><tr><th scope="col">Property</th><th scope="col">Value</th></tr></thead><tbody>${n.values.map(v=>`<tr><td>${link(v.p)}<br><code>${e(v.p)}</code></td><td>${v.literal?`${e(v.v)} ${v.lang?`<span class="lang">Language: ${e(v.lang)}</span>`:""}${v.datatype?`<br><code>Datatype: ${e(v.datatype)}</code>`:""}`:link(v.v)}</td></tr>`).join("")}</tbody></table></div>`;
}
function guide() {
  const account=data.nodes.find(n=>referenceTerms.has(n.id)&&short(n.id)==="CustomerAccount");
  const partyRole=data.nodes.find(n=>referenceTerms.has(n.id)&&short(n.id)==="PartyRole");
  return `${crumb(["How to use it"])}<h1>Read the ontology with a question in mind</h1><p class="lead">The ontology records shared definitions and connections. Use it to find what a term means and how it relates to the rest of the model.</p>
  <section class="section"><h2>Choose a guided path</h2><ul><li><a href="#process">Process explorer</a>: expand the tree, choose a process and use Go deeper to reach its lowest recorded level.</li><li><a href="#customer">Customer lifecycle</a>: choose a stage, then follow its recorded processes and system stages. These lifecycle stages have no asserted sequence.</li><li><a href="#streams">Value streams</a>: choose Commercial Hydrocarbon Lifecycle or Order to Cash, then follow the ordered stages into their processes and connected concepts.</li></ul><p>Connection cards retain the direction and name of each relationship. Your connection trail keeps the items you followed and distinguishes a value-stream process from its process-map concept. Select an earlier item to return there.</p><p>For a different starting point, <a href="#modules">browse every module</a> or <a href="#browse">find a term</a>. Connections across modules stay in this reference.</p></section>
  <section class="section"><h2>Start with a customer question</h2><ol><li>Open ${account?link(account.id):'<a href="#module=party">the Party module</a>'}. Read its definition and scope notes before following a connection.</li><li>Use <strong>Where this term fits</strong> to inspect its parent, domain or range statements.</li><li>Read a connection from left to right: a term, a named relationship, then another term. Select the destination to continue.</li><li>Open ${partyRole?link(partyRole.id):'<a href="#browse?module=party">another Party term</a>'} and compare its definition. Similar labels do not make two terms equivalent.</li><li>Use <strong>All recorded facts, types and sources</strong> when you need the exact predicate, source reference or datatype.</li></ol></section>
  <section class="section"><h2>Follow a process</h2><ol><li><a href="#browse?module=core&layer=Business+concepts">Find a process in Core</a>.</li><li>Read its definition, then follow its broader concept to see where it sits in the taxonomy.</li><li>Inspect outgoing connections and <strong>What points to this term</strong>. An incoming link may connect a customer lifecycle stage or another module to that process.</li><li><a href="#connections=party">Open Party's connections</a> to see which recorded statements cross module boundaries.</li></ol></section>
  <section class="section"><h2>Distinguish the layers</h2>${layersHtml()}</section>
  <section class="section panel"><h2>Read relationships precisely</h2><p>A subclass is a more specific kind of class. A broader concept is a parent in a concept hierarchy. A property domain or range is a vocabulary statement. A validation shape records a constraint. These relationships have different meanings.</p><p>An arrow does not imply a required field, a process sequence, a causal effect or a live data flow unless the named relationship explicitly says so. This reference adds no inferred relationships.</p><p>Module dependencies identify package versions needed by a module. They are separate from the business connections shown between terms.</p></section>
  <section class="section"><h2>Use an identifier</h2><p>Use <strong>Copy identifier</strong> on a term to copy its IRI, the full identifier used in the RDF. The label helps people read it; the IRI identifies the term when querying or mapping data.</p><p>This site is a reference. To run queries or set up a store, use the existing instructions in this release. Reading these pages needs no connection to a store.</p><ul><li><a href="../business_architecture/ontology/epm-ontology-guide.html">Read the ontology guide</a></li><li><a href="../business_architecture/ontology/epm-walkthrough.html">Follow the walkthrough</a></li><li><a href="../viewer/index.html">Explore the full ontology</a></li></ul></section>`;
}
function about() {
  return `${crumb(["Release and coverage"])}<h1>Release and coverage</h1><p>This reference covers every current ontology module in the source release. It retains their recorded facts, supporting nodes and cross-module relationships. Module pages, search and term links stay within this reference.</p><p>The source is the released ontology at commit <code>${e(data.sourceCommit)}</code>. Package versions are shown on each module. This documentation does not update those packages or their versions.</p><p>Historical packages, example datasets and technical-graph records are outside the input set. Blank nodes and evidence remain reachable through term details.</p><p>To read the reference offline, unzip the whole release and open <code>horoi_viewer/index.html</code>. Keep its location within the release so links to the full viewer and guides work.</p><p><a href="build.json">Build record and input hashes</a> · <a href="NOTICE.txt">Credits and license notes</a></p>`;
}
function missing(message) {return `<h1>Choose a starting point</h1><p>${e(message)}</p><div class="actions"><a href="#overview">Overview</a><a href="#browse">Find a term</a><a href="../viewer/index.html">Full viewer</a></div>`;}
/* EXPLORER_CODE */
function render() {
  const raw=location.hash.slice(1)||"overview";
  const [route,query=""]=raw.split("?",2);
  let html;
  const routeValue = route.includes("=") ? route.slice(route.indexOf("=")+1) : "";
  let decoded;
  try { decoded=decodeURIComponent(routeValue); } catch { decoded=null; }
  if(decoded===null) html=missing("This address contains an invalid identifier. Choose a module or search for the term.");
  else if(route.startsWith("term=")) html=termPage(decoded);
  else if(route.startsWith("module=")) html=modulePage(decoded);
  else if(route.startsWith("connections=")) html=connectionsPage(decoded);
  else if(route==="modules") html=modulesPage();
  else if(route==="browse") html=browsePage(new URLSearchParams(query));
  else if(route==="guide") html=guide();
  else if(route==="about") html=about();
  else if(route==="streams") html=valueStreamsPage();
  else if(isExplorerRoute(route)) html=explorerPage(route,new URLSearchParams(query));
  else if(route==="overview") html=intro();
  else html=missing("This page is not available. Choose a starting point.");
  main.innerHTML=html;
  if(isExplorerRoute(route)) bindExplorer();
  document.querySelectorAll(".masthead nav a").forEach(a=>a.toggleAttribute("aria-current",a.hash.slice(1)===route || (a.hash==="#streams" && Object.hasOwn(streamModes,route))));
  document.querySelectorAll(".masthead nav a[aria-current]").forEach(a=>a.setAttribute("aria-current","page"));
  if(route==="browse") {
    refreshResults();
    document.getElementById("prev").onclick=()=>{browseState.page--;refreshResults();};
    document.getElementById("next").onclick=()=>{browseState.page++;refreshResults();};
    for(const [id,key] of [["search","q"],["module-filter","module"],["layer-filter","layer"]]) document.getElementById(id).addEventListener("input",event=>{
      browseState[key]=event.target.value;browseState.page=0;
      refreshResults();
    });
  }
  const copy=document.getElementById("copy-iri");
  if(copy) copy.onclick=async()=>{
    const iri=document.getElementById("term-iri"),status=document.getElementById("copy-status");
    const text=iri.textContent;
    try { await navigator.clipboard.writeText(text);if(status.isConnected) status.textContent="Copied"; }
    catch {
      if(!iri.isConnected||!status.isConnected) return;
      const r=document.createRange();r.selectNodeContents(iri);getSelection().removeAllRanges();getSelection().addRange(r);
      status.textContent="Identifier selected. Use Copy from your browser.";
    }
  };
  window.scrollTo(0,0);
  main.focus({preventScroll:true});
  if (isExplorerRoute(route) && new URLSearchParams(query).get("at")) {
    const selected=document.getElementById("selected-title");
    if(selected) {
      selected.tabIndex=-1;selected.focus({preventScroll:true});
      if(matchMedia("(max-width:900px)").matches) selected.scrollIntoView({block:"start"});
    }
  }
}
const themeRoot=document.documentElement,systemTheme=matchMedia("(prefers-color-scheme: dark)");
let chosenTheme=null;
function applyTheme(){themeRoot.dataset.theme=chosenTheme||(systemTheme.matches?"dark":"light");}
systemTheme.addEventListener("change",applyTheme);
applyTheme();
document.getElementById("theme").onclick=()=>{chosenTheme=themeRoot.dataset.theme==="dark"?"light":"dark";applyTheme();};
document.querySelector(".skip").onclick=event=>{event.preventDefault();main.focus();main.scrollIntoView();};
window.addEventListener("hashchange",render);
render();
