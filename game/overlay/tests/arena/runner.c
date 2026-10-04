// Headless mGBA driver. All gameplay executes as ARM code in the compiled ROM.
#include <mgba/core/core.h>
#include <mgba/core/log.h>
#include <mgba/core/serialize.h>
#include <mgba-util/audio-buffer.h>
#include <mgba-util/vfs.h>
#include <fcntl.h>
#include <SDL2/SDL.h>
#include <sys/select.h>
#include <unistd.h>
#include <png.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static mColor pixels[240 * 160];
static SDL_Window *liveWindow;
static SDL_Renderer *liveRenderer;
static SDL_Texture *liveTexture;
static unsigned liveSpeed = 1;
static FILE *recordVideo, *recordAudio;
static unsigned recordedFrames;
static size_t recordedSamples;
static int16_t recordSamples[8192];

static void present(void)
{
    if (!liveWindow) return;
    SDL_UpdateTexture(liveTexture, NULL, pixels, 240 * sizeof(mColor));
    SDL_RenderClear(liveRenderer);
    SDL_RenderCopy(liveRenderer, liveTexture, NULL, NULL);
    SDL_RenderPresent(liveRenderer);
}

static void pump(void)
{
    if (!liveWindow) return;
    SDL_Event e;
    while (SDL_PollEvent(&e)) {
        if (e.type == SDL_QUIT) {
            SDL_DestroyTexture(liveTexture);
            SDL_DestroyRenderer(liveRenderer);
            SDL_DestroyWindow(liveWindow);
            liveWindow = NULL;
        }
    }
}

static void showLive(unsigned speed)
{
    liveSpeed = speed;
    if (!liveWindow) {
        SDL_Init(SDL_INIT_VIDEO);
        SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "0");
        liveWindow = SDL_CreateWindow("Esmeralda - LABORATORIO EN VIVO", SDL_WINDOWPOS_CENTERED,
            SDL_WINDOWPOS_CENTERED, 960, 640, SDL_WINDOW_SHOWN);
        liveRenderer = SDL_CreateRenderer(liveWindow, -1, SDL_RENDERER_ACCELERATED);
        liveTexture = SDL_CreateTexture(liveRenderer, SDL_PIXELFORMAT_ABGR8888,
            SDL_TEXTUREACCESS_STREAMING, 240, 160);
        SDL_SetTextureBlendMode(liveTexture, SDL_BLENDMODE_NONE);
    }
    SDL_RaiseWindow(liveWindow);
    present(); pump();
}

static void silentLog(struct mLogger *logger, int category, enum mLogLevel level, const char *format, va_list args) {}

static void screenshot(const char *path)
{
    FILE *f = fopen(path, "wb");
    png_structp p = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
    png_infop info = png_create_info_struct(p);
    unsigned char row[240 * 3];
    if (!f || !p || !info || setjmp(png_jmpbuf(p))) exit(3);
    png_init_io(p, f);
    png_set_IHDR(p, info, 240, 160, 8, PNG_COLOR_TYPE_RGB, PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT);
    png_write_info(p, info);
    for (int y = 0; y < 160; y++) {
        for (int x = 0; x < 240; x++) {
            unsigned c = pixels[y * 240 + x];
            row[x * 3] = c; row[x * 3 + 1] = c >> 8; row[x * 3 + 2] = c >> 16;
        }
        png_write_row(p, row);
    }
    png_write_end(p, info); png_destroy_write_struct(&p, &info); fclose(f);
}

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    struct mLogger logger = {.log = silentLog};
    mLogSetDefaultLogger(&logger);
    struct mCore *core = mCoreFind(argv[1]);
    if (!core || !core->init(core)) return 3;
    mCoreInitConfig(core, NULL);
    mCoreConfigSetDefaultIntValue(&core->config, "useBios", 0);
    mCoreConfigSetDefaultIntValue(&core->config, "skipBios", 1);
    mCoreConfigSetDefaultIntValue(&core->config, "volume", 0);
    mCoreLoadConfig(core);
    core->setVideoBuffer(core, pixels, 240);
    core->setAudioBufferSize(core, 4096);
    if (!mCoreLoadFile(core, argv[1])) return 4;
    core->reset(core);
    char line[4096], command[40], path[2048];
    unsigned a, b, n;
    setvbuf(stdin, NULL, _IONBF, 0);
    puts("ready"); fflush(stdout);
    for (;;) {
        pump();
        fd_set ready; FD_ZERO(&ready); FD_SET(STDIN_FILENO, &ready);
        struct timeval delay = {0, 20000};
        if (select(STDIN_FILENO + 1, &ready, NULL, NULL, &delay) <= 0) continue;
        if (!fgets(line, sizeof(line), stdin)) break;
        if (sscanf(line, "%39s", command) != 1) continue;
        if (!strcmp(command, "frame")) {
            sscanf(line, "%*s %u %u", &n, &a); core->setKeys(core, a);
            for (unsigned i = 0; i < n; i++) {
                unsigned began = SDL_GetTicks();
                core->runFrame(core);
                if (recordVideo) {
                    struct mAudioBuffer *audio=core->getAudioBuffer(core);
                    size_t count=mAudioBufferRead(audio,recordSamples,4096);
                    if(fwrite(pixels,sizeof(mColor),240*160,recordVideo)!=240*160
                        ||fwrite(recordSamples,4,count,recordAudio)!=count) return 8;
                    recordedFrames++;recordedSamples+=count;
                }
                if (liveWindow) {
                    if (!liveSpeed || i % liveSpeed == 0) present();
                    pump();
                    unsigned duration = liveSpeed ? 1000 / (60 * liveSpeed) : 0;
                    unsigned used = SDL_GetTicks() - began;
                    if (duration > used) SDL_Delay(duration - used);
                }
            }
            puts("ok");
        } else if (!strcmp(command, "record")) {
            char videoPath[2048],audioPath[2048];
            if(recordVideo||sscanf(line,"%*s %2047s %2047s",videoPath,audioPath)!=2)return 8;
            recordVideo=fopen(videoPath,"wx");recordAudio=fopen(audioPath,"wx");
            if(!recordVideo||!recordAudio)return 8;
            mCoreConfigSetDefaultIntValue(&core->config,"volume",256);
            mCoreLoadConfig(core);mAudioBufferClear(core->getAudioBuffer(core));
            recordedFrames=0;recordedSamples=0;puts("ok");
        } else if (!strcmp(command, "record_stop")) {
            if(!recordVideo)return 8;
            fclose(recordVideo);fclose(recordAudio);recordVideo=recordAudio=NULL;
            printf("{\"frames\":%u,\"frequency\":%d,\"frame_cycles\":%d,\"sample_rate\":%u,\"stereo_samples\":%zu,\"duration\":%.6f}\n",
                recordedFrames,core->frequency(core),core->frameCycles(core),core->audioSampleRate(core),recordedSamples,
                (double)recordedFrames*core->frameCycles(core)/core->frequency(core));
        } else if (!strcmp(command, "view")) {
            sscanf(line, "%*s %u", &a); showLive(a); puts("ok");
        } else if (!strcmp(command, "read")) {
            sscanf(line, "%*s %x %u", &a, &n);
            for (unsigned i = 0; i < n; i++) printf("%02x", core->busRead8(core, a + i));
            puts("");
        } else if (!strcmp(command, "reset")) {
            core->reset(core); puts("ok");
        } else if (!strcmp(command, "write32")) {
            sscanf(line, "%*s %x %x", &a, &b); core->busWrite32(core, a, b); puts("ok");
        } else if (!strcmp(command, "write16")) {
            sscanf(line, "%*s %x %x", &a, &b); core->busWrite16(core, a, b); puts("ok");
        } else if (!strcmp(command, "write8")) {
            sscanf(line, "%*s %x %x", &a, &b); core->busWrite8(core, a, b); puts("ok");
        } else if (!strcmp(command, "screenshot")) {
            sscanf(line, "%*s %2047s", path); screenshot(path); puts("ok");
        } else if (!strcmp(command, "save")) {
            sscanf(line, "%*s %2047s", path);
            void *data; size_t size = core->savedataClone(core, &data);
            FILE *f = fopen(path, "wb"); if (!f) return 5;
            fwrite(data, 1, size, f); fclose(f); free(data); puts("ok");
        } else if (!strcmp(command, "loadsave")) {
            sscanf(line, "%*s %2047s", path);
            puts(mCoreLoadSaveFile(core, path, true) ? "ok" : "failed"); core->reset(core);
        } else if (!strcmp(command, "state")) {
            sscanf(line, "%*s %2047s", path);
            struct VFile *vf = VFileOpen(path, O_WRONLY | O_CREAT | O_TRUNC);
            if (!vf) { puts("failed"); } else {
                puts(mCoreSaveStateNamed(core, vf, SAVESTATE_ALL) ? "ok" : "failed");
                vf->close(vf);
            }
        } else if (!strcmp(command, "loadstate")) {
            sscanf(line, "%*s %2047s", path);
            struct VFile *vf = VFileOpen(path, O_RDONLY);
            if (!vf) { puts("failed"); } else {
                puts(mCoreLoadStateNamed(core, vf, SAVESTATE_ALL) ? "ok" : "failed");
                vf->close(vf);
                present();
            }
        } else if (!strcmp(command, "quit")) break;
        else puts("unknown command");
        fflush(stdout);
    }
    if(recordVideo){fclose(recordVideo);fclose(recordAudio);}
    core->deinit(core);
    return 0;
}
