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
const selects=new Set(['source','rule','duration']);
function el(id){if(!elements.has(id))elements.set(id,new Element(selects.has(id)?'select':'div'));return elements.get(id);}
el('duration').value='3';
const document={getElementById:el,createElement:tag=>new Element(tag),querySelectorAll:()=>[...elements.values()].flatMap(function flatten(e){return [e,...e.children.flatMap(flatten)];})};
const fixture={inputs:{base:{filename:'original.gba'}},preview_available:true,realtime_available:true,catalog:null,project:{schema_version:1,pools:{'55':{tracks:['exegp:1'],selector_shift:0},'64':{tracks:['pvp:64'],selector_shift:5}},names:{}}};
const rows=[{key:'exegp:1',source:'exegp',source_index:1,track_count:7,playlist_eligible:true,name:''},{key:'pvp:64',source:'pvp',source_index:64,track_count:6,playlist_eligible:true,name:''},{key:'exegp:5',source:'exegp',source_index:5,track_count:9,playlist_eligible:false,availability:'exceeds_target_track_capacity'}];
let exported, previewed, persisted, next=0;const jobs={};
async function fetch(path, options){const body=options.body?JSON.parse(options.body):{};let value;
 assert.equal(options.headers['X-Manager-Token'],'fixture-token');
 if(path==='/api/state')value=structuredClone(fixture);
 else if(path.startsWith('/api/job/'))value=jobs[path.split('/').at(-1)];
 else if(path==='/api/name'){value=body;fixture.project.names[body.key]=body.name;}
 else if(path==='/api/project'){persisted=body;fixture.project=body;value=fixture;}
 else {const id=String(++next);if(path==='/api/load'){fixture.catalog={entries:rows,source_labels:{pvp:'EXE4.5 PvP',exegp:'Battle Chip GP'}};value={tracks:2};}else if(path==='/api/export'){exported=body;value={size_bytes:9585460,files:['unified.bps','unified.gba','project.json','catalog.csv']};}else if(path==='/api/preview'){previewed=body;value={files:['preview.wav']};}else throw new Error(path);jobs[id]={id,status:'done',result:value};value={job_id:id};}
 return {ok:true,json:async()=>value};
}
const context=vm.createContext({document,window:{MANAGER_TOKEN:'fixture-token',addEventListener(){},ExeRealtime:class{constructor(token,callback){this.callback=callback;this.active=false;}async play(key){this.active=true;this.callback({type:'playing',key,latency_ms:40});}async stop(){this.active=false;this.callback({type:'stopped'});}}},fetch,File:class{},setTimeout,Promise,console,encodeURIComponent,Set,JSON});
vm.runInContext(fs.readFileSync(new URL('../web/app.js',import.meta.url),'utf8'),context);
const flush=()=>new Promise(r=>setTimeout(r,0));await flush();
assert.equal(el('export').disabled,true);
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
console.log('UI workflow checks passed: load, unavailable entries, pool edits, names, preview, export, project save.');
