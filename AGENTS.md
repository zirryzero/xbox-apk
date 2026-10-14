# Instrucciones para agentes de OpenFFNY

## Objetivo y estado del proyecto

Este repositorio desarrolla **OpenFFNY**, un port de **Def Jam: Fight for NY**
para Xbox a Linux, Windows, Android y web. Reutiliza la arquitectura y la
capa de abstracción de plataforma (PAL) de
[OpenCE](https://github.com/OpenCommunityEdition/OpenCE), el port de la
descompilación de Halo: Combat Evolved. Mantener el crédito y la procedencia
de esa base.

Empezar por [README.md](README.md) y
[REGISTRO_DEF_JAM.md](REGISTRO_DEF_JAM.md). Contrastarlos con el código:
las notas de investigación pueden describir hipótesis o trabajo pendiente.

El estado actual es:

- `source/` contiene el código reconstruido de Halo, no el motor AKI de
  Def Jam. `port/linux/game/` contiene extensiones específicas de Halo.
- Los objetivos Ninja y los artefactos existentes todavía corresponden a
  Halo. Compilarlos comprueba la base heredada; no demuestra que Def Jam
  arranque o funcione.
- El trabajo propio de Def Jam está en `tools/extract_defjam.py`,
  `tools/parse_xbe.py`, `tools/unpack_viv.py`, `tools/parse_shpx.py`
  y el registro de investigación. Son herramientas iniciales, con
  validaciones y cobertura de formatos pendientes.
- El cargador, la ejecución del motor y su integración con la PAL siguen
  pendientes. La PAL implementa las APIs que utiliza Halo; su compatibilidad
  con otro juego debe comprobarse función por función.
- Hay archivos extraídos del juego ya rastreados bajo
  `Def Jam - Fight for NY/extracted/`. Esto es una deuda existente:
  estas reglas no significan que se hayan retirado del repositorio.

Actualizar esta descripción cuando cambie la implementación. Distinguir
siempre los objetivos del proyecto de las capacidades verificadas.

## Prioridades de desarrollo

1. Hacer reproducibles y seguras las herramientas de investigación y
   documentar sus dependencias y límites.
2. Documentar la estrategia de ejecución de Def Jam: reconstrucción y
   recompilación de código, ejecución del binario o una combinación
   justificada. Identificar qué resuelve cada componente de la PAL.
3. Conseguir un arranque mínimo comprobable en una plataforma, con
   diagnóstico de las llamadas pendientes.
4. Integrar progresivamente recursos, renderizado, audio, entrada y lógica
   del juego, comprobando cada subsistema.
5. Llevar esa integración a las otras plataformas y preparar su distribución.

Estos pasos orientan el trabajo; una tarea concreta puede abordar un
subsistema o plataforma en paralelo. No declarar un port jugable por haber
extraído recursos, localizado `main()` o abierto una ventana con SDL.

El XBE original contiene instrucciones x86. El invitado Android heredado
ejecuta AArch64 ILP32 y la web ejecuta WebAssembly. Cargar las secciones del
XBE o sustituir sus importaciones no traduce esas instrucciones. Cualquier
estrategia debe explicar cómo se ejecutará el código en cada destino.
Documentar también la carga de secciones y BSS, las importaciones del kernel,
las funciones del SDK enlazadas estáticamente, TLS, pila y convenciones de
llamada que necesite esa estrategia.

## Organización

| Ruta | Contenido y alcance |
| --- | --- |
| `source/` | Descompilación heredada de Halo y sus dependencias |
| `port/linux/src/` | PAL compartida: Direct3D 8 sobre OpenGL, DirectSound y XInput sobre SDL3, archivos, memoria, hilos, configuración y transporte; también conserva adaptaciones de Halo |
| `port/linux/game/` | Código específico de Halo: menús, netcode, co-op, mapas Custom Edition, validadores y controles |
| `port/linux/include/` | Cabeceras, límites, capacidades y ajustes de compilación heredados |
| `port/include/xdk/` | Declaraciones propias de las APIs Xbox, sin cabeceras del SDK propietario |
| `port/windows/` | Adaptación de Windows |
| `port/android/` | Invitado AArch64 ILP32, biblioteca anfitriona, aplicación Java y puentes de llamadas |
| `port/web/` | Runtime wasm32, WebGL 2, página, almacenamiento, service worker y pruebas |
| `port/assets/` | Recursos redistribuibles del port; conservar procedencia y licencias |
| `port/third_party/` | Dependencias vendorizadas con su documentación |
| `tools/` | Compilación, generadores, herramientas de Def Jam y pruebas |
| `docs/` | Diseños y documentación de formatos |
| `REGISTRO_DEF_JAM.md` | Evidencia, hipótesis, avances y pendientes de Def Jam |
| `Def Jam - Fight for NY/` y `assets/` | Datos locales del usuario; no añadir material extraído a Git |
| `pgo/` | Perfiles de optimización heredados; no asumir que representan Def Jam |
| `.github/workflows/` | CI y publicación heredadas; revisar su alcance al adaptar el port |

Ubicar el nuevo código específico de Def Jam en una ruta propia y
documentada. Integrarlo explícitamente en el sistema de compilación.
Reutilizar la PAL cuando corresponda y separar sus dependencias de Halo
sin hacer renombrados masivos ni eliminar la base de referencia como efecto
secundario de otra tarea.

## Ingeniería inversa y documentación

- Registrar la herramienta, el comando y la identificación de la muestra
  (tamaño, hash y versión cuando se conozca) de los resultados importantes.
  No incluir el binario ni fragmentos de recursos propietarios como evidencia.
- Separar hechos observados, hipótesis e implementaciones comprobadas.
  Las direcciones y nombres deducidos deben indicar su procedencia.
- Distinguir identificación de ordinales, declaración de una API,
  implementación, stub y comportamiento verificado. Documentar por
  importación su nombre, implementación, limitaciones y pruebas.
- Un stub debe dejar constancia de la llamada y de su resultado limitado.
  No contar un retorno fijo o una función vacía como compatibilidad completa.
- Declarar porcentajes de cobertura solo con un inventario reproducible
  y criterios explícitos. Identificar los 160 ordinales no equivale a
  implementar sus ABI ni sus comportamientos.
- Las claves de desarrollo de un XBE no prueban por sí solas que incluya
  símbolos completos o carezca de optimizaciones.
- Afirmar soporte únicamente para formatos, variantes y plataformas
  comprobados; etiquetar como hipótesis o pendientes los demás.
  Actualizar las afirmaciones relacionadas cuando una prueba revele un límite.

## Datos del juego, SDK y licencias

- Los discos, XBE, paquetes VIV, videos, texturas, modelos, audio, fuentes,
  XML y scripts extraídos del juego son datos locales. No añadirlos a
  commits, fixtures, artefactos de CI ni distribuciones.
- Usar una copia del usuario para análisis local. Mantener las nuevas
  extracciones en una ruta ignorada o fuera del repositorio y comprobar
  `git status` y el contenido de los archivos preparados para commit.
- Un archivo de texto extraído sigue siendo un recurso del juego.
  `.gitignore` no retira archivos ya rastreados ni borra el historial.
  Tratar cualquier limpieza de esos archivos como una tarea explícita,
  conservando las copias locales del usuario.
- No leer `xbox/include`, las cabeceras del SDK propietario ni copias
  derivadas de ellas. No copiarlas al proyecto.
  `port/include/xdk/` se mantiene con información de depuración permitida,
  documentación pública y observaciones del juego. Para añadir declaraciones,
  seguir [port/include/xdk/README.md](port/include/xdk/README.md);
  no asumir que las declaraciones de Halo cubren el XDK usado por Def Jam.
- El código propio del port conserva la licencia CC0 del repositorio.
  Esta licencia no se aplica a los recursos del juego ni sustituye las
  licencias de terceros.
- El código vendorizado va en `port/third_party/<nombre>/`, sin modificaciones,
  con un README que indique upstream, versión o commit, checksum, licencia
  y uso. Declarar también las dependencias Python, como `pyBIG`, y cómo
  instalarlas; no depender de paquetes presentes solo en una máquina.
- Conservar avisos y créditos de OpenCE y de las dependencias.
  No copiar código GPL al port; puede consultarse como documentación de
  formatos, manteniendo clara la procedencia.
- Usar arte y fuentes redistribuibles con procedencia documentada.
  No distribuir las fuentes comerciales extraídas del juego.
  Para recursos heredados consultar los README de menús y fuentes;
  `AUTHORS.md` mantiene los créditos de arte.

## Lectores, extractores y formatos

Todos los discos, ejecutables y recursos son entrada no confiable.

- Validar firmas, tamaños, contadores, offsets, rangos, terminadores y
  longitudes de lectura antes de utilizarlos. Comprobar rangos en el archivo
  y en la imagen virtual según corresponda.
- Respetar los límites del directorio y del contenedor. Rechazar datos
  truncados y formatos no soportados con un error claro; no informar éxito
  después de una lectura incompleta.
- Limitar memoria, tamaño descomprimido, número de entradas y profundidad.
  Detectar ciclos en árboles y referencias de directorios.
- Rechazar rutas absolutas, componentes `..`, prefijos de unidad y nombres
  que permitan salir del destino en Windows o POSIX. Comprobar que el destino
  resuelto permanezca dentro de la raíz, también frente a enlaces.
- Validar antes de crear o sobrescribir archivos. Hacer explícita la política
  de sobrescritura y no modificar la imagen de origen.
- En texturas, comprobar dimensiones rectangulares, organización swizzled
  o lineal, formato de píxel, canales, transparencia y tamaños de paleta.
  No sustituir índices inválidos por píxeles aparentemente válidos.
- Las herramientas deben aceptar rutas por argumentos, funcionar con
  espacios en los nombres y devolver un código de salida distinto de cero
  ante errores. Documentar dependencias y formatos realmente soportados.

## Código y compatibilidad de la base heredada

- Cambiar `source/` solo cuando la tarea lo necesite. Marcar cada cambio
  respecto de la descompilación original con un comentario que empiece
  `port:`, incluyendo correcciones de bugs originales.
- Seguir nombres, estilo y densidad de comentarios del código circundante.
  Declarar las funciones que llama el código heredado en
  `halo_linux_source_fixups.h` o incluir su cabecera con una nota que indique
  el archivo de implementación.
- El C heredado se compila como `gnu89`: declaraciones antes de sentencias.
  El C++ nuevo debe documentar sus requisitos de ABI y runtime y contar
  con soporte explícito en los destinos que lo compilen.
- Conservar las convenciones de llamada, layouts, tamaños y alineaciones
  requeridos por la PAL. No convertir punteros de 32 bits a 64 bits sin
  analizar los formatos y puentes que dependen de ellos.
- Mantener la matemática vendorizada (`halo_math.h`) y la compilación sin
  fused multiply-add en el código que las utiliza. No sustituirlas por
  matemáticas del sistema. Un cambio numérico requiere comprobar sus efectos.
- Los nombres `HALO_*`, `halo_*` y los artefactos `halo*` son identificadores
  heredados, no pruebas de compatibilidad con Def Jam. Cambiarlos solo
  dentro de una migración coherente de sus referencias.
- Las reglas de menús Halo Custom Edition, mapas CE y OpenSauce se aplican
  al código de Halo conservado. La interfaz y los recursos nuevos deben
  responder a Def Jam. Si se cambian los XML generados de Halo, modificar
  su generador (`tools/ce_menus.py` o `tools/port_settings.py`) y regenerar;
  no editarlos a mano. Conservar los redibujados y las excepciones documentadas
  en `NON_HANDDRAWN.md`, y las fuentes Overpass y OpenCE de esa interfaz.
  La compatibilidad de mapas heredada no debe añadir funciones OpenSauce;
  sus lectores siguen sujetos a validación de límites.
- Al modificar el netcode heredado, leer `port/linux/NETCODE.md`, conservar
  la autoridad del host e incrementar `HALO_PORT_NETWORK_VERSION` si cambia
  el protocolo o algo en lo que deban coincidir los participantes.
  Comprobar transporte nativo y web, con validación de tamaños, índices y
  tasas. Su existencia no significa que Def Jam tenga multijugador integrado.
- Una opción nueva de la PAL se declara en `port/linux/src/port_config.c`
  con valor predeterminado, variable de entorno y descripción.
  Documentarla en el README correspondiente. Mantener el comportamiento
  original del juego por defecto cuando exista una implementación comprobada.

## Compilación

Estos comandos corresponden a la **base heredada de Halo** hasta que se
introduzca y documente un objetivo específico de Def Jam:

```sh
python configure.py
ninja linux
ninja windows
ninja android
ninja android_apk
ninja web
python tools/ci_build.py linux release
```

- `configure.py` escribe `build.ninja`. Conservar las opciones anteriores
  (`configure_args`) al probar otras configuraciones. Las opciones incluyen
  `--release`, `--portable`, `--profile`, `--pgo=off` y `--lto=off`.
- Linux y Windows usan x86 de 32 bits, clang y ABI compatible con MSVC
  (`-fms-extensions -fshort-wchar -malign-double -fcommon`).
  El objetivo Windows se compila en Windows.
- Android usa un invitado `arm64_32` en una aplicación de 64 bits.
  Solo puede llamar a las importaciones de `port/android/host_imports.list`
  y `port/android/guest/runtime/guest_host.h`, y a las funciones SDL
  que puentea `guest_sdl.c`.
- Web usa `wasm32`, un Worker y WebGL 2/OpenGL ES 3.0. Los tipos de las
  llamadas deben coincidir exactamente con los de sus destinos.
- Al cambiar código compartido o su compilación, comprobar los destinos
  afectados. Ejecutar `ninja android` y `ninja web` cuando cambie código que
  compilan, si sus toolchains están disponibles; informar las comprobaciones
  pendientes cuando falten.
- Conservar los defines existentes: `HALO_ANDROID`, `HALO_GLES`,
  `HALO_ARM64_GUEST`, `HALO_WEB`, `HALO_WINDOWS`, `HALO_RELEASE` y
  `HALO_PROFILE`. `HALO_LINUX` y `HALO_CUSTOM_EDITION` no están definidos
  en las builds heredadas. No asumir que una guarda nueva queda activa.
  La instrumentación bajo `HALO_PROFILE` no debe alterar las builds normales.

## Pruebas y ejecución

Los lectores y el código nuevo de Def Jam deben tener pruebas reproducibles
sin datos comerciales. Usar fixtures sintéticas para archivos válidos
mínimos, truncamientos, rangos inválidos, ciclos, rutas externas y errores
de descompresión. En texturas, comprobar dimensiones rectangulares, canales
y alfa. Probar resultados observables; evitar pruebas que solo repitan la
implementación.

Las pruebas existentes verifican principalmente Halo y la PAL heredada:

```sh
python -m pytest -q tools/harness tools/test_touch_menu.py
python -m pytest -q tools/test_linux_port.py
python -m pytest -q tools/test_cache_file_formats.py tools/test_bmp_files.py tools/test_profile.py
python tools/test_touch_layout.py
python tools/test_light_storage.py
python tools/test_death_timing.py
python -m pytest -q tools/test_web_build.py
node --test "port/web/tests/*.test.js"
node port/web/tests/webrtc_native.mjs chromium firefox
```

- `tools/harness/README.md` explica las pruebas que extraen funciones reales
  y sus controles negativos. Necesitan compilador C y runtime de 32 bits.
  Algunas pruebas de integración requieren mapas locales o toolchains.
- Las pruebas de herramientas deben tolerar las rutas de Windows y POSIX.
  Integrar las pruebas nuevas en CI sin descargar ni publicar datos del juego.
- Informar qué se ejecutó, qué pasó, qué falló y qué se omitió, con sus
  requisitos pendientes. Una prueba de Halo aprobada no valida Def Jam.
- Para cambios solo de documentación, revisar el diff, los enlaces y los
  comandos es suficiente; no hace falta recompilar el juego.
- No ejecutar juegos en el escritorio del usuario para pruebas automáticas.
  Usar un display virtual como Xvfb cuando corresponda, o ejecución oculta
  y sin renderizado si la implementación la admite. Detener únicamente los
  procesos iniciados para la tarea.
- `HALO_NETWORK_TEST`, `HALO_NET_ADDRESS`, `HALO_NET_BROADCAST` y
  `debug.exit_after`, `debug.hidden_window`, `debug.null_renderer`,
  `debug.menu_open` y `debug.telnet_console` son mecanismos de Halo.
  Documentar los mecanismos equivalentes cuando se implementen en Def Jam.

## Identidad, distribución y contribuciones

- Antes de distribuir OpenFFNY, adaptar de forma consistente nombres de
  artefactos, identificador Android, actualizadores, enlaces web, servicios
  de informes y configuración de CI. Los actuales todavía conservan la
  identidad y varios endpoints de OpenCE.
- Las actualizaciones de OpenFFNY deben usar sus propios artefactos y
  versiones. No publicar un paquete Def Jam que descargue actualizaciones
  de Halo. Comprobar el contenido de releases y del sitio.
- Mantener este documento, README y registro alineados con los avances
  comprobados. No marcar un hito como terminado por compilar un stub.
- Los commits describen lo que cambió; el cuerpo explica el motivo y las
  comprobaciones. Limitar los cambios al alcance de la tarea.
- Los PR se integran con merge commit. Los ajustes posteriores conservan
  commits separados con referencia al PR.
- Conservar autoría al incorporar commits de otro repositorio mediante
  `git cherry-pick -x`.

## Documentos de referencia

Los documentos de plataformas y juego de OpenCE describen la base heredada.
Comprobar su vigencia para Def Jam antes de usarlos como requisitos.

| Documento | Alcance |
| --- | --- |
| [README.md](README.md) | Objetivo y presentación de OpenFFNY |
| [REGISTRO_DEF_JAM.md](REGISTRO_DEF_JAM.md) | Investigación de XBE, motor y recursos de Def Jam |
| [port/linux/README.md](port/linux/README.md) | PAL, compilación, configuración y funcionamiento de Halo |
| [port/linux/NETCODE.md](port/linux/NETCODE.md) | Protocolo y pruebas de red heredados |
| [port/windows/README.md](port/windows/README.md) | ABI, compilación e informes de fallos de Windows |
| [port/android/README.md](port/android/README.md) | Invitado, anfitrión, importaciones, controles y diagnóstico |
| [port/web/README.md](port/web/README.md) | WebAssembly, WebGL, almacenamiento y alojamiento |
| [port/include/xdk/README.md](port/include/xdk/README.md) | Procedencia y mantenimiento de las declaraciones Xbox |
| [docs/custom_edition_caches.md](docs/custom_edition_caches.md) | Formatos de mapas de Halo Custom Edition |
| [port/assets/menus/README.md](port/assets/menus/README.md) | Generadores y formato de menús heredados |
| [port/assets/menus/NON_HANDDRAWN.md](port/assets/menus/NON_HANDDRAWN.md) | Procedencia de imágenes heredadas |
| [port/assets/menus/UNWIRED.md](port/assets/menus/UNWIRED.md) | Funciones de menús Halo pendientes |
| [port/assets/fonts/README.md](port/assets/fonts/README.md) | Fuentes redistribuibles heredadas |
| [tools/harness/README.md](tools/harness/README.md) | Pruebas sin recursos comerciales |
| `port/third_party/*/README.md` | Procedencia y licencias de dependencias |
| [AUTHORS.md](AUTHORS.md) | Créditos de arte |
