# Explicaciones

## Idea general

Tomamos tres imágenes con solapamiento, elegimos una como ancla y llevamos las otras dos al mismo sistema de coordenadas mediante homografías. Con eso armamos un panorama único.

## Método elegido

- Features SIFT para detectar y describir puntos distintivos.
- ANMS para repartir mejor los puntos.
- BFMatcher + Lowe ratio + cross-check para obtener matches más confiables.
- DLT propio para estimar homografías.
- RANSAC propio para filtrar outliers.
- `warpPerspective` para warpear.
- `distanceTransform` para generar pesos de blending.

## Qué parámetros suelen importar más

- `nfeatures` de SIFT.
- `contrastThreshold` de SIFT.
- `num_keep` de ANMS.
- `ratio` de Lowe.
- `reproj_threshold` de RANSAC.
- `num_iters` de RANSAC.

