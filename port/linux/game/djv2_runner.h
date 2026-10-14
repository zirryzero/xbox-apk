/*
DJV2_RUNNER.H

Native runner and section loader for Def Jam: Fight for NY (Xbox default.xbe).
Bridges the game's 32-bit x86 execution directly with OpenCE's platform layer.
*/

#ifndef DJV2_RUNNER_H
#define DJV2_RUNNER_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Status codes */
typedef enum djv2_status {
    DJV2_SUCCESS = 0,
    DJV2_ERROR_FILE_NOT_FOUND,
    DJV2_ERROR_INVALID_XBE,
    DJV2_ERROR_MEMORY_ALLOCATION,
    DJV2_ERROR_EXECUTION_FAILED
} djv2_status_t;

/* Information about the loaded game executable */
struct djv2_xbe_info {
    unsigned long base_address;
    unsigned long entry_point;
    unsigned long kernel_thunk_address;
    unsigned long image_size;
    int section_count;
};

/* Loads sections from default.xbe into the 32-bit virtual address space */
djv2_status_t djv2_loader_init(const char *xbe_path, struct djv2_xbe_info *out_info);

/* Installs and wires the 160 Xbox kernel import thunks to OpenCE's platform layer */
djv2_status_t djv2_install_kernel_thunks(unsigned long thunk_table_address);

/* Boots the game loop and executes main() (0x00011500) */
djv2_status_t djv2_start_game(void);

#ifdef __cplusplus
}
#endif

#endif /* DJV2_RUNNER_H */
