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

## Regla fija: los recursos visuales son dinámicos por defecto

Cuando la usuaria pida un recurso/gráfico para acompañar algo (una frase,
un dato, un ejemplo), construirlo **en movimiento continuo** por defecto
(estilo de la pieza "HOY vs SE DUPLICA": elementos que crecen/se revelan
y además tienen algo animándose todo el tiempo — línea con shimmer,
breathing, etc. — nunca una tarjeta que se arma una vez y luego queda
quieta). Solo construir algo estático si ella lo pide explícitamente. Si
no lo pide, asumir movimiento.

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

## Sistema de producción audiovisual (regla fija, permanente)

A partir de ahora, **todo** reel que se construya (editado desde cámara o
100% animado desde audio) debe seguir este estándar sin que la usuaria lo
repita cada vez — "master prompt" dado el 2026-10-12 (y su versión
ampliada el mismo día). Actuar como equipo completo de producción
(dirección creativa, motion graphics, data-viz, sonido, QA) y **ejecutar**,
no solo describir u opinar.

**Especificaciones de exportación:** vertical 9:16, 1080x1920, MP4,
máximo 60s (si el audio real supera 60s, avisar y pedir autorización
antes de recortarlo — nunca acelerar la voz para encajar).

**Detección de modalidad (automática, sin preguntar):**
- **Modalidad A — 100% animado:** llega solo audio o solo guion de
  texto. Construir toda la narrativa visual (gráficos, infografías,
  diagramas, comparaciones, cifras animadas). Nada de diapositivas
  estáticas ni sucesión de imágenes genéricas — lenguaje cinematográfico,
  movimiento, continuidad. Si solo llega texto (sin audio), avisar que
  no hay narración disponible y dejar el proyecto listo para
  sincronizarla cuando ella la grabe — nunca clonar su voz ni inventar
  una grabación.
- **Modalidad B — híbrido con cámara:** llega un video de ella hablando
  a cámara. Combinar su presencia real con recursos visuales — no tiene
  que estar en pantalla los 60s completos; decidir con criterio
  narrativo cuándo su imagen aporta (conexión/confianza/énfasis) y
  cuándo conviene sustituirla por una explicación visual. Nunca
  modificar sus facciones, proporciones, expresiones o identidad; nunca
  generar versiones artificiales de su rostro o movimientos. Conservar
  gestos naturales, permitir ajustes de encuadre/color/iluminación,
  evitar cortes que produzcan saltos corporales raros, no alterar la voz
  original.

**Fidelidad al guion:** el guion que la usuaria aprueba no se reescribe,
reordena ni se le cambian las palabras, el tono o el CTA por iniciativa
propia. Si hay un problema de claridad, duración o un dato dudoso,
señalarlo primero y esperar autorización antes de tocarlo.

**Verificación de datos (segunda revisión independiente):** cuando el
guion incluya cifras/porcentajes/fechas/cálculos/afirmaciones financieras
concretas (no ejemplos hipotéticos marcados como tales), verificar con
fuentes primarias/oficiales cuando sea posible (WebSearch) antes de
darlas por buenas en los gráficos — nunca inventar una fuente ni afirmar
haber consultado algo que no se revisó. Distinguir dato comprobado /
ejemplo hipotético / interpretación / pendiente de verificar. Si algo
resulta incorrecto o no verificable, no cambiar el guion en silencio:
reportar afirmación original, problema detectado, información correcta o
limitación, fuente, y corrección recomendada — y pausar esa escena hasta
que ella decida. Los gráficos deben representar las cantidades y
proporciones con fidelidad (sin exagerar diferencias ni alterar escalas).

**Storyboard antes de construir:** para un reel nuevo (no para un ajuste
menor sobre uno ya aprobado), proponer primero una tabla de escenas en
español llano — timestamp, narración exacta, recurso visual, texto en
pantalla, animación, transición, efecto de sonido previsto, música/cambio
de intensidad si aplica, objetivo narrativo — y esperar luz verde. Salvo
que la usuaria pida explícitamente saltarse ese paso ("dame tu mejor
resultado", "guíate por el guion"), en cuyo caso se construye directo con
buen criterio y se presenta el resultado terminado.

**Diseño sonoro — obligatorio, no opcional:**
- Todo video lleva SFX con función narrativa (nunca decorativos ni uno
  por cada palabra/movimiento): whooshes en transiciones, pops al
  aparecer cifras/elementos, clicks en botones/tablas/selecciones, ticks
  en contadores/porcentajes, risers antes de revelar un dato, impacts
  sutiles en cifras/conclusiones clave, swishes en movimientos
  laterales, sonidos de confirmación al completar un paso/resultado.
  Sincronizados con el instante exacto del movimiento/revelación/cambio
  de escena/palabra enfatizada — nunca antes o después sin intención. Un
  silencio intencional también es una herramienta narrativa válida.
- Todo video lleva música instrumental de fondo que nunca compite con la
  voz, con ritmo apropiado y que acompaña los cambios de intensidad —
  nada infantil, exagerado ni excesivamente dramático.
- Mezcla profesional: la voz es siempre el elemento dominante. Mezclar
  con `amix normalize=0`, medir niveles con `ffmpeg -af volumedetect`
  antes de fijar el volumen de SFX/música (no fiarse del oído), aplicar
  ducking cuando la música conviva con el habla, evitar picos/distorsión
  y cambios de volumen injustificados.
- **Cómo se genera en este entorno** (sin internet para bancos de sonido
  ni música con copyright, y sin clonación de voz): SFX se sintetizan
  localmente con ffmpeg (ruido filtrado para whooshes, tonos cortos con
  decay para ticks/pops/clicks, acordes de senos superpuestos para
  chimes/impacts — ver `videos/como-reducir-gastos-animado/edit/sfx/`).
  La música de fondo se genera igual que en
  `helpers/reedicion-reels/make_bgm_ritmo.py` (pulso/ritmo local, no un
  pad plano). Si falta narración, dejar el proyecto listo para que ella
  la grabe — nunca inventar una grabación con su voz.
- **Entregables cuando sea técnicamente posible:** video con voz+música+
  SFX integrados (mezcla final), más las pistas por separado (voz
  original, SFX, música) por si hace falta retocar en otra herramienta.

**Subtítulos — se preparan, pero NO se queman en el video final (decisión
de la usuaria, 2026-10-12):** construir igual los subtítulos palabra por
palabra con el mismo criterio de siempre — paleta y resaltado de
palabras clave coherentes con los colores que esas palabras ya tienen en
los gráficos de esa escena, posición que no tape badges/íconos/texto en
pantalla (referencia: `videos/como-reducir-gastos-animado/edit/build_subs.py`)
— pero **no** incluir el paso de quemarlos (`ass=...`) sobre el
`final.mp4` que se entrega. Entregar el video limpio **y además** el
archivo de subtítulos ya armado (`.ass`/`.srt`, con los timestamps y
colores ya resueltos) para que ella los agregue en CapCut Pro.

**Dirección creativa — evitar:** monedas/billetes flotantes, iconografía
financiera literal (alcancías, bolsas de dinero), flechas sin contexto,
gráficos bursátiles genéricos, zooms constantes, transiciones
exageradas, efectos sonoros excesivos, texto que tape innecesariamente
la pantalla, animaciones sin función narrativa/educativa. Cada escena
debe tener identidad propia (no repetir exactamente la misma
composición/animación entre videos), priorizando claridad sobre
espectáculo.

**Sistema de visualización financiera:** preferir el recurso que mejor
explique la idea — comparaciones (alternativas lado a lado, proporción
real), crecimiento (curvas/barras animadas para inversión/interés/
rendimiento), procesos (líneas de tiempo/diagramas), cálculos (la
operación matemática construyéndose progresivamente, como ya se hace con
el payoff de sumas), datos (estadísticas animadas sin alterar escalas),
conceptos abstractos (analogías visuales, nunca iconografía financiera
prohibida).

**Estrategia de retención:** gancho reforzado visual y sonoramente en los
primeros 0–3s (sin intro de logo que retrase el contenido), progresión
narrativa en el desarrollo con cambios visuales/sonoros en cada idea
nueva/contraste/revelación (sin forzar cortes que perjudiquen la
comprensión), cierre que refuerza la conclusión y acompaña el CTA ya
aprobado (sin agregar llamados a la acción adicionales).

**Eficiencia:** no regenerar un video completo por una corrección menor
(editar el archivo puntual y volver a renderizar esa escena/paso, como
ya se hace). No repreguntar información que ya está en el guion o en
este archivo. Reutilizar componentes gráficos/sonoros entre escenas
cuando tenga sentido.

**Control de calidad antes de entregar:** duración ≤60s, narración
sincronizada, guion respetado (palabras/tono/intención/CTA), datos
verificados o marcados como ejemplo, gráficos matemáticamente correctos,
transiciones fluidas, legible en móvil, ritmo natural (ni acelerado ni
artificial), identidad visual consistente (BRAND.md), presencia a cámara
integrada con naturalidad cuando aplica (modalidad B), SFX sincronizados
con lo que deben acompañar, voz siempre clara por encima de música/SFX,
sin efectos repetitivos/excesivos/molestos, sin distorsión ni cortes de
volumen injustificados, archivo final íntegro. No auto-aprobar el propio
trabajo — señalar defectos reales si los hay.

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
