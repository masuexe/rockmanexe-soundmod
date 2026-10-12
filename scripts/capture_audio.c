/* Capture mGBA's complete SDL output (Direct Sound + PSG) after an explicit gate.
 * Only injected into the disposable preview process. Uses SDL2's public ABI.
 */
#define _GNU_SOURCE
#include <SDL2/SDL.h>
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

struct Capture {
    SDL_AudioCallback callback;
    void *userdata;
    SDL_AudioSpec spec;
    FILE *file;
    size_t written;
    size_t limit;
    int finished;
};
static struct Capture capture;

static void mark(const char *name, const char *text) {
    const char *directory = getenv("EXE_CAPTURE_DIR");
    if (!directory) return;
    char path[4096];
    snprintf(path, sizeof(path), "%s/%s", directory, name);
    FILE *file = fopen(path, "w");
    if (file) { fputs(text, file); fclose(file); }
}

static void callback(void *userdata, Uint8 *stream, int length) {
    struct Capture *state = userdata;
    state->callback(state->userdata, stream, length);
    if (state->finished) return;
    const char *directory = getenv("EXE_CAPTURE_DIR");
    if (!directory) return;
    char path[4096];
    snprintf(path, sizeof(path), "%s/enabled", directory);
    if (access(path, F_OK)) return;
    if (!state->file) {
        if (state->spec.format != AUDIO_S16LSB || !state->spec.channels || state->spec.freq <= 0) {
            mark("error.txt", "Preview capture requires little-endian signed 16-bit SDL output");
            state->finished = 1; return;
        }
        snprintf(path, sizeof(path), "%s/audio.pcm", directory);
        state->file = fopen(path, "wb");
        if (!state->file) { mark("error.txt", "Cannot open audio capture"); state->finished = 1; return; }
        double seconds = strtod(getenv("EXE_CAPTURE_SECONDS") ? getenv("EXE_CAPTURE_SECONDS") : "12", NULL);
        state->limit = (size_t)(seconds * state->spec.freq) * state->spec.channels * 2;
        char info[256];
        snprintf(info, sizeof(info), "{\"frequency\":%d,\"channels\":%d,\"sample_width\":2,\"format\":%u}\n",
                 state->spec.freq, state->spec.channels, state->spec.format);
        mark("audio-format.json", info);
    }
    size_t amount = (size_t)length;
    if (amount > state->limit - state->written) amount = state->limit - state->written;
    if (fwrite(stream, 1, amount, state->file) != amount) {
        mark("error.txt", "Audio capture write failed"); state->finished = 1;
        fclose(state->file); state->file = NULL; return;
    }
    state->written += amount;
    if (state->written == state->limit) {
        fclose(state->file); state->file = NULL; state->finished = 1;
        mark("done", "complete\n");
    }
}

SDL_AudioDeviceID SDL_OpenAudioDevice(const char *device, int recording,
        const SDL_AudioSpec *desired, SDL_AudioSpec *obtained, int changes) {
    typedef SDL_AudioDeviceID (*Function)(const char *, int, const SDL_AudioSpec *, SDL_AudioSpec *, int);
    Function original = (Function)dlsym(RTLD_NEXT, "SDL_OpenAudioDevice");
    if (!original) return 0;
    if (recording || !desired->callback || desired->callback == callback || !getenv("EXE_CAPTURE_DIR"))
        return original(device, recording, desired, obtained, changes);
    SDL_AudioSpec wrapped = *desired, actual;
    capture.callback = desired->callback; capture.userdata = desired->userdata;
    wrapped.callback = callback; wrapped.userdata = &capture;
    SDL_AudioDeviceID id = original(device, recording, &wrapped, &actual, changes);
    capture.spec = actual;
    if (obtained) *obtained = actual;
    return id;
}

int SDL_OpenAudio(SDL_AudioSpec *desired, SDL_AudioSpec *obtained) {
    typedef int (*Function)(SDL_AudioSpec *, SDL_AudioSpec *);
    Function original = (Function)dlsym(RTLD_NEXT, "SDL_OpenAudio");
    if (!original) return -1;
    if (!desired->callback || desired->callback == callback || !getenv("EXE_CAPTURE_DIR")) return original(desired, obtained);
    SDL_AudioSpec wrapped = *desired, actual;
    capture.callback = desired->callback; capture.userdata = desired->userdata;
    wrapped.callback = callback; wrapped.userdata = &capture;
    int result = original(&wrapped, &actual);
    capture.spec = actual;
    if (obtained) *obtained = actual;
    return result;
}
