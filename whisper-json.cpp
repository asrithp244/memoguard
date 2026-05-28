#include "whisper.h"
#include <cstdio>
#include <string>
#include <vector>

int main(int argc, char ** argv) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <model> <wav>\n", argv[0]);
        return 1;
    }

    const char * model_path = argv[1];
    const char * wav_path   = argv[2];

    struct whisper_context_params cparams = whisper_context_default_params();
    struct whisper_context * ctx = whisper_init_from_file_with_params(model_path, cparams);
    if (!ctx) { fprintf(stderr, "Failed to load model\n"); return 1; }

    struct whisper_full_params params = whisper_full_default_params(WHISPER_SAMPLING_GREEDY);
    params.print_progress   = false;
    params.print_special    = false;
    params.print_realtime   = false;
    params.print_timestamps = false;
    params.language         = "en";
    params.n_threads        = 4;

    FILE * f = fopen(wav_path, "rb");
    if (!f) { fprintf(stderr, "Failed to open WAV\n"); return 1; }
    fseek(f, 44, SEEK_SET);
    std::vector<float> pcm;
    short sample;
    while (fread(&sample, 2, 1, f) == 1)
        pcm.push_back(sample / 32768.0f);
    fclose(f);

    if (whisper_full(ctx, params, pcm.data(), (int)pcm.size()) != 0) {
        fprintf(stderr, "Inference failed\n"); return 1;
    }

    std::string text;
    int n = whisper_full_n_segments(ctx);
    for (int i = 0; i < n; i++) text += whisper_full_get_segment_text(ctx, i);
    if (!text.empty() && text[0] == ' ') text = text.substr(1);

    printf("{\"text\": \"%s\"}\n", text.c_str());
    whisper_free(ctx);
    return 0;
}
