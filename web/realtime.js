'use strict';
class ExeRealtime {
  constructor(token,onState){this.token=token;this.onState=onState;this.current=null;}
  get active(){return !!this.current;}
  wake(session){const waiters=session.waiters.splice(0);for(const resolve of waiters)resolve();}
  async stop(){
    const session=this.current;if(!session)return;
    clearInterval(session.loadingTimer);
    this.current=null;session.abort.abort();this.wake(session);
    if(session.node){session.node.port.postMessage({stop:true});session.node.disconnect();session.node.port.close();}
    session.context.close().catch(()=>{});
    if(session.id)fetch('/api/realtime/stop',{method:'POST',headers:{'X-Manager-Token':this.token,'Content-Type':'application/json'},body:JSON.stringify({id:session.id}),keepalive:true}).catch(()=>{});
    this.onState({type:'stopped',key:session.key});
  }
  async play(key){
    await this.stop();
    const AudioContext=window.AudioContext||window.webkitAudioContext;
    if(!AudioContext)throw new Error('This browser does not support Web Audio.');
    const context=new AudioContext({sampleRate:48000,latencyHint:'interactive'});
    const session={key,context,abort:new AbortController(),waiters:[],sent:0,consumed:0,started:false,startedAt:performance.now()};
    this.current=session;this.onState({type:'loading',key});
    session.loadingTimer=setInterval(()=>{
      if(this.current!==session||session.started){clearInterval(session.loadingTimer);return;}
      this.onState({type:'loading',key,elapsed_ms:performance.now()-session.startedAt});
    },1000);
    try{
      await context.resume();await context.audioWorklet.addModule('/audio-worklet.js');
      if(this.current!==session)return;
      const node=new AudioWorkletNode(context,'exe-stream',{numberOfInputs:0,numberOfOutputs:1,outputChannelCount:[2]});session.node=node;node.connect(context.destination);
      node.port.onmessage=({data})=>{
        if(this.current!==session)return;
        if(data.type==='started'){session.started=true;clearInterval(session.loadingTimer);this.onState({type:'playing',key,latency_ms:performance.now()-session.startedAt});}
        if(data.type==='progress'){session.consumed=data.consumed;this.wake(session);this.onState({...data,key,sample_rate:context.sampleRate});}
        if(data.type==='ended'){this.stop();this.onState({type:'ended',key});}
      };
      const response=await fetch('/api/realtime',{method:'POST',headers:{'X-Manager-Token':this.token,'Content-Type':'application/json'},body:JSON.stringify({key,sample_rate:context.sampleRate}),signal:session.abort.signal});
      if(!response.ok){const error=await response.json();throw new Error(error.error||'Realtime preview failed');}
      session.id=response.headers.get('X-Preview-Id');
      if(Number(response.headers.get('X-Audio-Sample-Rate'))!==context.sampleRate)throw new Error('Audio sample-rate mismatch');
      const reader=response.body.getReader();let carry=new Uint8Array(0);
      while(this.current===session){
        const {value,done}=await reader.read();if(done)break;
        const bytes=new Uint8Array(carry.length+value.length);bytes.set(carry);bytes.set(value,carry.length);
        const usable=bytes.length-bytes.length%8;carry=bytes.slice(usable);const samples=new Float32Array(bytes.buffer,0,usable/4);
        for(let offset=0;offset<samples.length&&this.current===session;offset+=8192){
          while(session.sent-session.consumed>context.sampleRate*.5&&this.current===session)await new Promise(resolve=>session.waiters.push(resolve));
          if(this.current!==session)break;
          const block=samples.slice(offset,offset+8192);session.sent+=block.length/2;node.port.postMessage({samples:block},[block.buffer]);
        }
      }
      if(this.current===session){if(carry.length)throw new Error('Truncated audio stream');node.port.postMessage({end:true});}
    }catch(error){if(this.current===session){await this.stop();if(error.name!=='AbortError')throw error;}}
  }
}
window.ExeRealtime=ExeRealtime;
