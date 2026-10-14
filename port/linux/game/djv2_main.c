/*
DJV2_MAIN.C

Standalone entry point for the Def Jam: Fight for NY native port (OpenFFNY).
Initializes platform services, loads default.xbe into memory, and launches the game loop.
*/

#include "djv2_runner.h"

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    printf("=====================================================\n");
    printf("  OpenFFNY: Def Jam Fight for NY Native Source Port  \n");
    printf("  Based on OpenCE (Halo: Combat Evolved Platform)    \n");
    printf("=====================================================\n\n");

    const char *xbe_path = "Def Jam - Fight for NY/extracted/default.xbe";
    if (argc > 1) {
        xbe_path = argv[1];
    }

    printf("[OpenFFNY] Loading XBE from: %s\n", xbe_path);

    struct djv2_xbe_info info;
    djv2_status_t status = djv2_loader_init(xbe_path, &info);
    if (status != DJV2_SUCCESS) {
        fprintf(stderr, "[OpenFFNY] Failed to initialize XBE loader (error code: %d)\n", status);
        return EXIT_FAILURE;
    }

    printf("[OpenFFNY] Initializing game execution...\n");
    status = djv2_start_game();

    printf("[OpenFFNY] Execution finished with status: %d\n", status);
    return (status == DJV2_SUCCESS) ? EXIT_SUCCESS : EXIT_FAILURE;
}
