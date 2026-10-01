"use strict";

const REPOSITORY = "AtriManthani/AI-Center-Of-Excellence";
const BRANCH = "main";
const DATA_URL = `data/use-cases.json?v=${Date.now()}`;
const CATALOG_URL = `governance/controls.json?v=${Date.now()}`;
const TREE_API = `https://api.github.com/repos/${REPOSITORY}/git/trees/${BRANCH}?recursive=1`;
const RECORD_PREFIX = "AI Inventory/use-cases/";
const PHASES = ["Intake", "Qualify", "Prioritize", "Design", "Develop", "Test", "Deploy", "Monitor", "Close"];
const PHASE_FOLDERS = {
  Intake:"01 Intake", Qualify:"02 Qualify", Prioritize:"03 Prioritize",
  Design:"04 Design", Develop:"05 Develop", Test:"06 Test",
  Deploy:"07 Deploy", Monitor:"08 Monitor", Close:"09 Close"
};
const STATUSES = ["In Progress", "Backlog", "Live", "On Hold", "Closed"];
const VIEWS = ["overview", "pipeline", "reviews", "risks", "production", "issues", "closed"];
const REVIEW_GROUPS = ["Cyber", "Data", "Application", "Network", "Enterprise"];
const COMPLETE_REQUIREMENT_STATUSES = new Set(["Complete", "Not Applicable"]);
const COMPLETE_REVIEW_STATUSES = new Set(["Approved", "Approved with Conditions", "Not Required"]);
const state = {data:null, catalog:null, view:"overview", slide:0};
const byId = id => document.getElementById(id);
const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, character => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[character]));
const normal = value => String(value || "").trim().toLowerCase();
const empty = message => `<div class="empty-state"><strong>No records to display</strong>${escapeHtml(message)}</div>`;
const today = () => {const value=new Date();value.setHours(0,0,0,0);return value;};
const parseDate = value => {if(!value)return null;const result=new Date(`${value}`.length===10?`${value}T12:00:00`:value);return Number.isNaN(result.valueOf())?null:result;};
const formatDate = value => {const date=parseDate(value);return date?date.toLocaleDateString(undefined,{month:"short",day:"numeric",year:"numeric"}):value?escapeHtml(value):"Not scheduled";};
const statusCount = status => state.data.useCases.filter(item => item.status === status).length;
const badgeClass = value => normal(value).replace(/[^a-z0-9]+/g,"-");
const isOverdue = (date,status) => {const parsed=parseDate(date);return !!parsed&&parsed<today()&&!COMPLETE_REQUIREMENT_STATUSES.has(status)&&!COMPLETE_REVIEW_STATUSES.has(status);};
const phaseCatalog = name => (state.catalog?.phases||[]).find(item=>item.name===name)||{name,playbookPhase:name,controls:[]};

function enrichedPhases(record){
  if(Array.isArray(record.phases)&&record.phases.length) return record.phases;
  const governance=record.governance||{};
  const progress=new Map((governance.phaseProgress||[]).map(item=>[item.phase,item]));
  return (state.catalog?.phases||[]).map(catalogPhase=>{
    const item=progress.get(catalogPhase.name)||{};
    const overrides=item.requirements||{};
    const requirements=(catalogPhase.controls||[]).map(control=>{
      const override=overrides[control.id]||{};
      return {...control,status:override.status||"Not Started",ownerGroup:override.ownerGroup||"",targetDate:override.targetDate||null,completedDate:override.completedDate||null,evidence:override.evidence||[],notes:override.notes||""};
    });
    const required=requirements.filter(requirement=>requirement.required);
    const done=required.filter(requirement=>COMPLETE_REQUIREMENT_STATUSES.has(requirement.status)).length;
    return {phase:catalogPhase.name,playbookPhase:catalogPhase.playbookPhase,status:item.status||"Not Started",startedDate:item.startedDate||null,targetDate:item.targetDate||null,completedDate:item.completedDate||null,gate:item.gate||{status:"Not Started"},requirements,done,total:required.length,readiness:required.length?Math.round(done/required.length*100):0};
  });
}

function publicRecord(record){
  const phases=enrichedPhases(record);
  const current=phases.find(item=>item.phase===record.phase)||{};
  const governance=record.governance||{};
  const folderPath=record._folderPath||record.folderPath||"";
  const encodedPath=String(folderPath).split("/").map(encodeURIComponent).join("/");
  const folderUrl=encodedPath?`https://github.com/${REPOSITORY}/tree/${BRANCH}/${encodedPath}`:null;
  const phaseFolder=PHASE_FOLDERS[record.phase];
  const phaseFolderUrl=folderUrl&&phaseFolder?`${folderUrl}/${encodeURIComponent(phaseFolder)}`:folderUrl;
  return {
    id:record.id,name:record.name,department:record.department,owner:record.owner,sponsor:record.sponsor,
    phase:record.phase,status:record.status,health:record.health||"Needs Review",riskTier:record.riskTier||"Not Assessed",
    gateReadiness:Number(current.readiness??record.gateReadiness??0),checklistDone:Number(current.done??record.checklistDone??0),checklistTotal:Number(current.total??record.checklistTotal??0),
    reviewStatus:record.reviewStatus||"Not Started",currentStep:record.currentStep||record.currentActivity,currentActivity:record.currentActivity,
    blocker:record.blocker,phaseEnteredDate:record.phaseEnteredDate,targetPhaseExitDate:record.targetPhaseExitDate,
    nextDecision:record.nextDecision,nextDecisionDate:record.nextDecisionDate,lastUpdated:record.lastUpdated,
    summary:record.summary,benefits:record.benefits||{},closureReason:record.closureReason,folderUrl,phaseFolderUrl,
    phases,formalReviews:record.formalReviews||governance.formalReviews||[],technicalRisks:record.technicalRisks||governance.technicalRisks||[],
    decisions:record.decisions||governance.decisions||[],monitoring:record.monitoring||governance.monitoring||{},
    issues:(record.issues||[]).filter(issue=>issue.publish!==false).map(issue=>({id:issue.id,title:issue.title,severity:issue.severity,status:issue.status,owner:issue.owner,targetDate:issue.targetDate,resolvedDate:issue.resolvedDate,mitigationSummary:issue.mitigationSummary}))
  };
}

async function fetchJson(url,label){
  const response=await fetch(url,{cache:"no-store"});
  if(!response.ok) throw new Error(`${label} request failed (${response.status}).`);
  return response.json();
}

async function discoverInventory(){
  const response=await fetch(TREE_API,{headers:{Accept:"application/vnd.github+json"},cache:"no-store"});
  if(!response.ok) throw new Error(`GitHub inventory discovery failed (${response.status}).`);
  const tree=await response.json();
  const paths=(tree.tree||[]).map(item=>item.path).filter(path=>path.startsWith(RECORD_PREFIX)&&path.endsWith("/status.json")&&!path.includes("/_template/"));
  const records=await Promise.all(paths.map(async path=>{
    const rawUrl=relative=>`https://raw.githubusercontent.com/${REPOSITORY}/${BRANCH}/${relative.split("/").map(encodeURIComponent).join("/")}?v=${Date.now()}`;
    const record=await fetchJson(rawUrl(path),path);
    record._folderPath=path.slice(0,-"/status.json".length);
    const governancePath=`${record._folderPath}/governance.json`;
    try{record.governance=await fetchJson(rawUrl(governancePath),governancePath);}catch(error){console.warn(error.message);record.governance={};}
    return record;
  }));
  const published=records.filter(record=>record.publish).map(publicRecord);
  const latest=published.map(item=>item.lastUpdated).filter(Boolean).sort().at(-1)||null;
  return {schemaVersion:2,generatedAt:latest,source:"AI CoE public governance workspace",useCases:published.sort((a,b)=>String(a.id).localeCompare(String(b.id)))};
}

async function fallbackInventory(){
  const data=await fetchJson(DATA_URL,"Inventory fallback");
  data.useCases=(data.useCases||[]).map(publicRecord);
  return data;
}

function phaseAge(item){
  const entered=parseDate(item.phaseEnteredDate);
  if(!entered)return "Phase start not recorded";
  const days=Math.max(0,Math.floor((today()-entered)/86400000));
  return `${days} day${days===1?"":"s"} in phase`;
}

function pendingReviews(item){
  return (item.formalReviews||[]).filter(review=>review.applicability==="Required"&&!COMPLETE_REVIEW_STATUSES.has(review.status));
}

function activeTechnicalRisks(item){
  return (item.technicalRisks||[]).filter(risk=>risk.status!=="Closed");
}

function overdueActions(item){
  const requirements=(item.phases||[]).flatMap(phase=>phase.requirements||[]).filter(requirement=>isOverdue(requirement.targetDate,requirement.status));
  const risks=activeTechnicalRisks(item).filter(risk=>isOverdue(risk.targetDate,risk.status));
  return requirements.length+risks.length;
}

function card(item){
  const blocker=item.blocker?`<div class="detail blocker"><strong>Blocker:</strong> ${escapeHtml(item.blocker)}</div>`:"";
  const closure=item.status==="Closed"?`<div class="detail"><strong>Closure reason:</strong> ${escapeHtml(item.closureReason||"Not recorded")}</div>`:"";
  const reviews=pendingReviews(item).length;
  const risks=activeTechnicalRisks(item).filter(risk=>["High","Critical"].includes(risk.residualRisk)).length;
  const actions=`<div class="card-actions"><button class="link-button detail-button" data-case-id="${escapeHtml(item.id)}" type="button">View Governance</button>${item.folderUrl?`<a href="${item.folderUrl}" target="_blank" rel="noopener">Open Files</a><a href="${item.phaseFolderUrl}/CHECKLIST.md" target="_blank" rel="noopener">Open Checklist</a>`:""}</div>`;
  return `<article class="use-case-card">
    <div class="card-top"><div><div class="use-case-id">${escapeHtml(item.id)}</div><h3>${escapeHtml(item.name)}</h3></div><span class="badge ${badgeClass(item.health)}">${escapeHtml(item.health)}</span></div>
    <div class="card-meta">${escapeHtml(item.department||"Department not set")} &middot; ${escapeHtml(item.status)} &middot; ${escapeHtml(item.phase)}</div>
    <div class="card-latest"><strong>Current step</strong>${escapeHtml(item.currentStep||"No current step recorded")}${blocker}${closure}</div>
    <div class="mini-grid"><span><strong>${item.gateReadiness}%</strong> gate controls</span><span><strong>${reviews}</strong> pending reviews</span><span><strong>${risks}</strong> high risks</span></div>
    <div class="card-footer"><span>${escapeHtml(item.owner||"Owner not set")}</span><span>${escapeHtml(phaseAge(item))}</span></div>${actions}
  </article>`;
}

function issue(item,parent){
  const mitigation=item.mitigationSummary?`<div class="mitigation"><strong>Mitigation:</strong> ${escapeHtml(item.mitigationSummary)}</div>`:"";
  return `<div class="issue-item"><div><div class="issue-parent">${escapeHtml(parent.id)} &middot; ${escapeHtml(parent.name)}</div><strong>${escapeHtml(item.title)}</strong><div class="detail">Owner: ${escapeHtml(item.owner||"Not assigned")} &middot; ${item.status==="Resolved"?`Resolved ${formatDate(item.resolvedDate)}`:`Target ${formatDate(item.targetDate)}`}</div>${mitigation}</div><span class="badge ${badgeClass(item.severity)}">${escapeHtml(item.severity)}</span></div>`;
}

function renderOverview(){
  const items=state.data.useCases;
  byId("recordCount").textContent=`${items.length} use case${items.length===1?"":"s"}`;
  const pending=items.reduce((sum,item)=>sum+pendingReviews(item).length,0);
  const attention=items.filter(item=>["At Risk","Blocked","Needs Review"].includes(item.health)).length;
  const overdue=items.reduce((sum,item)=>sum+overdueActions(item),0);
  const values=[
    ["Total use cases",items.length,"Current approved inventory"],
    ["In progress",statusCount("In Progress"),"Moving through governance"],
    ["Live",statusCount("Live"),"Operating in production"],
    ["Needs attention",attention,"At risk, blocked, or needs review"],
    ["Pending reviews",pending,"Formal group decisions outstanding"],
    ["Overdue actions",overdue,"Controls and risk treatments past due"]
  ];
  byId("kpiGrid").innerHTML=values.map(([label,value,note])=>`<div class="kpi"><div class="kpi-label">${label}</div><div class="kpi-value">${value}</div><div class="kpi-note">${note}</div></div>`).join("");
  const updates=[...items].sort((a,b)=>String(b.lastUpdated||"").localeCompare(String(a.lastUpdated||"")));
  byId("latestUpdates").innerHTML=updates.length?updates.slice(0,8).map(item=>`<div class="update-item"><span class="badge ${badgeClass(item.health)}">${escapeHtml(item.health)}</span><div><strong>${escapeHtml(item.name)}</strong><div class="detail">${escapeHtml(item.currentActivity||"No current activity recorded")}${item.blocker?` &middot; Blocker: ${escapeHtml(item.blocker)}`:""}</div></div><span class="date">${escapeHtml(item.phase)}</span></div>`).join(""):empty("No use-case updates have been published.");
  const decisions=items.filter(item=>item.nextDecision||item.nextDecisionDate).sort((a,b)=>String(a.nextDecisionDate||"9999").localeCompare(String(b.nextDecisionDate||"9999")));
  byId("decisionList").innerHTML=decisions.length?decisions.slice(0,10).map(item=>`<div class="decision-item"><span class="date">${formatDate(item.nextDecisionDate)}</span><div><strong>${escapeHtml(item.nextDecision||"Decision not described")}</strong><div class="detail">${escapeHtml(item.id)} &middot; ${escapeHtml(item.name)} &middot; ${escapeHtml(item.phase)}</div></div><span class="badge neutral">${escapeHtml(item.status)}</span></div>`).join(""):empty("No upcoming decisions have been published.");
}

function populateFilters(){
  [["statusFilter",STATUSES],["departmentFilter",[...new Set(state.data.useCases.map(item=>item.department).filter(Boolean))].sort()]].forEach(([id,values])=>{const element=byId(id);while(element.options.length>1)element.remove(1);values.forEach(value=>element.add(new Option(value,value)));});
}

function renderPipeline(){
  const query=normal(byId("searchFilter").value),status=byId("statusFilter").value,department=byId("departmentFilter").value;
  const matches=state.data.useCases.filter(item=>(!query||[item.id,item.name,item.department,item.owner,item.currentActivity,item.currentStep].some(value=>normal(value).includes(query)))&&(!status||item.status===status)&&(!department||item.department===department));
  byId("pipelineBoard").innerHTML=PHASES.map(phase=>{const phaseItems=matches.filter(item=>item.phase===phase);return `<section class="phase-column"><h3 class="phase-title">${escapeHtml(phase)}<span>${phaseItems.length}</span></h3><div class="phase-cards">${phaseItems.length?phaseItems.map(card).join(""):`<div class="detail">No use cases</div>`}</div></section>`;}).join("");
}

function renderReviewQueue(){
  const rows=state.data.useCases.flatMap(parent=>(parent.formalReviews||[]).map(review=>({parent,review}))).sort((a,b)=>REVIEW_GROUPS.indexOf(a.review.group)-REVIEW_GROUPS.indexOf(b.review.group)||String(a.parent.id).localeCompare(String(b.parent.id)));
  const pending=rows.filter(({review})=>review.applicability==="Required"&&!COMPLETE_REVIEW_STATUSES.has(review.status));
  byId("reviewKpis").innerHTML=REVIEW_GROUPS.map(group=>{const count=pending.filter(item=>item.review.group===group).length;return `<div class="kpi"><div class="kpi-label">${escapeHtml(group)}</div><div class="kpi-value">${count}</div><div class="kpi-note">Pending required reviews</div></div>`;}).join("");
  byId("reviewQueue").innerHTML=pending.length?pending.map(({parent,review})=>`<div class="review-row"><div><div class="issue-parent">${escapeHtml(parent.id)} &middot; ${escapeHtml(parent.name)}</div><strong>${escapeHtml(review.group)} review</strong><div class="detail">Phase: ${escapeHtml(review.phase)} &middot; Submitted: ${formatDate(review.submittedDate)}${review.conditions?` &middot; ${escapeHtml(review.conditions)}`:""}</div></div><span class="badge ${badgeClass(review.status)}">${escapeHtml(review.status)}</span></div>`).join(""):empty("No formal reviews are waiting for action.");
}

function renderTechnicalRisks(){
  const rows=state.data.useCases.flatMap(parent=>(parent.technicalRisks||[]).map(risk=>({parent,risk})));
  const active=rows.filter(({risk})=>risk.status!=="Closed");
  const values=[
    ["Active risks",active.length,"Open, mitigating, monitoring, or accepted"],
    ["High residual",active.filter(({risk})=>risk.residualRisk==="High").length,"Requires active treatment or decision"],
    ["Critical residual",active.filter(({risk})=>risk.residualRisk==="Critical").length,"Blocks gate without authorized exception"],
    ["Past due",active.filter(({risk})=>isOverdue(risk.targetDate,risk.status)).length,"Mitigation target has passed"]
  ];
  byId("riskKpis").innerHTML=values.map(([label,value,note])=>`<div class="kpi"><div class="kpi-label">${label}</div><div class="kpi-value">${value}</div><div class="kpi-note">${note}</div></div>`).join("");
  byId("technicalRiskList").innerHTML=active.length?active.map(({parent,risk})=>`<article class="risk-card"><div class="card-top"><div><div class="use-case-id">${escapeHtml(risk.id)} &middot; ${escapeHtml(parent.id)}</div><h3>${escapeHtml(risk.title)}</h3></div><span class="badge ${badgeClass(risk.residualRisk)}">${escapeHtml(risk.residualRisk)} residual</span></div><p>${escapeHtml(risk.scenario)}</p><div class="detail"><strong>Category:</strong> ${escapeHtml(risk.category)} &middot; <strong>Owner:</strong> ${escapeHtml(risk.ownerGroup)} &middot; <strong>Target:</strong> ${formatDate(risk.targetDate)}</div><div class="mitigation"><strong>Mitigation:</strong> ${escapeHtml(risk.mitigation)}</div></article>`).join(""):empty("No technical risks have been entered. The Design gate remains incomplete until applicable risks are assessed.");
}

function renderOperationalViews(){
  const live=state.data.useCases.filter(item=>item.status==="Live");
  byId("productionGrid").innerHTML=live.length?live.map(card).join(""):empty("No live use cases have been published.");
  const closed=state.data.useCases.filter(item=>item.status==="Closed");
  byId("closedGrid").innerHTML=closed.length?closed.map(card).join(""):empty("No closed use cases have been published.");
  const joined=state.data.useCases.flatMap(parent=>(parent.issues||[]).map(record=>({record,parent})));
  const open=joined.filter(({record})=>record.status!=="Resolved"),resolved=joined.filter(({record})=>record.status==="Resolved");
  byId("openIssues").innerHTML=open.length?open.map(({record,parent})=>issue(record,parent)).join(""):empty("No open production issues.");
  byId("resolvedIssues").innerHTML=resolved.length?resolved.map(({record,parent})=>issue(record,parent)).join(""):empty("No resolved issues have been published.");
}

function requirementRow(requirement){
  const evidence=(requirement.evidence||[]).length?`${requirement.evidence.length} evidence item${requirement.evidence.length===1?"":"s"}`:"No evidence linked";
  return `<div class="requirement-row ${isOverdue(requirement.targetDate,requirement.status)?"overdue":""}"><div><span class="control-id">${escapeHtml(requirement.id)}</span><strong>${escapeHtml(requirement.title)}</strong><div class="detail">Owner: ${escapeHtml(requirement.ownerGroup||"Not assigned")} &middot; Target: ${formatDate(requirement.targetDate)} &middot; ${escapeHtml(evidence)}${requirement.notes?` &middot; ${escapeHtml(requirement.notes)}`:""}</div></div><span class="badge ${badgeClass(requirement.status)}">${escapeHtml(requirement.status)}</span></div>`;
}

function phaseDetail(phase,currentPhase){
  const gate=phase.gate||{};
  return `<details class="phase-detail" ${phase.phase===currentPhase?"open":""}><summary><span><strong>${escapeHtml(phase.phase)}</strong><small>${escapeHtml(phase.playbookPhase||phaseCatalog(phase.phase).playbookPhase||"")}</small></span><span class="phase-summary"><span>${phase.readiness}% controls</span><span class="badge ${badgeClass(phase.status)}">${escapeHtml(phase.status)}</span><span class="badge ${badgeClass(gate.status)}">Gate: ${escapeHtml(gate.status||"Not Started")}</span></span></summary><div class="progress-track"><i style="width:${Math.max(0,Math.min(100,Number(phase.readiness)||0))}%"></i></div><div class="phase-dates">Started: ${formatDate(phase.startedDate)} &middot; Target: ${formatDate(phase.targetDate)} &middot; Completed: ${formatDate(phase.completedDate)}</div>${gate.decision||gate.conditions?`<div class="gate-note"><strong>Gate decision:</strong> ${escapeHtml(gate.decision||"Not recorded")} &middot; ${escapeHtml(gate.conditions||"No conditions recorded")}</div>`:""}<div class="requirement-list">${(phase.requirements||[]).map(requirementRow).join("")}</div></details>`;
}

function showCaseDetail(id){
  const item=state.data.useCases.find(record=>record.id===id);
  if(!item)return;
  byId("caseDetailTitle").textContent=`${item.id} · ${item.name}`;
  byId("caseDetailBody").innerHTML=`
    <div class="detail-hero"><div><div class="eyebrow">${escapeHtml(item.department)} &middot; ${escapeHtml(item.phase)}</div><p>${escapeHtml(item.summary||"No summary recorded")}</p></div><div class="detail-badges"><span class="badge ${badgeClass(item.status)}">${escapeHtml(item.status)}</span><span class="badge ${badgeClass(item.health)}">${escapeHtml(item.health)}</span><span class="badge ${badgeClass(item.riskTier)}">Risk: ${escapeHtml(item.riskTier)}</span></div></div>
    <div class="detail-grid"><div class="detail-panel"><h3>Current position</h3><dl><dt>Owner</dt><dd>${escapeHtml(item.owner||"Not recorded")}</dd><dt>Sponsor</dt><dd>${escapeHtml(item.sponsor||"Not recorded")}</dd><dt>Current step</dt><dd>${escapeHtml(item.currentStep||"Not recorded")}</dd><dt>Current activity</dt><dd>${escapeHtml(item.currentActivity||"Not recorded")}</dd><dt>Blocker</dt><dd>${escapeHtml(item.blocker||"None recorded")}</dd><dt>Next decision</dt><dd>${escapeHtml(item.nextDecision||"Not recorded")} &middot; ${formatDate(item.nextDecisionDate)}</dd></dl></div><div class="detail-panel"><h3>Benefit measurement</h3><dl><dt>Measure</dt><dd>${escapeHtml(item.benefits.measure||"Not established")}</dd><dt>Baseline</dt><dd>${escapeHtml(item.benefits.baseline||"Not established")}</dd><dt>Target</dt><dd>${escapeHtml(item.benefits.target||"Not established")}</dd><dt>Current</dt><dd>${escapeHtml(item.benefits.current||"Not measured")}</dd><dt>Cadence</dt><dd>${escapeHtml(item.benefits.cadence||"Not established")}</dd></dl></div></div>
    <section class="detail-section"><div class="section-heading compact"><div><span class="eyebrow">Full lifecycle</span><h2>Phase requirements and gates</h2></div></div>${(item.phases||[]).map(phase=>phaseDetail(phase,item.phase)).join("")}</section>
    <section class="detail-section"><div class="section-heading compact"><div><span class="eyebrow">Assurance</span><h2>Formal reviews</h2></div></div><div class="review-grid">${(item.formalReviews||[]).map(review=>`<article class="review-card"><div class="card-top"><h3>${escapeHtml(review.group)}</h3><span class="badge ${badgeClass(review.status)}">${escapeHtml(review.status)}</span></div><div class="detail">${escapeHtml(review.phase)} &middot; ${escapeHtml(review.applicability)} &middot; Decision: ${formatDate(review.decisionDate)}</div><p>${escapeHtml(review.conditions||"No public conditions recorded.")}</p></article>`).join("")||empty("No formal reviews recorded.")}</div></section>
    <section class="detail-section"><div class="section-heading compact"><div><span class="eyebrow">Technical assurance</span><h2>Risks and mitigations</h2></div></div><div class="risk-grid">${(item.technicalRisks||[]).map(risk=>`<article class="risk-card"><div class="card-top"><div><div class="use-case-id">${escapeHtml(risk.id)}</div><h3>${escapeHtml(risk.title)}</h3></div><span class="badge ${badgeClass(risk.residualRisk)}">${escapeHtml(risk.residualRisk)} residual</span></div><p>${escapeHtml(risk.scenario)}</p><div class="detail">${escapeHtml(risk.category)} &middot; ${escapeHtml(risk.ownerGroup)} &middot; ${escapeHtml(risk.status)}</div><div class="mitigation"><strong>Mitigation:</strong> ${escapeHtml(risk.mitigation)}</div></article>`).join("")||empty("No technical risks entered. Complete the Design technical-risk assessment before gate approval.")}</div></section>
    <section class="detail-section"><div class="section-heading compact"><div><span class="eyebrow">Audit trail</span><h2>Recorded decisions</h2></div></div><div>${(item.decisions||[]).map(decision=>`<div class="decision-item"><span class="date">${formatDate(decision.decisionDate)}</span><div><strong>${escapeHtml(decision.decision)}</strong><div class="detail">${escapeHtml(decision.phase)} &middot; ${escapeHtml(decision.type)} &middot; ${escapeHtml(decision.decisionByGroup)}${decision.conditions?` &middot; ${escapeHtml(decision.conditions)}`:""}</div></div><span class="badge neutral">${escapeHtml(decision.outcome)}</span></div>`).join("")||empty("No decisions recorded.")}</div></section>`;
  const dialog=byId("caseDetailDialog");
  if(typeof dialog.showModal==="function")dialog.showModal();else dialog.setAttribute("open","");
}

function closeCaseDetail(){const dialog=byId("caseDetailDialog");if(typeof dialog.close==="function")dialog.close();else dialog.removeAttribute("open");}

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
    state.catalog=await fetchJson(CATALOG_URL,"Governance control catalog");
    let data;
    try{data=await discoverInventory();}
    catch(discoveryError){console.warn(discoveryError.message);data=await fallbackInventory();}
    if(!Array.isArray(data.useCases))throw new Error("Inventory data is not in the expected format.");
    state.data=data;
    byId("freshness").textContent=data.generatedAt?`Published ${formatDate(data.generatedAt)}`:"Awaiting first approved inventory publication";
    renderOverview();populateFilters();renderPipeline();renderReviewQueue();renderTechnicalRisks();renderOperationalViews();
    byId("loading").classList.add("hidden");
    const parameters=new URLSearchParams(window.location.search);
    const requestedView=parameters.get("view");
    if(VIEWS.includes(requestedView))selectView(requestedView);
    const requestedCase=parameters.get("case");
    if(requestedCase)showCaseDetail(requestedCase);
  }catch(error){byId("loading").innerHTML=`<div class="empty-state"><strong>The AI Inventory could not load</strong>${escapeHtml(error.message)}</div>`;console.error(error);}
}

document.querySelectorAll(".tabs button").forEach(button=>button.addEventListener("click",()=>selectView(button.dataset.view)));
["searchFilter","statusFilter","departmentFilter"].forEach(id=>byId(id).addEventListener(id==="searchFilter"?"input":"change",renderPipeline));
byId("printButton").addEventListener("click",()=>window.print());
byId("presentButton").addEventListener("click",()=>togglePresentation());
byId("exitPresentation").addEventListener("click",()=>togglePresentation(false));
byId("previousSlide").addEventListener("click",()=>{state.slide--;updatePresentation();});
byId("nextSlide").addEventListener("click",()=>{state.slide++;updatePresentation();});
byId("caseDetailClose").addEventListener("click",closeCaseDetail);
byId("caseDetailDialog").addEventListener("click",event=>{if(event.target===byId("caseDetailDialog"))closeCaseDetail();});
document.addEventListener("click",event=>{const button=event.target.closest(".detail-button");if(button)showCaseDetail(button.dataset.caseId);});
document.addEventListener("keydown",event=>{if(!document.body.classList.contains("presentation-mode"))return;if(["ArrowRight","PageDown"," "].includes(event.key)){event.preventDefault();state.slide++;updatePresentation();}if(["ArrowLeft","PageUp"].includes(event.key)){event.preventDefault();state.slide--;updatePresentation();}if(event.key==="Escape")togglePresentation(false);});
load();
