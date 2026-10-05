# Reedición de Reels @viainversiones — lecciones reutilizables

Contexto: serie de 9 reels de educación financiera ya publicados, que se
están re-editando uno por uno (ver `Prompts_Reedicion_9_Reels.md` que la
usuaria subió). En cada uno: **audio/voz y guion 100% intactos** — solo se
suma subtítulos, overlays animados, música de fondo y CTA de "guardar".

## Música de fondo — decisión y método

La usuaria sube el video solo con la voz limpia (sin música), y pidió
explícitamente que **yo proponga la música** en cada reel, sin tener que
referenciar el audio del reel ya publicado — no quiere perder tiempo
decidiendo cuál pega mejor. Esto aplica a los 9 reels de esta serie.

**Nunca usar créditos de IA de pago (Magnific, etc.) para esto.** Se
sintetiza localmente y gratis con `make_bgm_ritmo.py` (en esta misma
carpeta), que genera una pista con tres capas:

1. **Pad armónico suave** — acordes simples (ej. Cmaj9–Am7–Fmaj7–G),
   varios senos desafinados levemente + LFO lento para que respire, igual
   que `helpers/laminas/make_ambient_music.py` pero con cambios de acorde.
2. **Pulso rítmico contenido** — un "thump" grave y suave en cada beat
   (BPM configurable, ~90–100 para contenido informativo), para que NO
   suene plano ni a silencio de fondo total (pedido explícito en varios de
   los 9 prompts: "evita audios planos sin dinámica").
3. **Pulseo/arpegio disperso** — notas sueltas en los contratiempos,
   aleatoriamente salteadas para que no se sienta mecánico — da sensación
   de movimiento sin ser un beat que compita con la voz.

Uso:
```bash
python3 helpers/reedicion-reels/make_bgm_ritmo.py -o bgm.wav --dur <segundos_video + 3-5>
```
El mood/acordes/BPM son ajustables editando las constantes `CHORDS` y
`BPM` al inicio del script según el tono de cada reel (ej. más urgente →
BPM más alto y acordes menores; más cálido/editorial → BPM más bajo).

### Mezcla con la voz — nunca a ciegas, siempre medir

No asumir un volumen fijo de música. El método que funcionó:

```bash
# 1. medir el nivel real de la voz del reel
ffmpeg -nostdin -i voice.wav -af volumedetect -f null - 2>&1 | grep mean_volume

# 2. medir el nivel de la pista de música generada
ffmpeg -nostdin -i bgm.wav -af volumedetect -f null - 2>&1 | grep mean_volume

# 3. atenuar la música para que quede ~10-11 dB por debajo del promedio
#    de la voz (suficiente para que se note en los silencios sin competir)
ffmpeg -nostdin -i bgm.wav -t <dur> -af "volume=<factor>,afade=t=out:st=<dur-1>:d=1.0" -c:a pcm_s16le bgm_trim.wav

# 4. mezclar con normalize=0 (si no, amix aplasta la voz — lección ya
#    aprendida en el proyecto ser-venezolano, se repite aquí)
ffmpeg -nostdin -i voice.wav -i bgm_trim.wav -filter_complex \
  "[0:a][1:a]amix=inputs=2:duration=longest:normalize=0[a]" -map "[a]" -c:a pcm_s16le mixed_audio.wav

# 5. verificar: mean_volume del mix debe quedar muy cerca del mean_volume
#    de la voz sola (diferencia <1 dB), y max_volume sin pasar de -1dB
#    (sin clipping). Revisar también un tramo de silencio de la voz para
#    confirmar que ahí la música SÍ se escucha (si no, subió muy poco el
#    volume= del paso 3).
```

En el reel de DCA (#5), voz mean ≈ -29.5dB, bgm cruda mean ≈ -18.1dB →
`volume=0.085` dejó el mix en mean ≈ -29.1dB (casi igual a la voz sola) y
el tramo de silencio en ≈ -36dB (música audible pero subordinada). Ese
`0.085` NO es un valor fijo — depende del nivel de cada bgm.wav generado,
por eso el paso de medir siempre antes de fijar el `volume=`.

## Subtítulos palabra por palabra con resaltado de término clave

Varios de los 9 prompts piden subtítulos dinámicos palabra por palabra
(no por frase) con una palabra clave en color distinto cada vez que
aparece (ej. "DCA" en dorado, números en verde/amarillo, "HOY" resaltado,
etc.). Método: generar un `.ass` con **un evento por palabra** (nunca SRT
de frases — se pierde la granularidad), usando los timestamps word-level
de Scribe, y envolver la palabra clave con tags de color inline:

```
{{\c&H00AA66B5&}}DCA{{\c&H00FFFFFF&}}
```

(ASS usa `&HAABBGGRR&` — **usar siempre los colores de `BRAND.md`**, no
un dorado/neón inventado. Para el Azul Sereno `#4A80B5` el código es
`&H00B5804A&`; para el Dorado Tenue `#DAB97C` es `&H007CB9DA&`. La v1 del
reel de DCA usó un dorado saturado `#E8B33D` que NO es el de marca — se
corrigió después de que la usuaria compartió sus documentos de marca.
Ver `BRAND.md` en la raíz del repo antes de elegir cualquier color.)
Ver `build_subs.py` dentro de cada carpeta de proyecto
(`videos/<reel>/edit/build_subs.py`) como plantilla — no está
centralizado aquí porque cada reel resalta una palabra/color distinto.
Fuente usada: DejaVu Sans Bold (viene preinstalada, soporta tildes/ñ) —
sustituto temporal de Poppins/Nunito/Inter (los de marca), que no están
disponibles en este entorno ni se pueden descargar por la política de
red actual. Ver nota de tipografía en `BRAND.md`.

## Overlays animados (checklist, gráficos, íconos de CTA)

Se delegan a sub-agentes `hyperframes` en paralelo (nunca secuencial —
regla dura de `video-use`), renderizados a transparente (`webm` con
alpha) y compuestos sobre el video base. Mantenerlos siempre en el
espacio vacío de la toma (arriba de la cabeza, laterales) sin tapar la
cara — revisar un par de frames del video primero para saber dónde está
ese espacio seguro en cada caso, no asumir.

## Resolución

Los 9 videos fuente llegan en distintas resoluciones verticales (ej.
576x1024). Si la relación de aspecto ya es 9:16, basta un
`scale=720:1280:flags=lanczos` limpio (sin crop ni distorsión). Verificar
con `ffprobe` antes de asumir.
