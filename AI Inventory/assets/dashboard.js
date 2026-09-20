"use strict";

const REPOSITORY = "AtriManthani/AI-Center-Of-Excellence";
const BRANCH = "main";
const DATA_URL = `data/use-cases.json?v=${Date.now()}`;
const TREE_API = `https://api.github.com/repos/${REPOSITORY}/git/trees/${BRANCH}?recursive=1`;
const RECORD_PREFIX = "AI Inventory/use-cases/";
const PHASES = [
  "Intake",
  "Qualify",
  "Prioritize",
  "Design",
  "Develop",
  "Test",
  "Deploy",
  "Monitor",
  "Close"
];
const PHASE_FOLDERS = {
  Intake:"01 Intake", Qualify:"02 Qualify", Prioritize:"03 Prioritize",
  Design:"04 Design", Develop:"05 Develop", Test:"06 Test",
  Deploy:"07 Deploy", Monitor:"08 Monitor", Close:"09 Close"
};
const STATUSES = ["In Progress", "Backlog", "Live", "On Hold", "Closed"];
const state = {data:null, view:"overview", slide:0};
const byId = id => document.getElementById(id);
const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, character => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[character]));
const normal = value => String(value || "").trim().toLowerCase();
const empty = message => `<div class="empty-state"><strong>No records to display</strong>${escapeHtml(message)}</div>`;
const formatDate = value => {
  if(!value) return "Not scheduled";
  const date = new Date(`${value}`.length === 10 ? `${value}T12:00:00` : value);
  return Number.isNaN(date.valueOf()) ? escapeHtml(value) : date.toLocaleDateString(undefined,{month:"short",day:"numeric",year:"numeric"});
};
const statusCount = status => state.data.useCases.filter(item => item.status === status).length;

function publicRecord(record){
  const checklist=record.checklist||{};
  const done=Number(checklist.done||0),total=Number(checklist.total||0);
  const gateReadiness=total?Math.round(done/total*100):Number(record.gateReadiness||0);
  const encodedPath=String(record._folderPath||"").split("/").map(encodeURIComponent).join("/");
  const folderUrl=encodedPath?`https://github.com/${REPOSITORY}/tree/${BRANCH}/${encodedPath}`:null;
  const phaseFolder=PHASE_FOLDERS[record.phase];
  const phaseFolderUrl=folderUrl&&phaseFolder?`${folderUrl}/${encodeURIComponent(phaseFolder)}`:folderUrl;
  return {
    id:record.id,name:record.name,department:record.department,owner:record.owner,
    phase:record.phase,status:record.status,
    gateReadiness,checklistDone:done,checklistTotal:total,
    reviewStatus:record.reviewStatus||"Not Started",currentActivity:record.currentActivity,
    blocker:record.blocker,nextDecision:record.nextDecision,
    nextDecisionDate:record.nextDecisionDate,lastUpdated:record.lastUpdated,
    summary:record.summary,closureReason:record.closureReason,folderUrl,phaseFolderUrl,
    issues:(record.issues||[]).filter(issue=>issue.publish).map(issue=>({
      id:issue.id,title:issue.title,severity:issue.severity,status:issue.status,
      owner:issue.owner,targetDate:issue.targetDate,resolvedDate:issue.resolvedDate,
      mitigationSummary:issue.mitigationSummary
    }))
  };
}

function checklistProgress(markdown){
  const items=[...String(markdown||"").matchAll(/^\s*-\s*\[([ xX])\]/gm)];
  return {done:items.filter(item=>normal(item[1])==="x").length,total:items.length};
}

async function discoverInventory(){
  const response=await fetch(TREE_API,{headers:{Accept:"application/vnd.github+json"},cache:"no-store"});
  if(!response.ok) throw new Error(`GitHub inventory discovery failed (${response.status}).`);
  const tree=await response.json();
  const paths=(tree.tree||[]).map(item=>item.path).filter(path=>path.startsWith(RECORD_PREFIX)&&path.endsWith("/status.json")&&!path.includes("/_template/"));
  const records=await Promise.all(paths.map(async path=>{
    const url=`https://raw.githubusercontent.com/${REPOSITORY}/${BRANCH}/${path.split("/").map(encodeURIComponent).join("/")}?v=${Date.now()}`;
    const recordResponse=await fetch(url,{cache:"no-store"});
    if(!recordResponse.ok) throw new Error(`Could not read ${path}.`);
    const record=await recordResponse.json();
    record._folderPath=path.slice(0,-"/status.json".length);
    const phaseFolder=PHASE_FOLDERS[record.phase];
    if(phaseFolder){
      const checklistPath=`${record._folderPath}/${phaseFolder}/CHECKLIST.md`;
      const checklistUrl=`https://raw.githubusercontent.com/${REPOSITORY}/${BRANCH}/${checklistPath.split("/").map(encodeURIComponent).join("/")}?v=${Date.now()}`;
      const checklistResponse=await fetch(checklistUrl,{cache:"no-store"});
      if(checklistResponse.ok) record.checklist=checklistProgress(await checklistResponse.text());
    }
    return record;
  }));
  const useCases=records.filter(record=>record.publish).map(publicRecord).sort((a,b)=>String(a.id).localeCompare(String(b.id)));
  const latest=useCases.map(item=>item.lastUpdated).filter(Boolean).sort().at(-1)||null;
  return {schemaVersion:1,generatedAt:latest,source:"AI CoE public governance workspace",useCases};
}

async function fallbackInventory(){
  const response=await fetch(DATA_URL,{cache:"no-store"});
  if(!response.ok) throw new Error(`Inventory fallback request failed (${response.status}).`);
  return response.json();
}

function card(item){
  const blocker = item.blocker ? `<div class="detail"><strong>Blocker:</strong> ${escapeHtml(item.blocker)}</div>` : "";
  const closure = item.status === "Closed" ? `<div class="detail"><strong>Closure reason:</strong> ${escapeHtml(item.closureReason || "Not recorded")}</div>` : "";
  const checklist=item.checklistTotal?`${item.checklistDone} of ${item.checklistTotal} checks`:`${item.gateReadiness}% complete`;
  const actions=item.folderUrl?`<div class="card-actions"><a href="${item.folderUrl}" target="_blank" rel="noopener">Open Files</a><a href="${item.phaseFolderUrl}/CHECKLIST.md" target="_blank" rel="noopener">Open Checklist</a></div>`:"";
  return `<article class="use-case-card">
    <div class="card-top"><div><div class="use-case-id">${escapeHtml(item.id)}</div><h3>${escapeHtml(item.name)}</h3></div><span class="badge">${escapeHtml(item.phase)}</span></div>
    <div class="card-meta">${escapeHtml(item.department || "Department not set")} · ${escapeHtml(item.status)} · Review: ${escapeHtml(item.reviewStatus)}</div>
    <div class="card-latest"><strong>Latest update</strong>${escapeHtml(item.currentActivity || "No update recorded")}${blocker}${closure}</div>
    <div class="card-footer"><span>${escapeHtml(item.owner || "Owner not set")}</span><span class="readiness">${escapeHtml(checklist)}</span></div>${actions}
  </article>`;
}

function issue(item, parent){
  const mitigation = item.mitigationSummary ? `<div class="mitigation"><strong>Mitigation:</strong> ${escapeHtml(item.mitigationSummary)}</div>` : "";
  return `<div class="issue-item"><div><div class="issue-parent">${escapeHtml(parent.id)} · ${escapeHtml(parent.name)}</div><strong>${escapeHtml(item.title)}</strong><div class="detail">Owner: ${escapeHtml(item.owner || "Not assigned")} · ${item.status === "Resolved" ? `Resolved ${formatDate(item.resolvedDate)}` : `Target ${formatDate(item.targetDate)}`}</div>${mitigation}</div><span class="badge ${normal(item.severity)}">${escapeHtml(item.severity)}</span></div>`;
}

function renderOverview(){
  const items = state.data.useCases;
  byId("recordCount").textContent = `${items.length} use case${items.length === 1 ? "" : "s"}`;
  const values = [
    ["Total use cases",items.length,"Current approved inventory"],
    ["In progress",statusCount("In Progress"),"Moving through governance"],
    ["Backlog",statusCount("Backlog"),"Qualified and waiting"],
    ["Live",statusCount("Live"),"Operating in production"],
    ["On hold",statusCount("On Hold"),"Temporarily paused"]
  ];
  byId("kpiGrid").innerHTML = values.map(([label,value,note]) => `<div class="kpi"><div class="kpi-label">${label}</div><div class="kpi-value">${value}</div><div class="kpi-note">${note}</div></div>`).join("");
  const updates=[...items].sort((a,b)=>String(b.lastUpdated||"").localeCompare(String(a.lastUpdated||"")));
  byId("latestUpdates").innerHTML = updates.length ? updates.slice(0,8).map(item => `<div class="update-item"><span class="badge">${escapeHtml(item.status)}</span><div><strong>${escapeHtml(item.name)}</strong><div class="detail">${escapeHtml(item.currentActivity || "No current activity recorded")}${item.blocker ? ` · Blocker: ${escapeHtml(item.blocker)}` : ""}</div></div><span class="date">${escapeHtml(item.phase)}</span></div>`).join("") : empty("No use-case updates have been published.");
  const decisions = items.filter(item => item.nextDecision || item.nextDecisionDate).sort((a,b) => String(a.nextDecisionDate || "9999").localeCompare(String(b.nextDecisionDate || "9999")));
  byId("decisionList").innerHTML = decisions.length ? decisions.slice(0,10).map(item => `<div class="decision-item"><span class="date">${formatDate(item.nextDecisionDate)}</span><div><strong>${escapeHtml(item.nextDecision || "Decision not described")}</strong><div class="detail">${escapeHtml(item.id)} · ${escapeHtml(item.name)} · ${escapeHtml(item.phase)}</div></div><span class="badge neutral">${escapeHtml(item.status)}</span></div>`).join("") : empty("No upcoming decisions have been published.");
}

function populateFilters(){
  const definitions = [
    ["statusFilter",STATUSES],
    ["departmentFilter",[...new Set(state.data.useCases.map(item => item.department).filter(Boolean))].sort()]
  ];
  definitions.forEach(([id,values]) => {const element=byId(id);while(element.options.length>1) element.remove(1);values.forEach(value=>element.add(new Option(value,value)));});
}

function renderPipeline(){
  const query=normal(byId("searchFilter").value),status=byId("statusFilter").value,department=byId("departmentFilter").value;
  const matches=state.data.useCases.filter(item => (!query || [item.id,item.name,item.department,item.owner,item.currentActivity].some(value=>normal(value).includes(query))) && (!status || item.status===status) && (!department || item.department===department));
  byId("pipelineBoard").innerHTML = PHASES.map(phase => {const phaseItems=matches.filter(item=>item.phase===phase);return `<section class="phase-column"><h3 class="phase-title">${escapeHtml(phase)}<span>${phaseItems.length}</span></h3><div class="phase-cards">${phaseItems.length?phaseItems.map(card).join(""):`<div class="detail">No use cases</div>`}</div></section>`;}).join("");
}

function renderOperationalViews(){
  const live=state.data.useCases.filter(item=>item.status==="Live");
  byId("productionGrid").innerHTML=live.length?live.map(card).join(""):empty("No live use cases have been published.");
  const closed=state.data.useCases.filter(item=>item.status==="Closed");
  byId("closedGrid").innerHTML=closed.length?closed.map(card).join(""):empty("No closed use cases have been published.");
  const joined=state.data.useCases.flatMap(parent=>(parent.issues||[]).map(record=>({record,parent})));
  const open=joined.filter(({record})=>record.status!=="Resolved");
  const resolved=joined.filter(({record})=>record.status==="Resolved");
  byId("openIssues").innerHTML=open.length?open.map(({record,parent})=>issue(record,parent)).join(""):empty("No open production issues.");
  byId("resolvedIssues").innerHTML=resolved.length?resolved.map(({record,parent})=>issue(record,parent)).join(""):empty("No resolved issues have been published.");
}

function selectView(view){
  state.view=view;state.slide=0;
  document.querySelectorAll(".view").forEach(element=>element.classList.toggle("active",element.id===view));
  document.querySelectorAll(".tabs button").forEach(element=>element.classList.toggle("active",element.dataset.view===view));
  updatePresentation();
}
function slides(){return [...document.querySelectorAll(`#${state.view} .slide`)];}
function updatePresentation(){const list=slides();state.slide=Math.max(0,Math.min(state.slide,Math.max(0,list.length-1)));list.forEach((element,index)=>element.classList.toggle("present-active",index===state.slide));byId("slidePosition").textContent=`${state.slide+1} / ${Math.max(1,list.length)}`;}
function togglePresentation(force){const enabled=force??!document.body.classList.contains("presentation-mode");document.body.classList.toggle("presentation-mode",enabled);byId("presentButton").textContent=enabled?"Exit":"Present";state.slide=0;updatePresentation();if(enabled&&document.documentElement.requestFullscreen)document.documentElement.requestFullscreen().catch(()=>{});if(!enabled&&document.fullscreenElement)document.exitFullscreen().catch(()=>{});}

async function load(){
  try{
    let data;
    try{data=await discoverInventory();}
    catch(discoveryError){console.warn(discoveryError.message);data=await fallbackInventory();}
    if(!Array.isArray(data.useCases)) throw new Error("Inventory data is not in the expected format.");
    state.data=data;
    byId("freshness").textContent=data.generatedAt?`Published ${formatDate(data.generatedAt)}`:"Awaiting first approved inventory publication";
    renderOverview();populateFilters();renderPipeline();renderOperationalViews();
    byId("loading").classList.add("hidden");
  }catch(error){
    byId("loading").innerHTML=`<div class="empty-state"><strong>The AI Inventory could not load</strong>${escapeHtml(error.message)}</div>`;
    console.error(error);
  }
}

document.querySelectorAll(".tabs button").forEach(button=>button.addEventListener("click",()=>selectView(button.dataset.view)));
["searchFilter","statusFilter","departmentFilter"].forEach(id=>byId(id).addEventListener(id==="searchFilter"?"input":"change",renderPipeline));
byId("printButton").addEventListener("click",()=>window.print());
byId("presentButton").addEventListener("click",()=>togglePresentation());
byId("exitPresentation").addEventListener("click",()=>togglePresentation(false));
byId("previousSlide").addEventListener("click",()=>{state.slide--;updatePresentation();});
byId("nextSlide").addEventListener("click",()=>{state.slide++;updatePresentation();});
document.addEventListener("keydown",event=>{if(!document.body.classList.contains("presentation-mode"))return;if(["ArrowRight","PageDown"," "].includes(event.key)){event.preventDefault();state.slide++;updatePresentation();}if(["ArrowLeft","PageUp"].includes(event.key)){event.preventDefault();state.slide--;updatePresentation();}if(event.key==="Escape")togglePresentation(false);});
load();
