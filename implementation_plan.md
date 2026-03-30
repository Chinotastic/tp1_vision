# Plan de implementación

## Qué pide el TP

1. Detectar y describir features.
2. Aplicar ANMS para repartir mejor los puntos.
3. Hacer matching entre la imagen ancla y las otras dos.
4. Estimar una homografía manual con 4 pares de puntos usando DLT propio.
5. Implementar RANSAC para quedarnos con inliers.
6. Calcular el canvas final sin recortar imágenes ni dejar bordes de más.
7. Hacer stitching y blending.
8. Dejar notebook, código y material para el informe.

## Enfoque elegido

- Base teórica y de estilo: `tutorial_04/homografias.ipynb`.
- Detector y descriptor: `cv2.SIFT_create`.
- Matching: BFMatcher con Lowe ratio y verificación cruzada.
- DLT: implementación propia en `src/homography.py`.
- RANSAC: implementación propia en `src/homography.py`.
- Warp y blending: OpenCV + máscaras de pesos con `distanceTransform`.

## Estructura de entrega

- `src/features.py`
- `src/homography.py`
- `src/pipeline.py`
- `src/visualization.py`
- `tp1_pano.ipynb`
- `bitacora_notebook.md`
- `explicaciones.md`
- `informe_borrador.md`

