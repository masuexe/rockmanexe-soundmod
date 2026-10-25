// Waiting feedback must stop on playback, cancellation, failure and replacement.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../web/realtime.js',import.meta.url),'utf8');
const flush=async()=>{for(let i=0;i<15;i++)await Promise.resolve();};
function fixture({failModule=false}={}){
  let now=0,next=0;const timers=new Map(),requests=[],nodes=[],events=[];
  class Context{constructor(){this.sampleRate=48000;this.destination={};this.audioWorklet={addModule:async()=>{if(failModule)throw new Error('module failed');}};}async resume(){}async close(){}}
  class Node{constructor(){this.port={postMessage(){},close(){}};nodes.push(this);}connect(){}disconnect(){}}
  function fetch(path,options){
    if(path==='/api/realtime/stop')return Promise.resolve({ok:true});
    const request={...options};requests.push(request);
    return new Promise((resolve,reject)=>{
      request.resolve=()=>resolve({ok:true,headers:{get:name=>name==='X-Audio-Sample-Rate'?'48000':'session-id'},body:{getReader:()=>({read:()=>new Promise((r,j)=>{options.signal.addEventListener('abort',()=>j(Object.assign(new Error('aborted'),{name:'AbortError'})),{once:true});})})}});
      request.reject=reject;
      options.signal.addEventListener('abort',()=>reject(Object.assign(new Error('aborted'),{name:'AbortError'})),{once:true});
    });
  }
  const context=vm.createContext({window:{AudioContext:Context},AudioWorkletNode:Node,AbortController,fetch,performance:{now:()=>now},setInterval:fn=>{timers.set(++next,fn);return next;},clearInterval:id=>timers.delete(id),Uint8Array,Float32Array,Promise,Error});
  vm.runInContext(source,context);
  return {client:new context.window.ExeRealtime('token',e=>events.push(e)),timers,requests,nodes,events,tick:ms=>{now=ms;for(const fn of [...timers.values()])fn();}};
}
{
 const f=fixture(),play=f.client.play('slow');await flush();assert.equal(f.requests.length,1);f.tick(6000);assert.equal(f.events.at(-1).elapsed_ms,6000);assert.equal(f.events.at(-1).key,'slow');await f.client.stop();await play;assert.equal(f.timers.size,0);assert.equal(f.events.at(-1).type,'stopped');
}
{
 const f=fixture(),play=f.client.play('ready');await flush();f.requests[0].resolve();await flush();f.nodes[0].port.onmessage({data:{type:'started'}});assert.equal(f.timers.size,0);assert.equal(f.events.at(-1).type,'playing');await f.client.stop();await play;
}
{
 const f=fixture(),first=f.client.play('old');await flush();const stale=[...f.timers.values()][0];const second=f.client.play('new');await flush();const count=f.events.length;stale();assert.equal(f.events.length,count);f.tick(7000);assert.equal(f.events.at(-1).key,'new');assert.equal(f.timers.size,1);await f.client.stop();await Promise.all([first,second]);assert.equal(f.timers.size,0);
}
{
 const f=fixture(),first=f.client.play('simultaneous-old'),second=f.client.play('simultaneous-new');await flush();f.tick(1000);assert.equal(f.timers.size,1);assert.equal(f.events.at(-1).key,'simultaneous-new');await f.client.stop();await Promise.all([first,second]);assert.equal(f.timers.size,0);
}
{
 const f=fixture({failModule:true});await assert.rejects(f.client.play('broken'),/module failed/);assert.equal(f.timers.size,0);assert.equal(f.client.active,false);
 const g=fixture(),play=g.client.play('http-error');await flush();g.requests[0].reject(new Error('network failed'));await assert.rejects(play,/network failed/);assert.equal(g.timers.size,0);
}
console.log('Realtime client checks passed: elapsed wait, start, stop, replacement and error cleanup.');
