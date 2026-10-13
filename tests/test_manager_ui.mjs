// Exercise UI workflows without installing browser dependencies.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
class Element {
  constructor(tag='div'){this.tagName=tag;this.children=[];this.listeners={};this.dataset={};this.value='';this.checked=false;this.disabled=false;this.textContent='';}
  append(...nodes){this.children.push(...nodes);if(this.tagName==='select'&&!this.value&&nodes.length)this.value=nodes[0].value;}
  replaceChildren(...nodes){this.children=[];if(this.tagName==='select')this.value='';this.append(...nodes);}
  addEventListener(type,fn){this.listeners[type]=fn;}
  setAttribute(key,val){this[key]=val;}
  removeAttribute(key){delete this[key];}
  pause(){}
  play(){return Promise.resolve();}
}
const elements=new Map();
const selects=new Set(['source','rule','duration','target']);
function el(id){if(!elements.has(id))elements.set(id,new Element(selects.has(id)?'select':'div'));return elements.get(id);}
el('duration').value='3';
const document={getElementById:el,createElement:tag=>new Element(tag),querySelectorAll:()=>[...elements.values()].flatMap(function flatten(e){return [e,...e.children.flatMap(flatten)];})};
const fixture={selected_target:'exe45-pvp',patch_required:true,target_options:[{key:'exe45-pvp',label:'EXE4.5 PvP',available:true},{key:'exegp',label:'EXE GP',available:true}],selected_sources:['exegp'],source_options:[{key:'exegp',label:'Battle Chip GP',filename:'exegp.gba',loaded:false},{key:'exe6',label:'EXE6',filename:'exe6.gba',loaded:false}],inputs:{base:{filename:'original.gba'}},preview_available:true,realtime_available:true,catalog:null,project:{schema_version:1,pools:{'55':{tracks:['exegp:1'],selector_shift:0},'64':{tracks:['pvp:64'],selector_shift:5}},names:{}}};
const rows=[{key:'exegp:1',source:'exegp',source_index:1,track_count:7,playlist_eligible:true,name:''},{key:'pvp:64',source:'pvp',source_index:64,track_count:6,playlist_eligible:true,name:''},{key:'exegp:5',source:'exegp',source_index:5,track_count:9,playlist_eligible:false,availability:'exceeds_target_track_capacity'}];
let exported, previewed, persisted, next=0;const jobs={};
async function fetch(path, options){const body=options.body?JSON.parse(options.body):{};let value;
 assert.equal(options.headers['X-Manager-Token'],'fixture-token');
 if(path==='/api/state')value=structuredClone(fixture);
 else if(path.startsWith('/api/job/'))value=jobs[path.split('/').at(-1)];
 else if(path==='/api/name'){value=body;fixture.project.names[body.key]=body.name;}
 else if(path==='/api/target'){fixture.selected_target=body.target;fixture.patch_required=false;fixture.inputs={base:{filename:'exegp.gba'}};fixture.catalog=null;fixture.project={schema_version:1,target_profile:'exegp',pools:{'1':{tracks:['exegp:1'],selector_shift:0}},names:{}};value=structuredClone(fixture);}
 else if(path==='/api/project'){persisted=body;fixture.project=body;value=fixture;}
 else {const id=String(++next);if(path==='/api/load'){if(fixture.selected_target==='exegp'){for(const id of [12,13,14])fixture.project.pools[id] ||= {tracks:[`native-exegp:${id}`],selector_shift:0};}fixture.selected_sources=body.sources;fixture.source_options.forEach(o=>o.loaded=body.sources.includes(o.key));fixture.catalog={entries:rows,source_labels:{pvp:'EXE4.5 PvP',exegp:'Battle Chip GP'},preview_trigger:fixture.selected_target==='exegp'?1:55,event_groups:fixture.selected_target==='exegp'?{communication:{label:'Communication battles (music #12–14)',events:[12,13,14],description:'Also used by single-player battles.'}}:{},event_labels:fixture.selected_target==='exegp'?{'1':'Title screen'}:{'55':'Title screen'}};value={tracks:2};}else if(path==='/api/export'){exported=body;value={size_bytes:9585460,files:['unified.bps','unified.gba','project.json','catalog.csv']};}else if(path==='/api/preview'){previewed=body;value={files:['preview.wav']};}else throw new Error(path);jobs[id]={id,status:'done',result:value};value={job_id:id};}
 return {ok:true,json:async()=>value};
}
const context=vm.createContext({document,window:{MANAGER_TOKEN:'fixture-token',addEventListener(){},ExeRealtime:class{constructor(token,callback){this.callback=callback;this.active=false;}async play(key){this.active=true;this.callback({type:'playing',key,latency_ms:40});}async stop(){this.active=false;this.callback({type:'stopped'});}}},fetch,File:class{},setTimeout,Promise,console,encodeURIComponent,Set,JSON});
vm.runInContext(fs.readFileSync(new URL('../web/app.js',import.meta.url),'utf8'),context);
const flush=()=>new Promise(r=>setTimeout(r,0));await flush();
assert.equal(el('export').disabled,true);assert.equal(el('donor-list').children.length,2);assert.equal(el('donor-list').children[0].children[0].checked,true);assert.equal(el('donor-list').children[1].children[0].checked,false);
await el('load').onclick();assert.equal(el('tracks').children.length,2);assert.equal(el('export').disabled,false);
el('unavailable').checked=true;el('unavailable').listeners.change();assert.equal(el('tracks').children[2].children[0].disabled,true);
el('rule').value='64';el('rule').listeners.change();
const check=el('tracks').children[0].children[0];check.checked=true;check.listeners.change();
await el('export').onclick();assert.equal(exported.pools['64'].selector_shift,0);assert.deepEqual(exported.pools['64'].tracks,['pvp:64','exegp:1']);assert.equal(el('downloads').children.length,4);
el('tracks').children[0].listeners.click();el('name').value='GP Title';await el('save-name').onclick();assert.equal(el('tracks').children[0].children[1].children[0].textContent,'GP Title');
await el('play-now').onclick();assert.match(el('live-status').textContent,/Playing exegp:1/);assert.equal(el('stop-preview').disabled,false);await el('stop-preview').onclick();assert.equal(el('stop-preview').disabled,true);
await el('preview').onclick();assert.deepEqual(previewed,{key:'exegp:1',seconds:3});assert.match(el('audio').src,/preview.wav\?token=/);
el('clear').onclick();assert.equal(el('export').disabled,true);await el('save-project').onclick();assert.match(el('status').textContent,/1–255/);
el('all-visible').onclick();el('apply-all').onclick();await el('save-project').onclick();assert.equal(persisted.pools['55'].tracks.length,2);assert.equal(persisted.pools['55'].selector_shift,0);
el('sources-clear').onclick();assert.equal(el('export').disabled,true);assert.match(el('donor-summary').textContent,/0 selected/);el('sources-all').onclick();assert.match(el('donor-summary').textContent,/2 selected/);await el('load').onclick();assert.deepEqual(fixture.selected_sources,['exegp','exe6']);
console.log('UI workflow checks passed: load, unavailable entries, pool edits, names, preview, export, project save.');

el('target').value='exegp';await el('target').onchange();
assert.equal(el('inputs').children.length,1);assert.equal(el('export').disabled,true);assert.equal(el('downloads').children.length,0);assert.equal(el('target').value,'exegp');
await el('load').onclick();assert.equal(el('rule').children[0].value,'1');assert.equal(el('rule').children[0].textContent,'Title screen');
await el('export').onclick();assert.match(el('status').textContent,/apply BPS to exegp.gba/);
console.log('Target switching checks passed: separate target input, pool IDs, title label and patch application ROM.');

const titlePool=structuredClone(exported.pools['1']);
assert.equal(el('rule').children.at(-1).value,'group:communication');
el('rule').value='group:communication';el('rule').listeners.change();
assert.match(el('pool-info').textContent,/Pools differ/);
await el('export').onclick();
for(const id of [12,13,14])assert.deepEqual(exported.pools[id].tracks,[`native-exegp:${id}`]);
el('clear').onclick();assert.equal(el('export').disabled,true);
const groupCheck=el('tracks').children[0].children[0];groupCheck.checked=true;groupCheck.listeners.change();
await el('export').onclick();
for(const id of [12,13,14])assert.deepEqual(exported.pools[id],{tracks:['exegp:1'],selector_shift:0});
assert.deepEqual(exported.pools['1'],titlePool);
assert.match(el('pool-info').textContent,/single-player/);
el('all-visible').onclick();await el('save-project').onclick();
for(const id of [12,13,14])assert.deepEqual(persisted.pools[id].tracks,['exegp:1','pvp:64']);
await el('load').onclick();assert.equal(el('rule').value,'group:communication');
el('rule').value='12';el('rule').listeners.change();el('clear').onclick();el('all-visible').onclick();
await el('export').onclick();assert.deepEqual(exported.pools['13'].tracks,['exegp:1','pvp:64']);
console.log('Communication group checks passed: distinct defaults, synchronized editing, title isolation, save/reload and individual events.');
