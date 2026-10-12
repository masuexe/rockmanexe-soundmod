// Thin streaming adapter around the unmodified agbplay MP2K core.
#include "MP2KContext.hpp"
#include "MP2KScanner.hpp"
#include "Debug.hpp"
#include <bit>
#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <string>

static_assert(sizeof(sample) == 8 && sizeof(float) == 4 && std::endian::native == std::endian::little,
              "The streaming protocol requires little-endian float32 stereo");

int main(int argc, char **argv) {
    try {
        if (argc != 6) throw std::runtime_error("Usage: exe-realtime ROM TABLE COUNT SONG SAMPLE_RATE");
        std::signal(SIGPIPE, SIG_DFL);
        Debug::set_callback([](const std::string &message, void *) { std::cerr << message << '\n'; }, nullptr);
        const size_t table = std::stoul(argv[2], nullptr, 0);
        const unsigned count = std::stoul(argv[3]), song = std::stoul(argv[4]), rate = std::stoul(argv[5]);
        if (rate < 22050 || rate > 96000 || count > 65535 || song >= count)
            throw std::runtime_error("Invalid song or output sample rate");
        Rom rom = Rom::LoadFromFile(argv[1]);
        MP2KScanner scanner(rom);
        const auto scans = scanner.Scan(nullptr);
        const MP2KScanner::Result *match = nullptr;
        for (const auto &result : scans) if (result.songTableInfo.pos == table) match = &result;
        if (!match || match->songTableInfo.count != count)
            throw std::runtime_error("agbplay could not verify this ROM's song/player table and sound mode");
        MP2KContext context(rate, -1, rom, match->mp2kSoundMode, AgbplaySoundMode{}, match->songTableInfo, match->playerTableInfo);
        context.m4aSongNumStart(static_cast<uint16_t>(song));
        // Run one block before publishing metadata so initialization errors are HTTP errors.
        context.m4aSoundMain();
        std::cout << "{\"sample_rate\":" << rate << ",\"channels\":2,\"format\":\"f32le\",\"engine\":\"agbplay\",\"song\":" << song << "}\n" << std::flush;
        do {
            const auto &buffer = context.masterAudioBuffer;
            if (std::fwrite(buffer.data(), sizeof(sample), buffer.size(), stdout) != buffer.size()) return 0;
            std::fflush(stdout);
            if (context.SongEnded()) break;
            context.m4aSoundMain();
        } while (true);
        return 0;
    } catch (const std::exception &error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
