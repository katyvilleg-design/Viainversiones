# Estudio de edición de video

Este proyecto es un estudio de edición de video asistido por Claude Code.
Combina dos skills instaladas en `.claude/skills/`:

- **`video-use`** — edición conversacional: transcribe, corta muletillas y
  silencios, aplica color, quema subtítulos y coordina la generación de
  overlays animados. Es el punto de entrada para cualquier pedido de
  "edita este video".
- **`hyperframes`** (+ sus 19 skills asociadas, ej. `motion-graphics`,
  `embedded-captions`, `talking-head-recut`) — renderiza gráficos en
  movimiento a partir de HTML/CSS/animaciones a MP4 determinista.
  `video-use` lo invoca automáticamente como sub-agente cuando el video
  necesita gráficos animados (charts, kinetic typography, overlays, etc.).

No hace falta invocar `hyperframes` a mano para gráficos en movimiento:
pídele a `video-use` el edit completo (muletillas + gráficos) y él
reparte el trabajo.

## Flujo de trabajo

1. Crea una carpeta por proyecto dentro de `videos/`, p. ej.
   `videos/lanzamiento-producto/`.
2. Copia ahí el material crudo.
3. Desde esa carpeta, abre Claude Code (`cd videos/lanzamiento-producto && claude`)
   y describe lo que quieres, por ejemplo:
   - "edita estos clips en un video de lanzamiento"
   - "quita las muletillas y los silencios"
   - "agrégale gráficos en movimiento a las cifras que menciono"
4. Claude propone un plan en español llano antes de tocar el corte y lo
   confirma contigo.
5. El resultado final queda en `videos/<proyecto>/edit/final.mp4`. El
   repo del estudio (`video-use/`, `hyperframes`) se mantiene limpio.

## Dependencias y entorno

- **FFmpeg** — requerido por ambas skills. Se instala automáticamente al
  iniciar la sesión vía `.claude/hooks/session-start.sh` (el contenedor de
  Claude Code on the web es efímero, así que se reinstala cada vez que
  hace falta).
- **Python (uv)** — dependencias de `video-use` en
  `.claude/skills/video-use/`, sincronizadas por el mismo hook
  (`uv sync`).
- **Node.js 22+** — usado por `hyperframes` vía `npx hyperframes ...`, ya
  viene preinstalado en el entorno.
- **ElevenLabs API key** — necesaria para transcribir (detecta muletillas,
  silencios, hablantes). Va en `ELEVENLABS_API_KEY` dentro de:
  - `.env` (raíz del proyecto), y
  - `.claude/skills/video-use/.env` (donde `video-use` la busca primero).

  Ninguno de los dos `.env` se sube a git (ver `.gitignore`). Si `.env`
  está vacío, agrega tu key ahí antes de pedir una transcripción.

## Estructura

```
videos/                        # tus proyectos de video (no se commitea el material)
  <proyecto>/                  # material crudo + edit/final.mp4 al terminar
.claude/
  skills/
    video-use/                 # skill de edición conversacional (vendorizada)
    hyperframes*/, motion-graphics/, ... # skills de HyperFrames (vendorizadas)
  hooks/session-start.sh        # instala ffmpeg + uv sync en cada sesión remota
  settings.json                 # registra el hook de SessionStart
.env                             # ELEVENLABS_API_KEY (no se commitea)
```

## Actualizar las skills

Ambas skills están vendorizadas (copiadas dentro del repo, no como
submódulo) para que sobrevivan a que el contenedor se reinicie. Para
traer cambios de upstream:

```bash
# video-use
git clone --depth 1 https://github.com/browser-use/video-use /tmp/video-use
cp -a /tmp/video-use/. .claude/skills/video-use/ && rm -rf .claude/skills/video-use/.git

# hyperframes
npx -y skills update hyperframes --copy -a claude-code
```
