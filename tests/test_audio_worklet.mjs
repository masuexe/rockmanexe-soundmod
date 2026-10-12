import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
let Processor;
const context=vm.createContext({sampleRate:48000,AudioWorkletProcessor:class{constructor(){this.events=[];this.port={postMessage:message=>this.events.push(message)};}},registerProcessor:(_name,p)=>Processor=p,Math});
vm.runInContext(fs.readFileSync(new URL('../web/audio-worklet.js',import.meta.url),'utf8'),context);
const render=p=>{const channels=[new Float32Array(128),new Float32Array(128)];const running=p.process([], [channels]);return {channels,running};};
const p=new Processor();p.port.onmessage({data:{samples:new Float32Array([.25,-.5,.75,-.25])}});
assert.equal(render(p).channels[0][0],0); // Initial buffering retains all source samples.
p.port.onmessage({data:{end:true}});
let result=render(p);assert.deepEqual([...result.channels[0]].slice(0,3),[.25,.75,0]);assert.deepEqual([...result.channels[1]].slice(0,3),[-.5,-.25,0]);assert.equal(result.running,false);assert.ok(p.events.some(e=>e.type==='ended'&&e.consumed===2));
const q=new Processor();q.port.onmessage({data:{samples:new Float32Array(8000).fill(.2)}});
assert.ok(render(q).channels[0][0]>.19);q.port.onmessage({data:{stop:true}});assert.equal(render(q).running,false);
console.log('AudioWorklet checks passed: prebuffer, stereo ordering, finite-song drain, immediate stop.');
