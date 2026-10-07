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

## Regla fija: siempre considerar Motion Graphics

En **todo** video que se edite a partir de ahora, Motion Graphics
(overlays animados vía `hyperframes`/`motion-graphics`: cifras, listas,
pros/contras, CTA, etc.) es un parámetro por defecto a evaluar — no algo
que la usuaria tenga que pedir explícitamente cada vez. Al proponer el
plan de edición, siempre incluir una sugerencia concreta de qué gráficos
en movimiento le añadirían valor al guion/contenido de ese video en
particular, y confirmarlo con ella antes de construirlos (sigue aplicando
BRAND.md para colores).

## Regla fija: preguntar por la portada al cerrar un edit

En cuanto la usuaria confirme que un video editado quedó bien (sin más
objeciones, "está listo"), preguntarle de inmediato si quiere que genere
la portada de Instagram para ese reel — no esperar a que ella lo pida por
su cuenta en otro momento. Esto aplica a partir de ahora, para todos los
reels futuros.

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

## Láminas / tarjetas de texto con transición fuerte y sonido

Cuando el pedido sea "agrégale láminas/tarjetas con transición fuerte y
sonido" (fact-check cards, preguntas, citas, etc. insertadas en una
entrevista), lee primero
`.claude/skills/video-use/helpers/laminas/LAMINAS_LESSONS.md` — documenta
el flujo completo y dos errores costosos ya resueltos (parpadeo por
congelar el último frame de un clip fuente, y `amix` bajando el diálogo
por no usar `normalize=0`). Los scripts reutilizables están en
`helpers/laminas/` junto a ese archivo.

## Portadas: zona segura del título (regla fija)

En **toda** portada de Instagram (1080x1920) que se genere a partir de
ahora, el bloque de título (eyebrow + headline + badge) debe cumplir dos
condiciones a la vez, verificadas antes de entregar el archivo:

1. **No lo tapa el recorte de grid de Instagram.** El thumbnail del perfil
   recorta la portada a ~4:5 (1080x1350), quitando ~285px arriba y ~285px
   abajo. Mantener el texto dentro de y 380-1550 (con margen). Verificar
   simulando el recorte: `im.crop((0, (H-1350)//2, W, (H-1350)//2+1350))`
   y mirar el resultado antes de entregar.
2. **Ninguna letra ni detalle tapa la cara.** Medir dónde nace el cabello
   en la foto fuente de cada portada (overlay de grid de coordenadas cada
   100px, como en `fix_chin.py`/`grid_overlay_check.jpg`) y asegurar que
   el bloque de texto termine claramente por encima de ese punto (~50px
   de margen). Si el guion es largo (3 líneas) y no cabe con margen,
   reducir el tamaño de fuente/interlineado del titular en vez de dejarlo
   invadir el cabello o la cara.

Si tras esto no queda espacio seguro para el `@viainversiones` sin
acercarse a la cara, omitirlo en esa portada en particular (mejor sin
handle que tapando la cara).

## Identidad de marca

Antes de generar cualquier elemento visual (portadas, overlays, texto en
pantalla, colores de subtítulos) lee `BRAND.md` en la raíz del repo —
tiene la paleta cromática oficial, tipografía, tono de voz y estilo
fotográfico de Viainversiones. Es una regla dura: la marca pide colores
suaves y de bajo contraste ("susurrar, no gritar confianza"), así que
nunca usar negro/navy casi puro + acentos saturados tipo neón.

## Reedición de reels ya publicados (sin tocar audio/guion)

Cuando el pedido sea "reedita/pule este reel" sobre un video ya grabado y
publicado (la usuaria sube la voz limpia sin música y pide que yo
proponga subtítulos, overlays y música sin cambiar ni el audio ni el
guion), lee primero
`.claude/skills/video-use/helpers/reedicion-reels/REEDICION_REELS_LESSONS.md`
— documenta cómo sintetizar música de fondo local y gratuita (sin
créditos de IA) con pulso/ritmo en vez de un pad plano, cómo medir y
mezclarla bajo la voz sin aplastarla (`amix normalize=0` + medir dB antes
de fijar el volumen), y cómo armar subtítulos palabra por palabra con una
palabra clave resaltada en otro color. El script reutilizable de música
está en `helpers/reedicion-reels/make_bgm_ritmo.py`.

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
