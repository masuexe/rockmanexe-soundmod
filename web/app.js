'use strict';
const $ = id => document.getElementById(id);
let state, project, focused, busy = false;
let selectedSources = new Set();
const roles = {base:'Original target ROM', pvp:'PvP BPS pre-patch'};
const sourceNames = {pvp:'Native target music'};
const messages = {empty:'Empty entry',preserved_native_audio:'Preserved native audio',reserved_nonmusic_entry:'Other audio; not imported',exceeds_target_track_capacity:'Exceeds target voice capacity',unsupported_dependencies:'Unsupported audio dependencies'};
const live = new window.ExeRealtime(window.MANAGER_TOKEN, event=>{
  if(event.type==='loading')$('live-status').textContent=`Starting ${event.key}…`;
  if(event.type==='playing'){$('live-status').textContent=`Playing ${event.key}`;$('live-status').dataset.latencyMs=event.latency_ms.toFixed(1);}
  if(event.type==='progress'){$('live-status').dataset.frames=event.consumed;$('live-status').dataset.peak=Math.max(Number($('live-status').dataset.peak||0),event.peak);$('live-status').dataset.underruns=event.underruns;}
  if(event.type==='stopped')$('live-status').textContent='Stopped';
  if(event.type==='ended')$('live-status').textContent='Song ended';
  $('stop-preview').disabled=!live.active;
});
const clone = value => JSON.parse(JSON.stringify(value));
function status(message, error=false) { $('status').textContent=message; $('status').className=error?'error':''; }
async function api(path, body, headers={}) {
  const response=await fetch(path,{method:body===undefined?'GET':'POST',headers:{'X-Manager-Token':window.MANAGER_TOKEN,...(body===undefined || body instanceof File ? {} : {'Content-Type':'application/json'}),...headers},body:body===undefined?undefined:body instanceof File?body:JSON.stringify(body)});
  const value=await response.json(); if(!response.ok) throw new Error(value.error || 'Request failed'); return value;
}
function fileURL(job, file){return `/files/${job}/${file}?token=${encodeURIComponent(window.MANAGER_TOKEN)}`;}
async function task(path, body) {
  if(busy) return; setBusy(true);
  try {const {job_id}=await api(path,body); let job;
    do { job=await api('/api/job/'+job_id); if(job.status==='running') {status(`${job.kind==='preview'?'Recording audio preview':job.kind==='export'?'Building and verifying patch':'Reading audio catalog'}…`); await new Promise(r=>setTimeout(r,400));} } while(job.status==='running');
    if(job.status==='error') throw new Error(job.message); return job;
  } finally {setBusy(false);}
}
function sourcesChanged(){return !!state && [...new Set([...selectedSources,...(state.selected_sources||[])])].some(key=>selectedSources.has(key)!==(state.selected_sources||[]).includes(key));}
function valid(){return !sourcesChanged() && state?.catalog && Object.keys(project.pools).length && Object.values(project.pools).every(p=>p.tracks.length>0 && p.tracks.length<=255);}
function setBusy(value){busy=value; for(const e of document.querySelectorAll('button, input, select')) e.disabled=value || e.dataset?.eligible==='false'; $('stop-preview').disabled=!live.active; if(!value){$('export').disabled=!valid(); $('play-now').disabled=sourcesChanged() || !focused?.playlist_eligible || !state?.realtime_available; $('preview').disabled=sourcesChanged() || !focused?.playlist_eligible || !state?.preview_available; $('name').disabled=$('save-name').disabled=!focused;}}
function entries(){return state?.catalog?.entries || [];}
function eventGroup(){const key=$('rule').value;return key.startsWith('group:') ? state?.catalog?.event_groups?.[key.slice(6)] || null : null;}
function selectedTriggers(){return eventGroup()?.events.map(String) || [$('rule').value];}
function pool(){return project?.pools[selectedTriggers()[0]];}
function editPool(tracks){for(const trigger of selectedTriggers())project.pools[trigger]={tracks:[...tracks],selector_shift:0};}

function visible(){const query=$('search').value.toLowerCase(),source=$('source').value;return entries().filter(r=>(!source||r.source===source)&&($('unavailable').checked||r.playlist_eligible)&&`${r.key} ${r.name||''}`.toLowerCase().includes(query));}
function renderInputs(){
if(Number.isInteger(state.nds_library_song_count))$('nds-library-info').textContent=`NDS music: ${state.nds_library_song_count} supported Star Force 1/2/3 songs for Japanese EXE6. Other NDS tracks are not included yet. Audio is prepared on first preview/export and cached locally.`;
$('target').replaceChildren();for(const option of state.target_options||[]){const el=document.createElement('option');el.value=option.key;el.textContent=option.label+(option.available?'':' · local files missing');$('target').append(el);}$('target').value=state.selected_target||'exe45-pvp';
$('inputs').replaceChildren(); for(const [role,label] of Object.entries(roles)){if(role==='pvp'&&state.patch_required===false)continue;const card=document.createElement('div');card.className='input-card';const title=document.createElement('strong');title.textContent=role==='pvp' ? state.patch_label || label : label;const name=document.createElement('span');name.className='filename';name.textContent=state.inputs[role]?.filename || 'No file selected';const choose=document.createElement('label');choose.className='file-button';choose.textContent='Choose file';const input=document.createElement('input');input.type='file';input.accept=role==='pvp' ? state.patch_accept || '.bps' : '.gba';input.addEventListener('change',()=>guard(async()=>{if(!input.files.length)return;setBusy(true);try{state=await api('/api/upload/'+role,input.files[0],{'X-Filename':encodeURIComponent(input.files[0].name)});live.stop();focused=null;renderInputs();render();status('File selected. Load tracks to refresh the catalog.');}finally{setBusy(false);}}));choose.append(input);card.append(title,name,choose);$('inputs').append(card);} renderSourceChoices(); }
function renderSourceChoices(){
  const options=state.source_options||[];
  $('donor-summary').textContent=`${selectedSources.size} selected · ${options.length} available · ${options.filter(o=>o.loaded).length} loaded`;
  $('donor-list').replaceChildren();
  for(const option of options){const label=document.createElement('label');label.className='source-choice';const check=document.createElement('input');check.type='checkbox';check.dataset.source=option.key;check.checked=selectedSources.has(option.key);check.disabled=busy;check.addEventListener('change',()=>{check.checked?selectedSources.add(option.key):selectedSources.delete(option.key);sourceSelectionChanged();});const text=document.createElement('span');const title=document.createElement('strong');title.textContent=option.label;const filename=document.createElement('small');filename.textContent=option.filename;text.append(title,filename);label.append(check,text);$('donor-list').append(label);}
}
function sourceSelectionChanged(){live.stop();renderSourceChoices();setBusy(busy);status(sourcesChanged()?'Source selection changed. Click Load tracks to apply.':'Source selection restored. Click Load tracks to reload if needed.');}

function renderSources(){const current=$('source').value;$('source').replaceChildren();for(const [key,label] of Object.entries({'':'All sources',...(state.catalog?.source_labels || {pvp:'Native target music'})})){const option=document.createElement('option');option.value=key;option.textContent=label;$('source').append(option);}if([...$('source').children].some(e=>e.value===current))$('source').value=current;}
function renderRules(){const current=$('rule').value;$('rule').replaceChildren();for(const key of Object.keys(project.pools)){const option=document.createElement('option');option.value=key;option.textContent=state.catalog?.scene_events?.[key]?.label || state.catalog?.event_labels?.[key] || (key==='55'&&(!state.catalog?.preview_trigger || state.catalog.preview_trigger===55)?'Title screen':`Music event #${key}`);$('rule').append(option);}for(const [key,group] of Object.entries(state.catalog?.event_groups || {})){if(!group.events.every(id=>project.pools[String(id)]))continue;const option=document.createElement('option');option.value=`group:${key}`;option.textContent=group.label;$('rule').append(option);}if([...$('rule').children].some(e=>e.value===current))$('rule').value=current;}
function render(){const rows=visible(),current=pool();$('tracks').replaceChildren();$('counts').textContent=state.catalog?`${entries().filter(r=>r.playlist_eligible).length} available · ${entries().length} catalog entries · ${rows.length} shown`:'Waiting for catalog';
for(const row of rows){const div=document.createElement('div');div.className='track'+(focused?.key===row.key?' focus':'');div.dataset.key=row.key;const check=document.createElement('input');check.type='checkbox';check.dataset.eligible=String(row.playlist_eligible);check.checked=current?.tracks.includes(row.key)||false;check.disabled=busy||!row.playlist_eligible;check.setAttribute('aria-label',`Include ${row.name||row.key}`);check.addEventListener('click',e=>e.stopPropagation());check.addEventListener('change',()=>{const keys=new Set(current.tracks);check.checked?keys.add(row.key):keys.delete(row.key);editPool([...keys]);render();});const text=document.createElement('div');const title=document.createElement('div');title.className='title';title.textContent=row.name||`${row.source_label || sourceNames[row.source] || row.source} · ${row.source_index}`;const subtitle=document.createElement('small');subtitle.textContent=`${row.key}${row.playback_note?` · ${row.playback_note}`:''}${row.playlist_eligible?'':` · ${messages[row.availability]||row.availability}`}`;text.append(title,subtitle);const voices=document.createElement('span');voices.className='badge';voices.textContent=row.track_count;div.append(check,text,voices);div.addEventListener('click',()=>{live.stop();focused=row;$('name').value=row.name||'';$('detail').textContent=`${row.key} · ${row.track_count} voices${row.playback_note?` · ${row.playback_note}`:''}${row.playlist_eligible?'':` · ${messages[row.availability]||row.availability}`}`;$('playback-hint').textContent=row.nds_selector?'Play now uses the converted GBA song. For game audio, record an mGBA preview.':'Play now uses agbplay directly from the source ROM. Its enhanced mixer can sound different from the exported game.';$('audio').pause();$('audio').removeAttribute('src');render();});$('tracks').append(div);}
if(!rows.length){const empty=document.createElement('div');empty.className='empty';empty.textContent='No matching entries.';$('tracks').append(empty);}
$('pool-info').textContent=current?`${new Set(current.tracks).size} unique tracks · ${current.tracks.length} pool entries${current.tracks.length===new Set(current.tracks).size?'':' · existing weights retained until edited'}${current.tracks.length>255?' · exceeds the 255-entry limit: select fewer tracks':''}`:'Load tracks to configure a pool.';const scene=state.catalog?.scene_events?.[$('rule').value];if(scene)$('pool-info').textContent+=' '+scene.description;const group=eventGroup();if(group){const pools=selectedTriggers().map(id=>project.pools[id]);const differs=pools.some(p=>JSON.stringify(p)!==JSON.stringify(current));$('pool-info').textContent+=(differs?' · Pools differ; showing the first pool. Changes apply to all three.':' · One pool applied to all three events.')+' '+group.description;}setBusy(busy);}
function guard(fn){return Promise.resolve().then(fn).catch(error=>status(error.message,true));}
$('load').onclick=()=>guard(async()=>{await live.stop();const job=await task('/api/load',{sources:[...selectedSources],project});if(!job)return;state=await api('/api/state');selectedSources=new Set(state.selected_sources||[]);project=clone(state.project);focused=null;$('audio').pause();$('audio').removeAttribute('src');renderInputs();renderSources();renderRules();render();status(state.project_notice || `Catalog ready: ${job.result.tracks} tracks available · ${state.target_label || 'EXE4.5 PvP'}.`);});
for(const id of ['search','source','unavailable','rule'])$(id).addEventListener(id==='search'?'input':'change',render);
$('all-visible').onclick=()=>{if(!pool())return;editPool([...new Set([...pool().tracks,...visible().filter(r=>r.playlist_eligible).map(r=>r.key)])]);render();};
$('clear').onclick=()=>{if(pool()){editPool([]);render();}};
$('apply-all').onclick=()=>{if(!pool()?.tracks.length){status('Select at least one track first.',true);return;}const tracks=[...pool().tracks];for(const p of Object.values(project.pools)){p.tracks=[...tracks];p.selector_shift=0;}render();status('Current selection applied to every configured music event.');};
$('save-name').onclick=()=>guard(async()=>{const result=await api('/api/name',{key:focused.key,name:$('name').value});focused.name=result.name;project.names[focused.key]=result.name;render();status('Track name saved locally.');});
$('save-project').onclick=()=>guard(async()=>{if(!valid())throw new Error('Each music event needs 1–255 track entries.');await api('/api/project',project);status('Project saved locally.');});
$('import-project').onchange=()=>guard(async()=>{const file=$('import-project').files[0];if(!file)return;const saved=await api('/api/project',JSON.parse(await file.text()));state=saved;project=clone(saved.project);focused=null;renderRules();render();status('Project imported.');});
$('export').onclick=()=>guard(async()=>{const job=await task('/api/export',project);if(!job)return;$('downloads').replaceChildren();for(const file of job.result.files){const link=document.createElement('a');link.href=fileURL(job.id,file);link.textContent=`Download ${file}`;$('downloads').append(link);}status(`Export verified · ${(job.result.size_bytes/1048576).toFixed(2)} MiB ROM · apply BPS to ${state.inputs.base.filename}.`);});
$('preview').onclick=()=>guard(async()=>{await live.stop();const key=focused.key;const job=await task('/api/preview',{key,seconds:Number($('duration').value)});if(!job)return;if(focused?.key===key){$('audio').src=fileURL(job.id,'preview.wav');$('audio').play().catch(()=>{});}status(`Preview ready: ${key}. Press play to listen.`);});
guard(async()=>{state=await api('/api/state');selectedSources=new Set(state.selected_sources||[]);project=clone(state.project);renderInputs();renderSources();renderRules();render();if(state.active_job)status('An existing task is running; reload after it finishes.');else if(state.catalog)status(state.project_notice || 'Catalog restored. Change sources and click Load tracks when needed.');});

$('donor-files').onchange=()=>guard(async()=>{const files=[...$('donor-files').files];if(!files.length)return;setBusy(true);try{for(const file of files){state=await api('/api/upload/rom',file,{'X-Filename':encodeURIComponent(file.name)});if(state.added_source)selectedSources.add(state.added_source);}status('Original ROMs added. Load tracks to refresh the catalog.');}finally{live.stop();focused=null;renderInputs();renderSources();render();setBusy(false);}});

$('play-now').onclick=()=>guard(async()=>{if(!focused?.playlist_eligible)return;$('audio').pause();$('live-status').dataset.peak='0';$('live-status').dataset.frames='0';await live.play(focused.key);});
$('stop-preview').onclick=()=>live.stop();
$('audio').addEventListener('play',()=>live.stop());
window.addEventListener('pagehide',()=>live.stop());

$('sources-all').onclick=()=>{selectedSources=new Set((state.source_options||[]).map(o=>o.key));sourceSelectionChanged();};
$('sources-clear').onclick=()=>{selectedSources.clear();sourceSelectionChanged();};

$('target').onchange=()=>guard(async()=>{
  await live.stop();setBusy(true);
  try{state=await api('/api/target',{target:$('target').value});project=clone(state.project);focused=null;$('downloads').replaceChildren();$('audio').pause();$('audio').removeAttribute('src');renderInputs();renderSources();renderRules();render();status('Target selected. Click Load tracks to read its music and apply your source selection.');}
  catch(error){$('target').value=state.selected_target;throw error;}
  finally{setBusy(false);}
});
