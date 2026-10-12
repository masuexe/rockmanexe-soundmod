/* Stereo float32 stream consumer; short bounded queue, no whole-song decoding. */
class ExeStreamProcessor extends AudioWorkletProcessor {
  constructor(){
    super();this.queue=[];this.offset=0;this.frames=0;this.consumed=0;this.clock=0;this.peak=0;this.ready=false;this.announced=false;this.finished=false;this.stopped=false;this.underruns=0;
    this.port.onmessage=({data})=>{if(data.samples){this.queue.push(data.samples);this.frames+=data.samples.length/2;}if(data.end)this.finished=true;if(data.stop){this.stopped=true;this.queue=[];this.frames=0;}};
  }
  process(_inputs,outputs){
    if(this.stopped)return false;
    const output=outputs[0];if(!output?.length)return true;
    if(!this.ready&&(this.frames>=sampleRate*.06||this.finished))this.ready=true;
    if(this.ready){
      for(let i=0;i<output[0].length;i++){
        if(!this.queue.length){if(!this.finished){this.underruns++;this.ready=false;}break;}
        const block=this.queue[0];const l=block[this.offset++],r=block[this.offset++];
        output[0][i]=l;if(output[1])output[1][i]=r;
        this.peak=Math.max(this.peak,Math.abs(l),Math.abs(r));this.frames--;this.consumed++;
        if(this.offset===block.length){this.queue.shift();this.offset=0;}
        if(!this.announced){this.announced=true;this.port.postMessage({type:'started'});}
      }
    }
    this.clock+=output[0].length;
    if(this.clock>=2048){this.clock=0;this.port.postMessage({type:'progress',consumed:this.consumed,buffered:this.frames,peak:this.peak,underruns:this.underruns});this.peak=0;}
    if(this.finished&&!this.frames){this.port.postMessage({type:'ended',consumed:this.consumed});return false;}
    return true;
  }
}
registerProcessor('exe-stream',ExeStreamProcessor);
