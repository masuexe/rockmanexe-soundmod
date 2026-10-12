# Realtime music preview

The manager's **Play now** button streams music from the original ROM through agbplay's MP2K sequence and mixing engine. Playback begins after a short buffer; it does not build a transplant ROM, record a clip, or wait for WAV conversion. **Stop**, choosing another row, replacing input files, and closing the page stop the current session. Looping songs continue until stopped; finite songs drain their audio buffer and end.

The separate **Verify playback in the exported game** section retains mGBA WAV capture. Use it to check the transplanted song with the target game's actual audio driver. agbplay has an enhanced mixer and does not enforce the target PCM channel budget, so source playback is not proof of transplant compatibility. Neither this feature nor its playback settings modify the exported ROM or saved pools.

Recorded previews now include measured runtime mixer configuration in `preview.json`. For original/target WAV comparisons, source-matched mixer experiments, and per-track state probes, see [audio fidelity diagnosis](audio-fidelity.md).

## Build once

The source is the unmodified [ipatix/agbplay](https://github.com/ipatix/agbplay) core, pinned to commit `0b87da48d2502da359e45718eec8566ac40fa9d7`. The default reference checkout is `../references/agbplay`, in the shared GBA references directory.

If that checkout is absent:

```bash
git clone https://github.com/ipatix/agbplay.git ../references/agbplay
git -C ../references/agbplay checkout 0b87da48d2502da359e45718eec8566ac40fa9d7
```

For the tested Ubuntu 24.04 environment, missing dependencies can be downloaded and extracted locally without sudo:

```bash
python3 scripts/build_realtime.py --fetch-deps
python3 scripts/manage_sound.py
```

This requires a C++20 compiler, CMake 3.18+, Git, zlib development headers, `apt-get`, and `dpkg-deb`. Local packages supply fmt, Boost headers, and libzip. They are extracted under `out/realtime-deps/`; no system packages are installed. The resulting executable is `out/realtime/exe-realtime` and the core shared library is `out/realtime/libexe_agbplay.so`. Keep these outputs and the locally extracted runtime libraries together in this workspace.

When dependencies are already available, run `python3 scripts/build_realtime.py` without `--fetch-deps`. `--source PATH` chooses the pinned checkout; `--deps PATH` chooses a local dependency prefix. The helper does not require Qt, PortAudio, or a running native desktop music player. The browser handles audio output. Linux x86-64 is the tested platform; other platforms are not established.

The reference core is LGPL-3.0 licensed and is built as a separate shared library. Its sources remain in the reference checkout, its license is copied to `out/realtime/AGBPLAY-LICENSE`, and `out/realtime/engine.json` records the source revision. The adapter and build configuration are under `native/realtime/`.

Restart an existing manager server after building, then load the catalog, select a row, and click **Play now**. If the helper is absent, realtime playback is disabled and mGBA verification remains available. The browser needs AudioWorklet support and a secure context; the default local HTTP address qualifies. `--realtime PATH` selects another build of the streaming helper with the same protocol.

## Data flow

```text
Original ROM + known table + source song ID
    → agbplay scanner verifies song/player tables and SoundMode
    → MP2K sequence processing and PCM/PSG mixing
    → stereo float32 blocks on stdout
    → authenticated local HTTP streaming response
    → AudioWorklet → browser audio output
```

The helper initializes before the server commits a successful response. Its first line declares the sample rate and stereo float32 format; subsequent bytes are raw little-endian PCM. The frontend requests the AudioContext's sample rate. Original input copies are cached by SHA-256 under the manager data directory's `realtime/` subdirectory. Session logs stay there too. No preview WAV or combined ROM is generated for this path.

The worklet starts after approximately 60 ms of queued audio. The frontend limits its worklet queue to roughly half a second plus one block; read pressure then passes through the HTTP connection and process pipe. Received byte chunks need not align to stereo frames, so incomplete frames are carried to the next chunk. The worklet preserves stereo order, buffers again on underrun, and drains the queue at a finite song's end.

There is one live engine session per manager instance. Starting another song terminates the old helper. Stop requests include a session ID, so a late stop from an old song cannot terminate a newer song. Browser cancellation disconnects audio immediately and aborts the stream; explicit stop requests and HTTP cleanup terminate and reap the owned process. Input replacement and server shutdown also stop it.

## Verification

Real browser playback against the local HTTP service produced nonzero PCM and no observed underruns in the tested runs:

| Source entry | Click to first worklet playback | Verified audio consumption |
|---|---:|---:|
| `exe1:0` | 74.9 ms | 49,792 frames |
| `exe6:1` | 71.0 ms | 49,920 frames |
| `exegp:1` | 61.9 ms | 51,968 frames |

Measurements include backend startup, browser stream setup, and prebuffering on the local test machine; they are not hardware speaker latency measurements or a guarantee on other systems. The output rate was 48 kHz. Row changes, subsequent playback, and explicit stop were exercised without JavaScript exceptions, and no helper processes remained after stopping. Evidence and a screenshot are in `out/realtime-browser-validation/`.

The standalone core initialized those three ROMs in about 40 ms and generated nonzero finite float samples before a one-second audio segment was read. A further source scan initialized one eligible entry from each of the 22 original-ROM profiles and streamed a nonzero first second with finite samples. Its report is `out/realtime-browser-validation/core-source-check.json`. These checks cover profile initialization and representative audio; other entries still need playback comparison.

The Python suite passes 50 tests. Additional checks cover live PCM, initialization failure, invalid/missing helpers, cached input reuse, switch cancellation, stale stop isolation, and representative actual-core output. Two Node checks cover the manager's playback controls and worklet buffering/stereo/end/stop behavior:

```bash
python3 -m unittest discover -s tests -v
node tests/test_manager_ui.mjs
node tests/test_audio_worklet.mjs
```

The mGBA verification path and patch export remain independently checked. Source previews should be used for browsing; target playback checks remain necessary when evaluating how a transplanted song sounds in-game.
