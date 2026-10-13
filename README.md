# Def Jam: Fight for NY for Linux, Windows, Android and the Web (OpenFFNY)

> [!NOTE]
> **Proyecto basado en OpenCE:** Este proyecto es un port nativo multiplataforma en desarrollo de ***Def Jam: Fight for NY*** (versión original de Xbox). Está construido y adaptado directamente a partir de la arquitectura y la Capa de Abstracción de Plataforma (PAL) de [**OpenCE**](https://github.com/OpenCommunityEdition/OpenCE) (el port de la descompilación de *Halo: Combat Evolved* para Linux, Windows, Android y Web creado por el equipo de *OpenCommunityEdition*).

---

## 1. Acerca de este Proyecto

OpenFFNY tiene como objetivo llevar **Def Jam: Fight for NY** (desarrollado originalmente en 2004 por AKI Corporation y EA Canada para la consola Xbox original) a sistemas operativos modernos:
* **Linux** (ejecutable nativo x86 con OpenGL 4.5 y SDL3)
* **Windows** (ejecutable nativo x86 con OpenGL y SDL3)
* **Android** (arquitectura de invitado AArch64 ILP32 en app de 64 bits con OpenGL ES 3)
* **Web** (WebAssembly / WebGL 2 en el navegador con soporte de hilos y almacenamiento local)

### Base Técnica Reutilizada de OpenCE

El proyecto aprovecha la base de ingeniería de OpenCE:
* **Renderizador Direct3D 8 / GPU NV2A:** Traducción de registros de la GPU original de Xbox, shaders y texturas *swizzled* a OpenGL moderno (`port/linux/src/d3d8_gl.c`, `nv2a_psh.c`, `xbox_textures.c`).
* **Kernel y Memoria de Xbox:** Reimplementación limpia de llamadas al kernel NT de Xbox (`xboxkrnl.exe`), espacio de memoria física de 32 bits y archivos (`port/linux/src/xbox_kernel.c`, `xbox_memory.c`, `xbox_files.c`).
* **Audio y Mandos con SDL3:** Emulación de llamadas de DirectSound y soporte para múltiples mandos vía XInput sobre SDL3 (`dsound_sdl.c`, `xinput_sdl.c`).
* **Cabeceras limpias del XDK:** Declaraciones legales tipo *cleanroom* en `port/include/xdk/` sin requerir el SDK propietario de Microsoft.
* **Sistema de compilación Multiplataforma:** Automatización mediante Python y Ninja (`configure.py`) con soporte para PGO (Profile-Guided Optimization) y LTO (Link-Time Optimization).

---

## 2. Estado de la Ingeniería Inversa

Para consultar el registro técnico paso a paso, consulta [**`REGISTRO_DEF_JAM.md`**](REGISTRO_DEF_JAM.md).

### Resumen de descubrimientos clave:
* **Ejecutable `default.xbe` analizado:** Corresponde a una versión con configuración de desarrollo (**Debug Build**), con identificador `DJFFNY` (Title ID: `0x45410049`) y ruta de compilación original:
  ```text
  D:\djv2\Code\Game\xbox\Game
  ```
* **Aislamiento de Secciones:** El binario separa limpiamente el código del motor (`.text`, 2.0 MB) de las librerías del Xbox SDK (`D3D`, `D3DX`, `DSOUND`, `XPP`, `DOLBY`).
* **Cobertura del Kernel:** Se han identificado y resuelto el **100% de los 160 ordinales del Kernel** de Xbox importados por el juego.

---

## 3. Datos del Juego (Game Data)

Este repositorio **no contiene ni distribuye datos, modelos, audios ni binarios propietarios de EA o Microsoft**. 

Para utilizar el proyecto:
1. Dispón de una copia legítima en disco de *Def Jam: Fight for NY* para Xbox (`.iso`, `.bin` o `.xiso`).
2. Utiliza el script extractor para obtener los recursos del disco:
   ```bash
   python tools/extract_defjam.py "ruta/a/Def Jam.bin" "Def Jam - Fight for NY/extracted"
   ```
3. Para inspeccionar el encabezado y las secciones de `default.xbe`:
   ```bash
   python tools/parse_xbe.py
   ```

---

## 4. Compilación

El sistema de compilación se hereda directamente del framework de OpenCE:

1. Configurar el entorno de compilación:
   ```bash
   python configure.py
   ```
   *(Opciones: `--release`, `--portable`, `--profile`, etc.)*

2. Compilar para la plataforma deseada con [Ninja](https://ninja-build.org/):
   * **Linux:** `ninja linux`
   * **Windows:** `ninja windows`
   * **Android:** `ninja android_apk`
   * **Web:** `ninja web`

---

## 5. Créditos y Licencias

* **OpenCE:** Todo el reconocimiento a la comunidad y desarrolladores de [OpenCE (OpenCommunityEdition)](https://github.com/OpenCommunityEdition/OpenCE), cuya capa de plataforma, ingeniería inversa de Xbox y soporte multiplataforma hacen posible este proyecto.
* **Def Jam: Fight for NY:** Copyright (C) 2004 Electronic Arts Inc. y AKI Corporation. Def Jam y todas las marcas asociadas pertenecen a sus respectivos dueños.
* **Licencia del código de plataforma:** CC0 (Dominio Público) para el código del port y la capa de compatibilidad.
