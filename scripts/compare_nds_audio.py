#!/usr/bin/env python3
"""Make a portable A/B listening page for the NDS import experiment.

Reference input is software DS synthesis. Target input is actual mGBA SDL
capture. Loudness normalization does not establish fidelity or alignment.
"""
import argparse
import base64
import html
import json
from pathlib import Path
import wave

from compare_fidelity import normalize_wav
from scan_audio import fingerprint


def make_comparison(experiment, reference, destination):
    manifest = json.loads((experiment / 'build.json').read_text())
    sequence_name = manifest['nds_conversion']['sequence_name']
    game_number = {'ssr1': '1', 'ssr2': '2', 'ssr3': '3'}[manifest['nds_conversion']['source_profile'][:4]]
    game_label = f'流星 {game_number}'
    preview = experiment / 'preview/preview.wav'
    with wave.open(str(preview), 'rb') as stream:
        params = stream.getparams()
    if (params.nchannels, params.sampwidth, params.framerate) != (2, 2, 44100):
        raise ValueError('Expected 44.1 kHz signed 16-bit stereo mGBA capture')
    raw = (reference / 'source.pcm').read_bytes()
    size = params.nframes * 4
    if len(raw) < size:
        raise ValueError('DS reference is shorter than the target capture')
    destination.mkdir(parents=True, exist_ok=False)
    source_wav = destination / 'source.wav'
    with wave.open(str(source_wav), 'wb') as stream:
        stream.setnchannels(2)
        stream.setsampwidth(2)
        stream.setframerate(44100)
        stream.writeframes(raw[:size])
    runs = []
    for key, label, path in [('source', 'DS software reference · SSEQPlayer', source_wav),
                             ('target', 'EXE6 actual emulator output · mGBA', preview)]:
        normalized = destination / (key + '-normalized.wav')
        levels = normalize_wav(path, normalized)
        runs.append({'key': key, 'label': label, 'path': str(path.resolve()),
                     'wav_fingerprint': fingerprint(path.read_bytes()), **levels})
    metadata = {'schema_version': 1, 'song': f'Star Force {game_number} · ' + sequence_name,
                'duration_seconds': params.nframes / params.framerate, 'runs': runs,
                'reference': json.loads((reference / 'reference.json').read_text()),
                'target': json.loads((experiment / 'preview/preview.json').read_text()),
                'limitations': ['Software DS reference, not a DS emulator/hardware capture.',
                                'Clips trimmed to equal duration, not sample-aligned.',
                                'Whole-clip RMS normalization with peak headroom.',
                                'GBA voice budget, envelopes and mixer differ from DS.']}
    if manifest['nds_conversion'].get('native_pitch_lfo_approximation'):
        metadata['native_pitch_lfo_approximation'] = True
        metadata['limitations'].append('Native triangle pitch LFO approximates per-voice DS sine; overlapping notes share/reset track phase.')
    if manifest['nds_conversion'].get('envelope_approximation'):
        metadata['envelope_approximation'] = True
        metadata['limitations'].append('Note-on ADSR snapshots; native linear attack fits DS attenuation attack with frame-rate and shape differences.')
    (destination / 'comparison.json').write_text(json.dumps(metadata, indent=2) + '\n')
    lfo_notice = ('<p>本版以 GBA 原生颤音近似 DS 效果，波形及重叠长音的相位会有差异，请留意长音和叠音的听感。</p>'
                  if manifest['nds_conversion'].get('native_pitch_lfo_approximation') else '')
    envelope_notice = ('<p>本版按音符开始时的参数生成包络；渐入起音由 GBA 包络近似，变化曲线和时间精度存在差异，请留意起音与尾音。</p>'
                       if manifest['nds_conversion'].get('envelope_approximation') else '')
    content = ['<!doctype html><html lang="zh-CN"><meta charset="utf-8">',
               '<meta name="viewport" content="width=device-width, initial-scale=1">',
               f'<title>{game_label} → EXE6：{html.escape(sequence_name)} 试听</title>',
               '<style>body{font:17px/1.65 system-ui;max-width:850px;margin:40px auto;padding:0 20px;background:#101720;color:#e6edf3}section{padding:20px;margin:20px 0;background:#1b2532;border-radius:12px}audio{width:100%}p{color:#b8c7d8}button{font:inherit;padding:6px 14px;cursor:pointer}</style>',
               f'<h1>{game_label} → EXE6：{html.escape(sequence_name)}</h1>',
               f'<p>第一阶段单曲实验。两段各 {metadata["duration_seconds"]:g} 秒，已统一整体响度。DS 一侧是软件参考合成，EXE6 一侧是导出 ROM 的真实模拟器录音。</p>',
               '<p>此页面用于比较听感，不证明整曲循环或游戏场景验证通过。GBA 的发声预算、8 位采样和包络近似仍会影响听感，具体检查结果见实验报告。</p>', lfo_notice, envelope_notice]
    for run in runs:
        key = run['key']
        encoded = base64.b64encode((destination / (key + '-normalized.wav')).read_bytes()).decode()
        content.extend([f'<section><h2>{html.escape(run["label"])}</h2>',
                        f'<audio id="{key}" controls preload="none" src="data:audio/wav;base64,{encoded}"></audio></section>'])
    content.extend(['<p><button id="switch">切换到另一段同一位置</button> <button id="stop">停止</button></p>',
                    '<script>const tracks=[document.querySelector("#source"),document.querySelector("#target")];let active=0;tracks.forEach((a,i)=>a.addEventListener("play",()=>{active=i;tracks[1-i].pause()}));document.querySelector("#switch").onclick=async()=>{const previous=tracks[active],next=tracks[1-active];const t=previous.currentTime;previous.pause();if(next.readyState<1){const ready=new Promise(resolve=>next.addEventListener("loadedmetadata",resolve,{once:true}));next.load();await ready}next.currentTime=Math.min(t,next.duration);await next.play()};document.querySelector("#stop").onclick=()=>tracks.forEach(a=>a.pause());</script>',
                    '</html>'])
    (destination / 'listen.html').write_text('\n'.join(content) + '\n')
    return destination / 'listen.html'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', type=Path)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(make_comparison(args.experiment, args.reference, args.out))


if __name__ == '__main__':
    main()
