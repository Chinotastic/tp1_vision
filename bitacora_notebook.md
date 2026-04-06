# Bitácora del notebook

Este archivo se va a mantener en paralelo al notebook final. La idea es que cada celda tenga una explicación corta pero útil: qué hacemos, por qué, qué método usamos y qué parámetros vale la pena tocar.

## Estado actual de implementación

- Set de prueba principal: `udesa`.
- Parámetros base actuales del pipeline:
  - `max_size = 1200`
  - `nfeatures = 4000`
  - `contrast_threshold = 0.02`
  - `edge_threshold = 10`
  - `sigma = 1.6`
  - `anms_keep = 700`
  - `anms_robust = 0.9`
  - `ratio = 0.75`
  - `cross_check = True`
  - `ransac_iters = 3000`
  - `ransac_thresh = 5.0`
  - `blend_power = 1.0`
- Resultado preliminar sobre `udesa`:
  - Par `0 -> 1`: 91 matches, 84 inliers.
  - Par `2 -> 1`: 33 matches, 24 inliers.
  - Panorama exportado en `img/outputs/udesa/panorama.png`.
- Resultado preliminar sobre `cuadro`:
  - Par `0 -> 1`: 130 matches, 95 inliers.
  - Par `2 -> 1`: 72 matches, 33 inliers.
  - Panorama exportado en `img/outputs/cuadro/panorama.png`.
- Visualizaciones nuevas agregadas:
  - Correspondencias manuales coloreadas para la DLT.
  - Contorno proyectado sobre la imagen ancla usando la homografía.
  - Matches totales, inliers y outliers por separado.
  - Histograma de error de reproyección.
  - Canvas final con contornos, warps intermedios y máscaras.

## Celda 1 - Setup e imports

- Objetivo:
  Cargar librerías, módulos de `src/` y definir paths de imágenes.
- Método:
  Setup simple del notebook.
- Parámetros importantes:
  - `SET_NAME`: cuál conjunto usar, por ejemplo `udesa` o `cuadro`.
  - `ANCHOR_INDEX`: qué imagen se toma como ancla.
  - `MAX_SIZE`: tamaño máximo de trabajo para acelerar pruebas.
- Qué se puede modificar:
  El set a usar y el tamaño de reescalado.

## Celda 2 - Visualización inicial del set

- Objetivo:
  Mostrar las tres imágenes y verificar visualmente el solapamiento.
- Método:
  Carga y visualización directa.
- Parámetros importantes:
  - `MAX_SIZE`.
- Qué se puede modificar:
  El tamaño de visualización.

## Celda 3 - Features crudas

- Objetivo:
  Detectar puntos clave y descriptores antes de ANMS.
- Método:
  `cv2.SIFT_create`.
- Parámetros importantes:
  - `nfeatures`
  - `contrastThreshold`
  - `edgeThreshold`
  - `sigma`
- Valores actuales:
  - `nfeatures = 4000`
  - `contrastThreshold = 0.02`
  - `edgeThreshold = 10`
  - `sigma = 1.6`
- Qué se puede modificar:
  La sensibilidad del detector y la cantidad máxima de keypoints.

## Celda 4 - ANMS

- Objetivo:
  Quedarnos con menos puntos pero mejor distribuidos.
- Método:
  Adaptive Non-Maximal Suppression implementado a mano.
- Parámetros importantes:
  - `num_keep`
  - `robust_factor`
- Valores actuales:
  - `num_keep = 700`
  - `robust_factor = 0.9`
- Qué se puede modificar:
  La cantidad final de puntos y cuán estricta es la condición de “más fuerte”.

## Celda 5 - Matching

- Objetivo:
  Relacionar features entre el ancla y cada imagen lateral.
- Método:
  BFMatcher con Lowe ratio y cross-check.
- Parámetros importantes:
  - `ratio`
  - `cross_check`
- Valores actuales:
  - `ratio = 0.75`
  - `cross_check = True`
- Qué se puede modificar:
  El umbral de Lowe y si se exige reciprocidad.

## Celda 6 - Homografía manual

- Objetivo:
  Mostrar cómo se obtiene una homografía usando 4 pares elegidos a mano.
- Método:
  DLT propio.
- Parámetros importantes:
  - `manual_points_left`
  - `manual_points_right`
- Qué se puede modificar:
  Los cuatro pares de correspondencias elegidos.

## Celda 7 - Correspondencias manuales y proyección

- Objetivo:
  Ver visualmente los 4 puntos elegidos y cómo el contorno de una imagen cae sobre la ancla.
- Método:
  Dibujado con colores consistentes entre ambas imágenes + proyección del rectángulo usando la homografía estimada.
- Parámetros importantes:
  - `manual_points_left`
  - `manual_points_right`
- Qué se puede modificar:
  Los puntos manuales y el tamaño de la figura para el informe.

## Celda 8 - Error de reproyección e inliers

- Objetivo:
  Medir qué tan bien explica la homografía a los matches.
- Método:
  Distancia de reproyección.
- Parámetros importantes:
  - `reproj_threshold`
- Valor actual:
  - `reproj_threshold = 5.0`
- Qué se puede modificar:
  El umbral que separa inliers de outliers.

## Celda 9 - RANSAC

- Objetivo:
  Estimar una homografía robusta sin depender de `cv2.RANSAC`.
- Método:
  RANSAC propio sampleando 4 correspondencias por iteración.
- Parámetros importantes:
  - `num_iters`
  - `reproj_threshold`
  - `random_seed`
- Valores actuales:
  - `num_iters = 3000`
  - `reproj_threshold = 5.0`
  - `random_seed = 0`
- Qué se puede modificar:
  La cantidad de iteraciones y el threshold de inliers.

## Celda 10 - Visualización de matches e histograma

- Objetivo:
  Separar visualmente matches buenos y malos y comparar contra el umbral de reproyección.
- Método:
  `cv2.drawMatches` para todos, inliers y outliers + histograma de distancias.
- Parámetros importantes:
  - `ransac_thresh`
  - cantidad de bins del histograma
- Qué se puede modificar:
  El threshold, el número de bins y qué pares se muestran.

## Celda 11 - Canvas final

- Objetivo:
  Calcular tamaño y traslación para que entren las tres imágenes.
- Método:
  Transformar los 4 vértices de cada imagen y sacar mínimos/máximos.
- Parámetros importantes:
  - No tiene muchos hiperparámetros.
- Qué se puede modificar:
  Eventualmente una política de recorte final.

## Celda 12 - Stitching y blending

- Objetivo:
  Warpear, mezclar y obtener la panorámica final.
- Método:
  `cv2.warpPerspective` + máscaras de pesos con `cv2.distanceTransform`.
- Parámetros importantes:
  - `blend_power`
  - estrategia de recorte
- Valores actuales:
  - `blend_power = 1.0`
- Qué se puede modificar:
  Cómo se suavizan las costuras y qué tan agresivo es el recorte final.

## Celda 13 - Canvas, warps y máscaras

- Objetivo:
  Mostrar claramente cómo queda cada imagen transformada antes del blending.
- Método:
  Contornos proyectados sobre el canvas + visualización de `warped_images` y `warped_masks`.
- Parámetros importantes:
  - No agrega hiperparámetros nuevos.
- Qué se puede modificar:
  Qué warps o máscaras se exportan y el layout de la figura.

## Celda 14 - Resultados y conclusiones

- Objetivo:
  Guardar la panorámica, resumir parámetros y anotar observaciones para el informe.
- Método:
  Resumen reproducible.
- Parámetros importantes:
  - paths de salida
- Qué se puede modificar:
  Qué figuras se exportan para el informe.
  Hoy además se exportan:
  - `matches_all_*`
  - `matches_inliers_*`
  - `matches_outliers_*`
  - `projection_*`
  - `canvas_outline.png`
  - `mask_*.png`
