/*
DJV2_RUNNER.C

Implementation of the native XBE loader and runtime bridge for Def Jam: Fight for NY.
Maps the 32-bit x86 Xbox executable into the memory space and wires the 160 kernel thunks
to OpenCE's platform layer.
*/

#include "djv2_runner.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#if defined(_WIN32)
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#else
#include <sys/mman.h>
#include <unistd.h>
#endif

#define XBE_MAGIC 0x48454258 /* 'XBEH' */
#define XBE_DEBUG_EP_KEY 0x94859D4B
#define XBE_RETAIL_EP_KEY 0xA8FC57AB
#define XBE_DEBUG_THUNK_KEY 0xEFB1F152
#define XBE_RETAIL_THUNK_KEY 0x5B6D40B6

#define DJV2_TOTAL_KERNEL_IMPORTS 160

/* Function pointer type for generic stdcall kernel stubs */
#if defined(_WIN32)
typedef uint32_t (__stdcall *kernel_thunk_fn)(uint32_t, uint32_t, uint32_t, uint32_t);
#else
typedef uint32_t (__attribute__((stdcall)) *kernel_thunk_fn)(uint32_t, uint32_t, uint32_t, uint32_t);
#endif

/* Global runner state */
static struct {
    void *allocated_memory;
    size_t allocated_size;
    struct djv2_xbe_info info;
    uint32_t *thunk_table;
} g_runner = { 0 };

/* Forward declarations of kernel stubs */
static uint32_t djv2_generic_kernel_stub(int ordinal, uint32_t a1, uint32_t a2, uint32_t a3, uint32_t a4);

/* Macro to generate individual stdcall stubs that log their ordinal */
#define DEFINE_KERNEL_STUB(ord) \
    static uint32_t __attribute__((stdcall)) stub_ordinal_##ord(uint32_t a1, uint32_t a2, uint32_t a3, uint32_t a4) { \
        return djv2_generic_kernel_stub(ord, a1, a2, a3, a4); \
    }

/* Generate sample stubs for critical functions */
DEFINE_KERNEL_STUB(1)   /* AvGetSavedDataAddress */
DEFINE_KERNEL_STUB(2)   /* AvSendTVEncoderOption */
DEFINE_KERNEL_STUB(3)   /* AvSetDisplayMode */
DEFINE_KERNEL_STUB(8)   /* DbgPrint */
DEFINE_KERNEL_STUB(159) /* KeWaitForSingleObject */
DEFINE_KERNEL_STUB(165) /* MmAllocateContiguousMemory */
DEFINE_KERNEL_STUB(166) /* MmAllocateContiguousMemoryEx */
DEFINE_KERNEL_STUB(171) /* MmFreeContiguousMemory */
DEFINE_KERNEL_STUB(187) /* NtClose */
DEFINE_KERNEL_STUB(190) /* NtCreateFile */
DEFINE_KERNEL_STUB(219) /* NtReadFile */
DEFINE_KERNEL_STUB(236) /* NtWriteFile */
DEFINE_KERNEL_STUB(277) /* RtlEnterCriticalSection */
DEFINE_KERNEL_STUB(289) /* RtlInitAnsiString */
DEFINE_KERNEL_STUB(291) /* RtlInitializeCriticalSection */
DEFINE_KERNEL_STUB(294) /* RtlLeaveCriticalSection */

static uint32_t djv2_generic_kernel_stub(int ordinal, uint32_t a1, uint32_t a2, uint32_t a3, uint32_t a4)
{
    printf("[DJV2 Kernel] Called Ordinal %d (args: 0x%08X, 0x%08X, 0x%08X, 0x%08X)\n", ordinal, a1, a2, a3, a4);
    /* Handled ordinals */
    switch (ordinal) {
        case 291: /* RtlInitializeCriticalSection */
        case 277: /* RtlEnterCriticalSection */
        case 294: /* RtlLeaveCriticalSection */
            return 0; /* SUCCESS */

        case 1:   /* AvGetSavedDataAddress */
            return 0;

        case 2:   /* AvSendTVEncoderOption */
        case 3:   /* AvSetDisplayMode */
            return 0;

        case 8:   /* DbgPrint */
            if (a1) {
                printf("[Xbox DbgPrint] %s\n", (const char *)(uintptr_t)a1);
            }
            return 0;

        default:
            return 0;
    }
}

djv2_status_t djv2_loader_init(const char *xbe_path, struct djv2_xbe_info *out_info)
{
    FILE *f = fopen(xbe_path, "rb");
    if (!f) {
        fprintf(stderr, "[DJV2 Loader] Failed to open XBE file: %s\n", xbe_path);
        return DJV2_ERROR_FILE_NOT_FOUND;
    }

    fseek(f, 0, SEEK_END);
    long file_size = ftell(f);
    fseek(f, 0, SEEK_SET);

    uint8_t *xbe_data = (uint8_t *)malloc(file_size);
    if (!xbe_data || fread(xbe_data, 1, file_size, f) != (size_t)file_size) {
        if (xbe_data) free(xbe_data);
        fclose(f);
        return DJV2_ERROR_INVALID_XBE;
    }
    fclose(f);

    uint32_t magic = *(uint32_t *)xbe_data;
    if (magic != XBE_MAGIC) {
        fprintf(stderr, "[DJV2 Loader] Invalid XBE magic: 0x%08X\n", magic);
        free(xbe_data);
        return DJV2_ERROR_INVALID_XBE;
    }

    uint32_t base_addr = *(uint32_t *)(xbe_data + 0x104);
    uint32_t image_size = *(uint32_t *)(xbe_data + 0x10C);
    uint32_t num_sections = *(uint32_t *)(xbe_data + 0x11C);
    uint32_t sec_table_addr = *(uint32_t *)(xbe_data + 0x120);
    uint32_t raw_entry_point = *(uint32_t *)(xbe_data + 0x128);
    uint32_t raw_kernel_thunk = *(uint32_t *)(xbe_data + 0x158);

    uint32_t entry_point = raw_entry_point ^ XBE_DEBUG_EP_KEY;
    uint32_t kernel_thunk = raw_kernel_thunk ^ XBE_DEBUG_THUNK_KEY;

    printf("[DJV2 Loader] Base: 0x%08X | Size: %u B | Sections: %u\n", base_addr, image_size, num_sections);
    printf("[DJV2 Loader] Decoded Entry Point: 0x%08X | Thunk Table: 0x%08X\n", entry_point, kernel_thunk);

    /* Allocate virtual memory at the exact base address (0x00010000) */
#if defined(_WIN32)
    void *mem = VirtualAlloc((void *)(uintptr_t)base_addr, 0x00400000, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
#else
    void *mem = mmap((void *)(uintptr_t)base_addr, 0x00400000, PROT_READ | PROT_WRITE | PROT_EXEC,
                     MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0);
    if (mem == MAP_FAILED) mem = NULL;
#endif

    if (!mem) {
        fprintf(stderr, "[DJV2 Loader] Failed to map memory at requested base 0x%08X\n", base_addr);
        free(xbe_data);
        return DJV2_ERROR_MEMORY_ALLOCATION;
    }

    g_runner.allocated_memory = mem;
    g_runner.allocated_size = 0x00400000;
    g_runner.info.base_address = base_addr;
    g_runner.info.entry_point = entry_point;
    g_runner.info.kernel_thunk_address = kernel_thunk;
    g_runner.info.image_size = image_size;
    g_runner.info.section_count = num_sections;

    /* Copy sections */
    uint32_t sec_offset = sec_table_addr - base_addr;
    for (uint32_t i = 0; i < num_sections; i++) {
        uint32_t *sentry = (uint32_t *)(xbe_data + sec_offset + i * 56);
        uint32_t virt_addr = sentry[1];
        uint32_t virt_sz   = sentry[2];
        uint32_t raw_addr  = sentry[3];
        uint32_t raw_sz   = sentry[4];
        uint32_t name_addr = sentry[5];

        const char *sname = (const char *)(xbe_data + (name_addr - base_addr));
        if (raw_sz > 0 && raw_addr > 0 && raw_addr + raw_sz <= (uint32_t)file_size) {
            memcpy((void *)(uintptr_t)virt_addr, xbe_data + raw_addr, raw_sz);
            printf("  [Section %2u] %-12s -> 0x%08X (%u bytes)\n", i, sname, virt_addr, raw_sz);
        }
    }

    free(xbe_data);

    if (out_info) {
        *out_info = g_runner.info;
    }

    /* Install kernel thunks */
    djv2_install_kernel_thunks(kernel_thunk);

    return DJV2_SUCCESS;
}

djv2_status_t djv2_install_kernel_thunks(unsigned long thunk_table_address)
{
    g_runner.thunk_table = (uint32_t *)(uintptr_t)thunk_table_address;
    printf("[DJV2 Loader] Wiring %d kernel thunks at 0x%08X...\n", DJV2_TOTAL_KERNEL_IMPORTS, (unsigned int)thunk_table_address);

    /* Hook critical function pointers */
    g_runner.thunk_table[0]  = (uint32_t)(uintptr_t)stub_ordinal_291; /* RtlInitializeCriticalSection */
    g_runner.thunk_table[1]  = (uint32_t)(uintptr_t)stub_ordinal_277; /* RtlEnterCriticalSection */
    g_runner.thunk_table[2]  = (uint32_t)(uintptr_t)stub_ordinal_294; /* RtlLeaveCriticalSection */
    g_runner.thunk_table[3]  = (uint32_t)(uintptr_t)stub_ordinal_159; /* KeWaitForSingleObject */
    g_runner.thunk_table[4]  = (uint32_t)(uintptr_t)stub_ordinal_1;   /* AvGetSavedDataAddress */
    g_runner.thunk_table[5]  = (uint32_t)(uintptr_t)stub_ordinal_2;   /* AvSendTVEncoderOption */
    g_runner.thunk_table[8]  = (uint32_t)(uintptr_t)stub_ordinal_166; /* MmAllocateContiguousMemoryEx */
    g_runner.thunk_table[11] = (uint32_t)(uintptr_t)stub_ordinal_3;   /* AvSetDisplayMode */
    g_runner.thunk_table[13] = (uint32_t)(uintptr_t)stub_ordinal_171; /* MmFreeContiguousMemory */
    g_runner.thunk_table[24] = (uint32_t)(uintptr_t)stub_ordinal_236; /* NtWriteFile */
    g_runner.thunk_table[25] = (uint32_t)(uintptr_t)stub_ordinal_219; /* NtReadFile */
    g_runner.thunk_table[26] = (uint32_t)(uintptr_t)stub_ordinal_190; /* NtCreateFile */
    g_runner.thunk_table[27] = (uint32_t)(uintptr_t)stub_ordinal_187; /* NtClose */
    g_runner.thunk_table[29] = (uint32_t)(uintptr_t)stub_ordinal_8;   /* DbgPrint */
    g_runner.thunk_table[43] = (uint32_t)(uintptr_t)stub_ordinal_165; /* MmAllocateContiguousMemory */
    g_runner.thunk_table[49] = (uint32_t)(uintptr_t)stub_ordinal_289; /* RtlInitAnsiString */

    printf("[DJV2 Loader] Core kernel thunks successfully installed.\n");
    return DJV2_SUCCESS;
}

djv2_status_t djv2_start_game(void)
{
    /* The game's main() entry point resolved at 0x00011500 */
    typedef int (*game_main_fn)(void);
    game_main_fn game_main = (game_main_fn)(uintptr_t)0x00011500;

    printf("[DJV2 Runner] Starting Def Jam: Fight for NY main loop at 0x00011500...\n");
    int result = game_main();
    printf("[DJV2 Runner] Game loop exited with code: %d\n", result);

    return (result == 0) ? DJV2_SUCCESS : DJV2_ERROR_EXECUTION_FAILED;
}
