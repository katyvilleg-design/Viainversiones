# Láminas / tarjetas de texto — guía y errores ya resueltos

Esta guía documenta cómo insertar tarjetas de texto ("láminas") con
transiciones fuertes y sonido en un video de entrevista, y los errores caros
que ya se cometieron una vez para no repetirlos. Los scripts que menciona
están en `helpers/laminas/` (junto a este archivo).

## Flujo recomendado

1. **Generar la imagen de la lámina** — `laminas/make_card_image.py`.
   Fondo difuminado + oscurecido (tomado de un frame real del video) +
   texto blanco en negrita centrado. Un JSON de spec por lote.

2. **Convertir la imagen en clip silencioso** — `laminas/make_still_card_clip.py`.
   Sostiene la imagen el tiempo que se pida, audio en silencio real.

   **REGLA DE ORO: nunca "extiendas" una lámina reproduciendo el video
   original y congelando su último frame (`tpad`, concat original+freeze,
   etc.).** Si el video fuente (típicamente exportado de CapCut/celular)
   tiene el más mínimo artefacto de compresión cerca de esos frames —
   altísimamente probable — ese artefacto queda congelado y se ve como un
   parpadeo. Ya pasó dos veces en este proyecto. La lámina completa debe
   ser SIEMPRE una sola imagen fija generada aparte, nunca contenido
   "vivo" decodificado del original.

3. **Detectar los cortes de lámina en el video del usuario** — si el video
   ya viene con las láminas insertadas (el usuario las puso con CapCut u
   otra app) y hay que agregarles transición/sonido, detecta los cortes con:

   ```bash
   ffmpeg -i video.mp4 -vf "select='gt(scene,0.05)',metadata=print" -f null - 2>&1 | grep pts_time
   ```

   **Usa un threshold MUY bajo (0.05), no el default de referencia (0.3-0.4).**
   Dos láminas oscuras consecutivas (mismo fondo difuminado, solo cambia el
   texto) tienen muy poco delta de escena y un threshold alto se las salta
   — en este proyecto 3 de 6 "láminas" detectadas eran en realidad 2 láminas
   pegadas cada una, y no se notó hasta la segunda ronda de revisión. Antes
   de dar por buena la lista de cortes, extrae un frame de texto completo
   de CADA tramo y confírmalo por contenido, no solo por duración.

4. **Cortar en segmentos** — `laminas/split_at_boundaries.py` (fade de
   30ms en cada borde nuevo, Hard Rule de video-use).

5. **Ensamblar con transición fuerte** — `laminas/assemble_with_transitions.py`
   (fadeblack de 0.25s + sonido de impacto de `laminas/make_hit_sound.py`
   en cada corte). Sirve tanto para cortes lámina↔entrevista como
   lámina↔lámina.

   **GOTCHA CRÍTICO (costó horas encontrarlo): `amix` por defecto usa
   `normalize=1`, que divide la señal entre el número de streams
   mezclados.** Si mezclas el audio principal con N sonidos de impacto
   cortos, eso son N+1 streams, y `amix` termina bajando el diálogo hasta
   -20dB aunque los golpes sean individualmente bajos. **Usa siempre
   `normalize=0` en cualquier `amix` con más de 2 entradas**, controlando
   el volumen relativo tú mismo con `volume=`. Esto aplica también al mix
   final con la música de fondo, no solo a los golpes de transición.

6. **Música de fondo suave (opcional)** — `laminas/make_ambient_music.py`
   si no hay pista con licencia. Genera la música con unos segundos MÁS
   de duración que el video final (el video puede crecer en iteraciones
   posteriores — dale margen, p. ej. +10s) para que `atrim` nunca se quede
   corto al final.

7. **Verificación antes de entregar** (no te fíes solo de mirar un frame
   del medio de cada lámina):
   - Extrae frames a `fps=8` de CADA lámina completa y compara brillo medio
     frame a frame (`numpy`); un salto aislado de ida y vuelta es un
     parpadeo, aunque sea sutil.
   - Corre `volumedetect` en ventanas de toda la pista, no solo puntos
     sueltos, para confirmar que no quedó ningún residuo de audio real
     colado en lo que debería ser silencio.
   - Confirma con un frame de texto completo que cada lámina en su
     posición final es la que corresponde — no asumas por duración.

## Referencia rápida de comandos

```bash
# 1. Generar imágenes de láminas (spec.json: [{text, out, font_size}, ...])
python helpers/laminas/make_card_image.py --spec spec.json --bg frame.png

# 2. Convertir a clip silencioso de N segundos
python helpers/laminas/make_still_card_clip.py card.png 6.0 -o card.mp4

# 3. Sonido de impacto (una vez, se reutiliza)
python helpers/laminas/make_hit_sound.py -o hit.wav

# 4. Ensamblar todo con transición fuerte
python helpers/laminas/assemble_with_transitions.py clip_order.json hit.wav -o assembled.mp4

# 5. Mezclar música de fondo (¡normalize=0!)
python helpers/laminas/make_ambient_music.py -o music.wav --dur <duracion_final+10>
ffmpeg -i assembled.mp4 -i music.wav -filter_complex \
  "[1:a]atrim=0:<duracion_final>,volume=0.12[music];[0:a][music]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 192k final.mp4
```
