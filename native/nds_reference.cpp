// Optional research renderer linked with the public kode54/SSEQPlayer core.
// This produces a software DS reference, not an emulator/hardware recording.
#include <algorithm>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>
#include "SDAT.h"
#include "Player.h"

// Instrumentation hooks installed only in the disposable reference build.
unsigned researchSequenceClock = 0;
unsigned researchTimerClock = 0;
static std::ofstream noteLog;
static std::ofstream controlLog;
static std::ofstream modulationLog;
void researchModulation(const Channel& channel, int value) {
    if (channel.trackId < 0) return;
    modulationLog << researchTimerClock - 1 << ',' << researchSequenceClock << ','
                  << static_cast<unsigned>(channel.ply->tracks[channel.trackId].num) << ','
                  << (&channel - &channel.ply->channels[0]) << ',' << static_cast<unsigned>(channel.key) << ','
                  << static_cast<unsigned>(channel.modType) << ','
                  << static_cast<unsigned>(channel.modSpeed) << ','
                  << static_cast<unsigned>(channel.modDepth) << ','
                  << static_cast<unsigned>(channel.modRange) << ','
                  << channel.modCounter << ',' << value << '\n';
}
void researchNote(const Track& track, int key, int velocity, int duration) {
    noteLog << researchSequenceClock - 1 << ',' << static_cast<unsigned>(track.num)
            << ',' << track.patch << ',' << key << ',' << velocity << ',' << duration << '\n';
}

void researchControl(const Track& track, int opcode, int value) {
    unsigned held = 0, releasing = 0;
    for (const auto& channel : track.ply->channels) {
        if (channel.trackId != track.trackId || channel.state == CS_NONE) continue;
        if (channel.state == CS_RELEASE) ++releasing;
        else ++held;
    }
    controlLog << researchSequenceClock - 1 << ',' << static_cast<unsigned>(track.num)
               << ',' << opcode << ',' << value << ',' << held << ',' << releasing << '\n';
}

static void write16(std::ostream& out, int value) {
    out.put(static_cast<char>(value & 255));
    out.put(static_cast<char>((value >> 8) & 255));
}

int main(int argc, char** argv) {
    try {
        if (argc != 5)
            throw std::runtime_error("usage: nds-reference validated.sdat sseq-id seconds output-directory");
        std::ifstream input(argv[1], std::ios::binary);
        if (!input) throw std::runtime_error("cannot read SDAT");
        std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(input)), {});
        if (bytes.size() < 64) throw std::runtime_error("short SDAT");
        PseudoFile file;
        file.data = &bytes;
        SDAT sdat(file, std::stoul(argv[2]));
        const unsigned seconds = std::stoul(argv[3]);
        if (!seconds || seconds > 180) throw std::runtime_error("duration must be 1..180");
        const std::string directory(argv[4]); // caller creates a fresh directory
        noteLog.open(directory + "/notes.csv");
        if (!noteLog) throw std::runtime_error("cannot create reference note log");
        noteLog << "tick,track,instrument,key,velocity,duration\n";
        controlLog.open(directory + "/controls.csv");
        if (!controlLog) throw std::runtime_error("cannot create reference control log");
        controlLog << "tick,track,opcode,value,held_voices,release_voices\n";
        modulationLog.open(directory + "/modulation.csv");
        if (!modulationLog) throw std::runtime_error("cannot create modulation log");
        modulationLog << "timer_frame,tick,track,channel,key,type,speed,depth,range,phase,value\n";
        Player player;
        player.sampleRate = 44100;
        player.interpolation = INTERPOLATION_NONE;
        player.prio = 0;
        player.sseqVol = Cnv_Sust(sdat.sseq->info.vol);
        if (!player.Setup(sdat.sseq.get())) throw std::runtime_error("player setup failed");
        std::ofstream audio(directory + "/source.pcm", std::ios::binary);
        if (!audio) throw std::runtime_error("cannot create reference PCM");
        std::vector<uint8_t> buffer(4410 * 4);
        int peak = 0;
        unsigned clipped = 0, maxVoices = 0;
        for (unsigned part = 0; part < seconds * 10; ++part) {
            player.GenerateSamples(buffer, 0, 4410);
            audio.write(reinterpret_cast<const char*>(buffer.data()), buffer.size());
            for (size_t i = 0; i < buffer.size(); i += 2) {
                int sample = static_cast<int16_t>(buffer[i] | (buffer[i + 1] << 8));
                peak = std::max(peak, std::abs(sample));
                clipped += sample == -32768 || sample == 32767;
            }
            unsigned voices = 0;
            for (const auto& channel : player.channels) voices += channel.state != CS_NONE;
            maxVoices = std::max(maxVoices, voices);
        }
        // Independent decoder output for exact comparison with Python ADPCM.
        for (unsigned slot = 0; slot < 4; ++slot) {
            if (!sdat.swar[slot]) continue;
            for (const auto& pair : sdat.swar[slot]->swavs) {
                std::ofstream wave(directory + "/wave-" + std::to_string(slot) + "-"
                                   + std::to_string(pair.first) + ".pcm16", std::ios::binary);
                if (!wave) throw std::runtime_error("cannot create decoded wave");
                for (int16_t sample : pair.second.data) write16(wave, sample);
            }
        }
        std::ofstream metadata(directory + "/reference.json");
        metadata << "{\"renderer\":\"kode54/SSEQPlayer\",\"capture\":\"software DS reference\","
                 << "\"sample_rate\":44100,\"channels\":2,\"seconds\":" << seconds
                 << ",\"peak\":" << peak << ",\"clipped_samples\":" << clipped
                 << ",\"max_voices_at_100ms_intervals\":" << maxVoices << "}\n";
        std::cout << seconds << " seconds; peak " << peak << "; coarse maximum voices " << maxVoices << '\n';
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
