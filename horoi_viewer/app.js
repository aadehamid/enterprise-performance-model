"use strict";
const data = JSON.parse(document.getElementById("ontology-data").textContent);
const nodes = new Map(data.nodes.map(n => [n.id, n]));
const pilot = new Set(data.pilotTerms);
const RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
const RDFS = "http://www.w3.org/2000/01/rdf-schema#";
const SKOS = "http://www.w3.org/2004/02/skos/core#";
const main = document.getElementById("content");
const incoming = new Map();
for (const n of data.nodes) for (const v of n.values) if (!v.literal) {
  if (!incoming.has(v.v)) incoming.set(v.v, []);
  incoming.get(v.v).push({s:n.id, p:v.p, o:v.v});
}
const e = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c]);
const short = id => id.replace(/[/#]$/, "").split(/[/#]/).pop();
const title = id => nodes.get(id)?.label || short(id);
const moduleNames = n => n.modules.map(m => m.name).filter(m => m !== "Release metadata");
const isLocal = n => n && moduleNames(n).some(m => data.pilotModules.includes(m));
const viewerHref = id => "../viewer/index.html#" + encodeURIComponent(id);
const termHref = id => isLocal(nodes.get(id)) ? "#term=" + encodeURIComponent(id) : viewerHref(id);
const link = id => nodes.has(id)
  ? `<a href="${e(termHref(id))}" title="${e(id)}">${e(title(id))}</a>`
  : `<span title="${e(id)}">${e(title(id))}</span>`;
const vals = (n, p) => n.values.filter(v => v.p === p);
const definitions = n => vals(n, SKOS+"definition").length ? vals(n, SKOS+"definition") : vals(n, RDFS+"comment");
const definition = n => definitions(n).find(v => !v.lang || v.lang === "en")?.v || definitions(n)[0]?.v || "No definition is recorded.";
const layer = n => ["Class","Property"].includes(n.kind) ? "Vocabulary" : data.supportingKinds.includes(n.kind) || n.kind === "Metadata" ? "Rules and evidence" : "Business concepts";
const moduleLabel = m => ({party:"Party · Customer domain",core:"Core · Process map"})[m] || m;
const pageLink = (m, l="") => "#browse?" + new URLSearchParams({module:m, layer:l});
const moduleLink = m => data.pilotModules.includes(m) ? `#module=${encodeURIComponent(m)}` : `../viewer/index.html#view=module:${encodeURIComponent(m)}`;
const moduleInfo = m => data.moduleInfo.find(i => i.name === m);
const valuesHtml = vs => vs.map(v => `<p>${e(v.v)}${v.lang ? `<span class="lang">${e(v.lang)}</span>` : ""}</p>`).join("");
const crumb = trail => `<div class="crumb"><a href="#overview">Overview</a>${trail.map(x=>` / ${x}`).join("")}</div>`;
const browseState = {q:"",module:"",layer:"",page:0};

function intro() {
  return `<div class="eyebrow">MPC Business Process and Architecture Ontology</div>
  <h1>Understand the concepts.<br>Follow their connections.</h1>
  <p class="lead">Start with the customer domain or the process map. Read what a term means, see how it connects to other terms, and follow those links across modules.</p>
  <div class="actions"><a class="primary" href="#module=party">Explore the customer domain</a><a href="#module=core">Explore the process map</a><a href="#guide">Take a guided tour</a></div>
  <div class="grid section">${data.pilotModules.map(m=>moduleTile(m)).join("")}</div>
  <section class="section"><h2>Three ways to read the ontology</h2><p>These are reading groups. They help you distinguish the kinds of information in a module.</p>${layersHtml()}</section>
  <section class="section panel"><h2>How the modules connect</h2><p>Each module describes one part of the business. Recorded relationships connect its terms to terms in other modules. Module dependencies identify the versions it requires.</p><a href="#modules">See the modules and their connections</a></section>
  <p class="quiet section">This reference covers Party and Core. Links to the other modules open the full ontology viewer supplied in this release.</p>`;
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
  if (!info || !data.pilotModules.includes(m)) return missing("This module is available in the full viewer.");
  const candidates = data.nodes.filter(n => pilot.has(n.id) && moduleNames(n).includes(m));
  const featuredNames = m === "party" ? ["Party","CustomerAccount","PartyRole","Person","Organization"] : [];
  const featured = featuredNames.length ? featuredNames.map(s=>candidates.find(n=>short(n.id)===s)).filter(Boolean) : candidates.filter(n=>n.kind==="Concept" && !n.parents.some(p=>pilot.has(p))).slice(0,5);
  return `${crumb([e(moduleLabel(m))])}<div class="eyebrow">${e(m)} · ${e(info.version)}</div><h1>${e(moduleLabel(m))}</h1><p class="lead">${e(info.description)}</p>
  <div class="actions"><a class="primary" href="${e(pageLink(m))}">Browse this module</a><a href="#connections=${e(m)}">Follow connections to other modules</a></div>
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
  <div class="grid">${data.pilotModules.map(moduleTile).join("")}</div>
  <section class="section"><h2>Follow a recorded connection</h2><p>These views show actual statements from the released RDF, grouped by the module at the other end.</p><div class="actions">${data.pilotModules.map(m=>`<a href="#connections=${e(m)}">Connections from ${e(moduleLabel(m))}</a>`).join("")}</div></section>
  <section class="section"><h2>The rest of the ontology</h2><p>Open these modules in the existing full viewer. Their packages are part of the same release.</p><div class="grid">${data.moduleInfo.filter(m=>!data.pilotModules.includes(m.name)).map(m=>moduleTile(m.name)).join("")}</div></section>`;
}
function connectionRows(module) {
  const rows = [];
  for (const n of data.nodes) {
    if (!pilot.has(n.id) || !moduleNames(n).includes(module)) continue;
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
  if (!data.pilotModules.includes(module)) return missing("Choose Party or Core to inspect its outgoing connections.");
  const rows = connectionRows(module);
  const groups = [...new Set(rows.map(r=>r.module))];
  return `${crumb([`<a href="${e(moduleLink(module))}">${e(moduleLabel(module))}</a>`,"Connections"])}<h1>Connections from ${e(moduleLabel(module))}</h1>
  <p class="lead">Read each row as a statement: the first term has the named relationship to the second term. Links outside the pilot open the full viewer.</p>
  <p class="note">This view shows outgoing statements to named terms in other modules. It excludes evidence and package metadata. A property domain or range describes vocabulary; it does not assert a relationship between individual records.</p>
  ${groups.length ? groups.map(m=>`<section class="section"><h2>To ${e(moduleLabel(m))}</h2>${relationshipTable(rows.filter(r=>r.module===m))}</section>`).join("") : '<p class="empty">No outgoing connection to another module is recorded for the terms in this view. Incoming links remain visible on each term.</p>'}`;
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
  browseState.q=params.get("q")||""; browseState.module=params.get("module")||""; browseState.layer=params.get("layer")||""; browseState.page=0;
  return `${crumb(["Find a term"])}<h1>Find a term</h1><p>Search labels, definitions and identifiers. Filter by module or reading group to narrow the result.</p>
  <div class="filters"><label class="search">Search terms<input id="search" type="search" placeholder="Try customer account or a process name" value="${e(browseState.q)}"></label>
  <label>Module<select id="module-filter"><option value="">Party and Core</option>${data.pilotModules.map(m=>`<option value="${e(m)}" ${m===browseState.module?"selected":""}>${e(moduleLabel(m))}</option>`).join("")}</select></label>
  <label>Reading group<select id="layer-filter"><option value="">All groups</option>${["Business concepts","Vocabulary","Rules and evidence"].map(l=>`<option ${l===browseState.layer?"selected":""}>${e(l)}</option>`).join("")}</select></label></div>
  <p id="result-count" role="status" class="quiet"></p><ul class="results" id="results"></ul><div id="pager" class="pager"></div>`;
}
function refreshResults() {
  const s=browseState;
  const found=data.nodes.filter(n=>isLocal(n) && (s.layer==="Rules and evidence" ? layer(n)===s.layer : pilot.has(n.id))
    && (!s.module||moduleNames(n).includes(s.module)) && (!s.layer||layer(n)===s.layer)
    && (n.label+" "+n.id+" "+definition(n)).toLowerCase().includes(s.q.toLowerCase())).sort((a,b)=>a.label.localeCompare(b.label)||a.id.localeCompare(b.id));
  const start=s.page*40;
  document.getElementById("result-count").textContent=found.length ? `${found.length} results. Showing ${start+1} to ${Math.min(start+40,found.length)}.` : "No matching terms. Try a shorter name or clear the filters.";
  document.getElementById("results").innerHTML=found.slice(start,start+40).map(n=>`<li>${link(n.id)}<span class="badge">${e(n.kind)}</span><p>${e(moduleNames(n).join(", "))} · ${e(definition(n))}</p></li>`).join("");
  document.getElementById("pager").innerHTML=`<button id="prev" ${!s.page?"disabled":""}>Previous</button><button id="next" ${start+40>=found.length?"disabled":""}>Next</button>`;
  document.getElementById("prev").onclick=()=>{s.page--;refreshResults();};
  document.getElementById("next").onclick=()=>{s.page++;refreshResults();};
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
  if (!n || !isLocal(n)) return missing("This term is outside the Party/Core reference. Open the full viewer to inspect the release.");
  const primary=moduleNames(n).find(m=>data.pilotModules.includes(m));
  const structural=[RDFS+"subClassOf",RDFS+"subPropertyOf",SKOS+"broader",RDFS+"domain",RDFS+"range"];
  const outgoing=n.values.filter(v=>!v.literal && v.p!==RDF+"type").map(v=>({s:id,p:v.p,o:v.v}));
  const back=incoming.get(id)||[];
  const namedBack=[], supportingBack=[];
  for (const row of back) {
    const named=pilot.has(row.s) || !["Metadata",...data.supportingKinds].includes(nodes.get(row.s).kind);
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
  return `<div class="graph"><svg viewBox="0 0 900 ${height}" role="img" aria-label="Outgoing connections from ${e(n.label)}. The same statements appear in the table below.">
  <rect x="8" y="${middle-28}" width="240" height="56" rx="8"/><text x="20" y="${middle+5}" font-size="14">${e(n.label.slice(0,27))}</text>
  ${rows.map((r,i)=>{const y=i*76+48;return `<line x1="248" y1="${middle}" x2="615" y2="${y}"/><polygon points="615,${y} 605,${y-5} 605,${y+5}"/><text class="edge-label" x="395" y="${(middle+y)/2-9}">${e(title(r.p).slice(0,29))}</text><a href="${e(termHref(r.o))}"><rect x="620" y="${y-26}" width="265" height="52" rx="8"/><text x="635" y="${y+5}" font-size="14">${e(title(r.o).slice(0,29))}</text><title>${e(title(r.o))}</title></a>`;}).join("")}</svg></div>`;
}
function facts(n) {
  return `<div class="table-wrap"><table><thead><tr><th scope="col">Property</th><th scope="col">Value</th></tr></thead><tbody>${n.values.map(v=>`<tr><td>${link(v.p)}<br><code>${e(v.p)}</code></td><td>${v.literal?`${e(v.v)} ${v.lang?`<span class="lang">Language: ${e(v.lang)}</span>`:""}${v.datatype?`<br><code>Datatype: ${e(v.datatype)}</code>`:""}`:link(v.v)}</td></tr>`).join("")}</tbody></table></div>`;
}
function guide() {
  const account=data.nodes.find(n=>pilot.has(n.id)&&short(n.id)==="CustomerAccount");
  const partyRole=data.nodes.find(n=>pilot.has(n.id)&&short(n.id)==="PartyRole");
  return `${crumb(["How to use it"])}<h1>Read the ontology with a question in mind</h1><p class="lead">The ontology records shared definitions and connections. Use it to find what a term means and how it relates to the rest of the model.</p>
  <section class="section"><h2>Start with a customer question</h2><ol><li>Open ${account?link(account.id):'<a href="#module=party">the Party module</a>'}. Read its definition and scope notes before following a connection.</li><li>Use <strong>Where this term fits</strong> to inspect its parent, domain or range statements.</li><li>Read a connection from left to right: a term, a named relationship, then another term. Select the destination to continue.</li><li>Open ${partyRole?link(partyRole.id):'<a href="#browse?module=party">another Party term</a>'} and compare its definition. Similar labels do not make two terms equivalent.</li><li>Use <strong>All recorded facts, types and sources</strong> when you need the exact predicate, source reference or datatype.</li></ol></section>
  <section class="section"><h2>Follow a process</h2><ol><li><a href="#browse?module=core&layer=Business+concepts">Find a process in Core</a>.</li><li>Read its definition, then follow its broader concept to see where it sits in the taxonomy.</li><li>Inspect outgoing connections and <strong>What points to this term</strong>. An incoming link may connect a customer lifecycle stage or another module to that process.</li><li><a href="#connections=party">Open Party's connections</a> to see which recorded statements cross module boundaries.</li></ol></section>
  <section class="section"><h2>Distinguish the layers</h2>${layersHtml()}</section>
  <section class="section panel"><h2>Read relationships precisely</h2><p>A subclass is a more specific kind of class. A broader concept is a parent in a concept hierarchy. A property domain or range is a vocabulary statement. A validation shape records a constraint. These relationships have different meanings.</p><p>An arrow does not imply a required field, a process sequence, a causal effect or a live data flow unless the named relationship explicitly says so. This reference adds no inferred relationships.</p><p>Module dependencies identify package versions needed by a module. They are separate from the business connections shown between terms.</p></section>
  <section class="section"><h2>Use an identifier</h2><p>Use <strong>Copy identifier</strong> on a term to copy its IRI, the full identifier used in the RDF. The label helps people read it; the IRI identifies the term when querying or mapping data.</p><p>This site is a reference. To run queries or set up a store, use the existing instructions in this release. Reading these pages needs no connection to a store.</p><ul><li><a href="../business_architecture/ontology/epm-ontology-guide.html">Read the ontology guide</a></li><li><a href="../business_architecture/ontology/epm-walkthrough.html">Follow the walkthrough</a></li><li><a href="../viewer/index.html">Explore the full ontology</a></li></ul></section>`;
}
function about() {
  return `${crumb(["Release and coverage"])}<h1>Release and coverage</h1><p>This pilot provides term navigation for Party and Core. It retains their recorded facts and the context needed to explain relationships. Other modules open in the full viewer.</p><p>The source is the released ontology at commit <code>${e(data.sourceCommit)}</code>. Package versions are shown on each module. This documentation does not update those packages or their versions.</p><p>Historical packages, example datasets and technical-graph records are outside the input set. Blank nodes and evidence remain reachable through term details.</p><p>To read the reference offline, unzip the whole release and open <code>horoi_viewer/index.html</code>. Keep its location within the release so links to the full viewer and guides work.</p><p><a href="build.json">Build record and input hashes</a> · <a href="NOTICE.txt">Credits and license notes</a></p>`;
}
function missing(message) {return `<h1>Choose a starting point</h1><p>${e(message)}</p><div class="actions"><a href="#overview">Overview</a><a href="#browse">Find a term</a><a href="../viewer/index.html">Full viewer</a></div>`;}
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
  else html=intro();
  main.innerHTML=html;
  document.querySelectorAll(".masthead nav a").forEach(a=>a.toggleAttribute("aria-current",a.hash.slice(1)===route));
  document.querySelectorAll(".masthead nav a[aria-current]").forEach(a=>a.setAttribute("aria-current","page"));
  if(route==="browse") {
    refreshResults();
    for(const [id,key] of [["search","q"],["module-filter","module"],["layer-filter","layer"]]) document.getElementById(id).addEventListener("input",event=>{
      browseState[key]=event.target.value;browseState.page=0;
      history.replaceState(null,"","#browse?"+new URLSearchParams({q:browseState.q,module:browseState.module,layer:browseState.layer}));refreshResults();
    });
  }
  const copy=document.getElementById("copy-iri");
  if(copy) copy.onclick=async()=>{
    const text=document.getElementById("term-iri").textContent;
    try { await navigator.clipboard.writeText(text);document.getElementById("copy-status").textContent="Copied"; }
    catch { const r=document.createRange();r.selectNodeContents(document.getElementById("term-iri"));getSelection().removeAllRanges();getSelection().addRange(r);document.getElementById("copy-status").textContent="Identifier selected. Use Copy from your browser."; }
  };
  window.scrollTo(0,0);
  main.focus({preventScroll:true});
}
document.getElementById("theme").onclick=()=>{document.documentElement.dataset.theme=document.documentElement.dataset.theme==="dark"?"light":"dark";};
document.querySelector(".skip").onclick=event=>{event.preventDefault();main.focus();main.scrollIntoView();};
window.addEventListener("hashchange",render);
render();
