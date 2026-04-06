# Guía de Lectura Profunda del Notebook `tp1_pano.ipynb`

Este archivo está pensado para acompañarte mientras leés y corrés [tp1_pano.ipynb](/Users/frino/Desktop/Udesa/3%20AN%CC%83O/Vision/tp1_panoramica/tp1_pano.ipynb).

La idea no es solo decir "qué hace el notebook", sino ayudarte a entender:

- qué problema resuelve cada celda,
- qué concepto de visión artificial está detrás,
- qué parámetros importan de verdad,
- qué información relevante podés extraer de cada salida,
- y cómo diagnosticar resultados malos.

En otras palabras: este documento está escrito para que el notebook deje de ser una secuencia de comandos y pase a ser una historia geométrica coherente.

---

## 1. Qué está haciendo este notebook, en una frase

El notebook construye una panorámica a partir de tres imágenes usando:

- detección de features locales,
- emparejamiento entre imágenes,
- estimación de homografías robustas,
- warping al sistema de una imagen ancla,
- y blending para mezclar los resultados.

La hipótesis geométrica principal es esta:

**la relación entre vistas puede aproximarse con una homografía**.

Eso funciona bien cuando:

- la escena es aproximadamente plana,
- o la cámara rota con poca traslación,
- y hay suficiente solapamiento entre imágenes.

---

## 2. Cómo conviene estudiar este notebook

No lo leas como "setup, código, figura, siguiente".

Conviene leerlo en cuatro capas:

1. **Capa visual**: mirar qué muestran las imágenes.
2. **Capa algorítmica**: entender qué etapa del pipeline estás ejecutando.
3. **Capa geométrica**: entender qué supuesto está usando esa etapa.
4. **Capa experimental**: saber qué parámetros tocar y qué efecto esperar.

Si una celda produce una figura, la pregunta correcta no es "se ve linda o fea", sino:

"¿qué me está diciendo esta figura sobre la validez del modelo?"

---

## 3. Parámetros globales del notebook

Antes de entrar celda por celda, conviene tener una foto general de los parámetros importantes. El notebook parte de `DEFAULT_CONFIG` definido en [src/pipeline.py](/Users/frino/Desktop/Udesa/3%20AN%CC%83O/Vision/tp1_panoramica/src/pipeline.py).

Los más importantes son:

- `max_size`
- `nfeatures`
- `contrast_threshold`
- `edge_threshold`
- `sigma`
- `anms_keep`
- `anms_robust`
- `ratio`
- `cross_check`
- `ransac_iters`
- `ransac_thresh`
- `blend_power`

### Qué controla cada uno

#### `max_size`

Redimensiona las imágenes para trabajar más rápido.

- valor alto -> más detalle, más costo
- valor bajo -> menos costo, pero podés perder features útiles

Si el algoritmo anda raro por falta de puntos, una reducción excesiva puede ser la causa.

#### `nfeatures`

Cantidad máxima aproximada de keypoints SIFT.

- más alto -> más puntos candidatos
- más bajo -> ejecución más simple, pero riesgo de quedarse corto

#### `contrast_threshold`

Controla cuán exigente es SIFT con el contraste local.

- más bajo -> detecta más puntos, incluso débiles
- más alto -> se queda solo con estructuras más marcadas

#### `edge_threshold`

Evita keypoints inestables fuertemente asociados a bordes.

Si lo modificás, cambiás cuánto tolerás puntos alargados o mal condicionados.

#### `sigma`

Suavizado inicial del detector SIFT.

No suele ser el primer parámetro a tocar, pero afecta la sensibilidad a detalle fino.

#### `anms_keep`

Cantidad final de puntos después de ANMS.

- más alto -> más cobertura, más cómputo
- más bajo -> mayor síntesis, pero riesgo de perder geometría

#### `anms_robust`

Define qué significa que un punto sea “suficientemente más fuerte” que otro.

Afecta cómo se calcula el radio de supresión adaptativa.

#### `ratio`

Threshold del test de Lowe para matching.

- más chico -> más estricto, menos matches, más confiables
- más grande -> más permisivo, más matches, más outliers

#### `cross_check`

Exige reciprocidad entre matches.

Si está activado, reduce ambigüedad pero puede descartar matches útiles.

#### `ransac_iters`

Cantidad de iteraciones de RANSAC.

- más alto -> más probabilidad de encontrar una muestra limpia
- más bajo -> más rápido, pero menos robusto

#### `ransac_thresh`

Threshold del error de reproyección para decidir inliers.

Es uno de los parámetros más sensibles de todo el pipeline.

#### `blend_power`

Controla cuánto privilegia el blending el interior de cada imagen frente a los bordes.

Sirve para suavizar costuras, no para corregir geometría.

---

## 4. Guía celda por celda

Ahora sí, vamos a recorrer el notebook exactamente como está escrito.

---

## Celda 0

### Tipo

Markdown.

### Qué hace

Presenta el notebook como el punto de entrada principal del TP.

### Qué deberías entender acá

Todavía no hay contenido técnico, pero sí una decisión de diseño importante:

- el notebook no reimplementa todo,
- usa módulos de `src/`,
- y el notebook sirve como espacio de análisis, visualización y registro de resultados.

Eso es una buena práctica: separar lógica reusable de lógica exploratoria.

---

## Celda 1

### Qué hace

Importa:

- librerías generales,
- OpenCV,
- NumPy,
- Pandas,
- Matplotlib,
- y funciones propias del proyecto.

### Conceptos importantes

Esta celda define el “vocabulario” del notebook.

De [src/features.py](/Users/frino/Desktop/Udesa/3%20AN%CC%83O/Vision/tp1_panoramica/src/features.py) vienen:

- `load_image`
- `bgr_to_rgb`
- `detect_sift_features`
- `anms_filter`
- `match_descriptors`
- `points_from_matches`

De [src/homography.py](/Users/frino/Desktop/Udesa/3%20AN%CC%83O/Vision/tp1_panoramica/src/homography.py) vienen:

- `dlt_homography`
- `compute_reprojection_distances`
- `compute_inliers`
- `ransac_homography`

De [src/pipeline.py](/Users/frino/Desktop/Udesa/3%20AN%CC%83O/Vision/tp1_panoramica/src/pipeline.py) viene:

- `DEFAULT_CONFIG`
- `run_triplet`

De [src/visualization.py](/Users/frino/Desktop/Udesa/3%20AN%CC%83O/Vision/tp1_panoramica/src/visualization.py) vienen helpers para armar visualizaciones.

### Parámetros relevantes

No hay parámetros algorítmicos todavía. Solo hay configuración visual:

- `plt.rcParams['figure.figsize']`
- `plt.rcParams['axes.titlesize']`

### Qué información relevante te da

Te muestra que el notebook no es “código suelto”: está apoyado en una arquitectura modular.

Eso importa porque:

- si algo falla en el notebook, muchas veces el problema real está en `src/`,
- y si querés defender el TP, conviene saber en qué archivo vive cada responsabilidad.

---

## Celda 2

### Qué hace

Configura el experimento.

Define:

- qué set usar,
- cuál es la imagen ancla,
- dónde están las imágenes,
- dónde se guardan los outputs,
- y copia la configuración base.

### Variables centrales

#### `SET_NAME`

Elige el conjunto de imágenes.

En este momento puede ser, por ejemplo:

- `udesa`
- `cuadro`

### `ANCHOR_INDEX`

Define qué imagen será el sistema de referencia.

En este notebook se usa:

- `ANCHOR_INDEX = 1`

Eso significa que las demás imágenes se alinean con la imagen central.

### `IMAGE_PATHS`

Lista de rutas de entrada.

### `OUTPUT_DIR`

Carpeta donde se exportan:

- panorámica,
- warps,
- masks,
- matches,
- etc.

### `config = copy.deepcopy(DEFAULT_CONFIG)`

Esto es importante porque permite tocar parámetros localmente en el notebook sin modificar el default en el módulo.

### Parámetros importantes para experimentar

Acá es donde deberías mirar primero si querés mejorar resultados:

- `max_size`
- `nfeatures`
- `anms_keep`
- `ratio`
- `ransac_thresh`
- `blend_power`

### Qué información relevante te da

La salida de `config` te permite ver rápidamente el estado experimental actual.

Esa salida cumple el rol de “fotografía de la configuración”.

### Qué errores suelen aparecer si esta celda está mal

- rutas incorrectas -> imágenes no encontradas
- ancla incorrecta -> homografías menos estables
- output mal definido -> figuras no exportadas

---

## Celda 3

### Qué hace

Carga las imágenes con:

- `load_image(path, max_size=config['max_size'])`

y las muestra lado a lado.

### Concepto detrás

Antes de correr cualquier algoritmo, necesitás verificar visualmente:

- que las imágenes sean las correctas,
- que haya solapamiento suficiente,
- que el orden tenga sentido,
- y que la reducción de tamaño no haya destruido demasiado detalle.

### Qué hace `load_image`

En [src/features.py](/Users/frino/Desktop/Udesa/3%20AN%CC%83O/Vision/tp1_panoramica/src/features.py), `load_image`:

1. lee la imagen,
2. calcula un factor de escala si `max_size` es necesario,
3. y la redimensiona manteniendo relación de aspecto.

### Parámetro importante

#### `max_size`

Es el parámetro verdaderamente importante de esta celda.

Si lo bajás mucho:

- el notebook corre más rápido,
- pero podés perder estructuras finas,
- y el matching puede degradarse.

Si lo subís:

- ganás detalle,
- pero aumenta costo computacional.

### Qué deberías mirar en la figura

- que las tres imágenes pertenezcan al mismo barrido
- que haya solapamiento entre 0 y 1
- que haya solapamiento entre 2 y 1
- que la imagen ancla tenga sentido como referencia

### Si esta celda ya se ve mal

Si a ojo no hay suficiente solapamiento, ningún ajuste fino posterior va a salvar la panorámica.

---

## Celda 4

### Tipo

Markdown.

### Qué hace

Marca el inicio de la etapa de features.

### Por qué esta etapa importa

Todo el pipeline depende de encontrar puntos repetibles.

Si acá arrancás mal:

- no habrá buenos matches,
- la homografía será mala,
- y la panorámica final también.

---

## Celda 5

### Qué hace

Para cada imagen:

1. detecta keypoints y descriptores SIFT crudos,
2. les aplica ANMS,
3. guarda todo en `features_debug`.

### Estructura que construye

Para cada imagen guarda:

- `kp_raw`
- `des_raw`
- `kp_anms`
- `des_anms`

### Conceptos que aparecen

#### SIFT

Busca keypoints robustos a escala y rotación.

#### ANMS

No mejora el descriptor en sí, sino la distribución espacial del conjunto de keypoints.

### Parámetros importantes

#### `nfeatures`

Cantidad máxima de puntos SIFT.

#### `contrast_threshold`

Controla cuánto contraste necesitás para aceptar un keypoint.

#### `edge_threshold`

Regula sensibilidad a estructuras tipo borde.

#### `sigma`

Suavizado inicial del detector.

#### `anms_keep`

Cuántos puntos sobreviven después de ANMS.

#### `anms_robust`

Afecta el criterio de supresión adaptativa.

### Qué información relevante devuelve

La expresión final:

```python
[(i, len(x['kp_raw']), len(x['kp_anms'])) for i, x in enumerate(features_debug)]
```

te dice, por imagen:

- cuántos puntos detectó SIFT,
- y cuántos quedaron después de ANMS.

### Cómo interpretar esa tabla

Si la diferencia entre raw y ANMS es enorme, está bien: ANMS está filtrando fuerte.

Lo importante no es “tener muchísimos puntos”, sino tener puntos:

- útiles,
- distribuidos,
- y suficientes.

### Señales de alarma

- muy pocos puntos raw -> SIFT está detectando poco
- muy pocos puntos ANMS -> `anms_keep` demasiado chico o imagen poco rica

---

## Celda 6

### Qué hace

Muestra, para cada imagen:

- keypoints crudos arriba,
- keypoints luego de ANMS abajo.

### Qué deberías aprender mirando esta figura

Esta es una de las figuras más pedagógicas del notebook.

Te muestra la diferencia entre:

- “muchos puntos”
- y “buenos puntos para geometría”.

### Qué mirar exactamente

#### Fila superior: raw

Esperás:

- muchos puntos,
- posiblemente muy concentrados en regiones texturadas.

#### Fila inferior: ANMS

Esperás:

- menos puntos,
- mejor cobertura espacial,
- presencia en distintas partes de la imagen.

### Información relevante

Si la fila de ANMS queda demasiado vacía en zonas importantes, después la homografía puede quedar mal condicionada.

### Parámetros relevantes para corregir problemas

- `anms_keep`
- `anms_robust`
- `nfeatures`
- `contrast_threshold`

### Lectura correcta

No preguntes "¿hay menos puntos?".

Preguntá:

"¿los puntos que quedaron cubren bien la geometría de la escena?"

---

## Celda 7

### Tipo

Markdown.

### Qué hace

Marca el inicio de la etapa de matching contra la imagen ancla.

### Idea conceptual

Una vez que ya tenés features útiles, el siguiente problema es:

**cuáles de estos puntos de una imagen corresponden a cuáles puntos de la ancla**.

---

## Celda 8

### Qué hace

Para cada imagen lateral:

1. matchea descriptores contra la imagen ancla,
2. convierte los matches en coordenadas puntuales,
3. guarda el resultado en `matching_debug`.

### Qué se guarda

Para cada par:

- `matches`
- `pts1`
- `pts2`

### Conceptos importantes

#### BFMatcher

Compara cada descriptor contra todos los del otro conjunto.

#### Lowe ratio

Acepta el mejor match solo si es claramente mejor que el segundo.

#### Cross-check

Exige reciprocidad entre correspondencias.

#### `points_from_matches`

Convierte objetos `cv2.DMatch` en arreglos de puntos 2D.

### Parámetros importantes

#### `ratio`

Uno de los parámetros más delicados.

- más estricto -> menos matches, pero más limpios
- más permisivo -> más matches, pero con riesgo de ruido

#### `cross_check`

Si lo apagás, podés ganar matches, pero normalmente también ganás ambigüedad.

### Qué información relevante imprime

```python
Par 0->1: X matches
Par 2->1: Y matches
```

Eso te da una medida inicial de “densidad de correspondencias”.

### Cómo interpretar cantidades

No existe un número mágico universal, pero:

- si tenés muy pocos matches, RANSAC puede quedarse sin base
- si tenés muchos pero de mala calidad, RANSAC puede sufrir igual

### Error típico

Confundir “muchos matches” con “buena geometría”. La cantidad no reemplaza la calidad.

---

## Celda 9

### Qué hace

Visualiza hasta 60 matches para cada imagen lateral contra la ancla.

### Qué mirar

No se trata solo de ver si las líneas “van más o menos en la misma dirección”.

Tenés que mirar si los matches conectan:

- estructuras visualmente equivalentes,
- zonas plausibles del solapamiento,
- y una distribución razonable sobre la escena.

### Qué te dice esta figura

Te permite evaluar la calidad del matching **antes** de meter geometría robusta.

Eso es importante porque si el matching ya está muy roto:

- la homografía manual puede ser arbitraria,
- y RANSAC va a depender demasiado del azar.

### Parámetros que impactan esta visualización

- `ratio`
- `cross_check`
- `anms_keep`
- `nfeatures`

### Lectura práctica

Si ves muchos matches absurdos:

- el problema no es todavía RANSAC,
- el problema probablemente está en features o matching.

---

## Celda 10

### Tipo

Markdown.

### Qué hace

Marca la etapa didáctica de homografía manual con DLT.

### Por qué esta etapa existe

No es la más automática, pero sí una de las más formativas.

Acá el objetivo no es “resolver el TP” sino entender:

- qué datos necesita una homografía,
- cómo se construye,
- y cómo se comporta geométricamente.

---

## Celda 11

### Qué hace

Define correspondencias manuales para cada set y usa esas correspondencias para estimar homografías con DLT.

### Qué hay dentro de `MANUAL_POINTS_BY_SET`

Para cada set y para cada imagen lateral:

- `src`: puntos de la imagen lateral
- `dst`: puntos correspondientes en la ancla

### Qué concepto geométrico aparece

**cuatro puntos definen una homografía**, siempre que no sean degenerados.

### Qué está aprendiendo el estudiante acá

Que una homografía no aparece mágicamente de SIFT o RANSAC:

- si tenés correspondencias correctas,
- podés estimarla directamente.

### Parámetros importantes

Acá no hay hiperparámetros clásicos, pero hay una decisión crucial:

#### calidad de los puntos manuales

Los puntos deben ser:

- precisos,
- bien identificables,
- bien distribuidos,
- y verdaderamente correspondientes.

### Qué información relevante te devuelve

`H_manual_01, H_manual_21`

Estas matrices son la primera manifestación explícita del modelo geométrico del problema.

### Error típico

Pensar que cualquier 4 puntos sirven. No:

- si están mal elegidos,
- si están casi alineados,
- o si hay error fuerte de correspondencia,

la homografía puede salir muy mala.

---

## Celda 12

### Tipo

Markdown.

### Qué hace

Introduce la visualización de correspondencias manuales y proyección.

### Por qué es clave

Porque una matriz sola no dice mucho. Lo que enseña de verdad es verla actuar sobre puntos y sobre el contorno de la imagen.

---

## Celda 13

### Qué hace

Para cada imagen lateral:

1. recalcula la homografía manual,
2. arma una visualización de correspondencias coloreadas,
3. proyecta el contorno de la imagen lateral sobre la ancla.

### Qué estás validando acá

Dos cosas diferentes:

#### 1. Correspondencias manuales

Te aseguran que entendiste bien qué puntos están jugando el rol de pares.

#### 2. Proyección del contorno

Te permite ver si la homografía resultante “cae” donde debería.

### Parámetros importantes

#### `manual_points`

Son el corazón de esta celda.

### Qué información relevante te da la primera columna

La visualización con colores consistentes te deja verificar:

- si los puntos efectivamente representan la misma estructura,
- y si la elección manual es razonable.

### Qué información relevante te da la segunda columna

El contorno proyectado te muestra si la imagen lateral, al pasar por la homografía, queda bien ubicada sobre la ancla.

### Cómo leer esta visualización

Si el contorno proyectado cae:

- en zona lógica,
- con tamaño razonable,
- y orientación coherente,

entonces la homografía es creíble.

Si no:

- hay puntos mal elegidos,
- o la correspondencia manual no representa bien el problema.

---

## Celda 14

### Tipo

Markdown.

### Qué hace

Abre la etapa de RANSAC.

### Por qué esta etapa es indispensable

Porque en datos reales nunca podés confiar completamente en los matches.

Siempre hay:

- ruido,
- ambigüedad,
- falsos positivos.

RANSAC aparece para robustecer la estimación.

---

## Celda 15

### Qué hace

Para cada par lateral-ancla:

1. corre `ransac_homography`,
2. obtiene la homografía robusta,
3. obtiene la máscara de inliers,
4. calcula distancias de reproyección.

### Qué estructura arma

`ransac_debug[idx]` contiene:

- `H`
- `inlier_mask`
- `distances`

### Conceptos fuertes en esta celda

#### RANSAC

Muestra mínima + hipótesis + consenso.

#### Inlier mask

Te dice qué matches son consistentes con la mejor homografía hallada.

#### Distancias de reproyección

Cuantifican qué tan bien el modelo explica las correspondencias.

### Parámetros importantes

#### `ransac_iters`

Controla cuánto explora RANSAC.

#### `ransac_thresh`

Controla quién entra como inlier.

#### `random_seed`

Hace reproducible el muestreo.

### Qué información relevante imprime

```python
Par i->1: inliers = a / b
```

Eso te da la tasa de soporte geométrico del modelo.

### Cómo interpretar esta relación

Si `a` es cercano a `b`, el matching ya venía bastante coherente.

Si `a` es mucho menor que `b`, había muchos outliers.

### Qué significa una buena celda 15

No necesariamente "muchísimos inliers", sino:

- suficientes inliers,
- bien distribuidos,
- y una homografía visualmente razonable.

---

## Celda 16

### Qué hace

Resume en una tabla:

- cantidad de matches,
- cantidad de inliers,
- error medio de reproyección sobre inliers.

### Por qué esta celda es muy valiosa

Porque comprime en pocos números la salud geométrica de cada par.

### Qué significa cada columna

#### `matches`

Cuántas correspondencias entraron al análisis robusto.

#### `inliers`

Cuántas sobrevivieron como coherentes con la homografía estimada.

#### `mean_reproj_inliers`

Qué tan bien, en promedio, el modelo explica los inliers.

### Cómo usar esta tabla

Sirve para comparar pares.

Por ejemplo, puede pasar que:

- un par tenga muchos matches pero error medio alto,
- otro tenga menos matches pero error medio bajo.

Eso te ayuda a distinguir cantidad de calidad.

### Qué sería una mala señal

- pocos inliers
- error de reproyección medio alto
- fuerte asimetría entre pares

---

## Celda 17

### Tipo

Markdown.

### Qué hace

Introduce la etapa de visualización de inliers, outliers y errores.

### Por qué es fundamental

La tabla numérica sola no alcanza. Necesitás ver:

- dónde están los inliers,
- dónde están los outliers,
- cómo se distribuyen los errores.

---

## Celda 18

### Qué hace

Arma una figura de 2 filas x 4 columnas.

Para cada par muestra:

1. todos los matches filtrados,
2. inliers de RANSAC,
3. outliers,
4. histograma de error de reproyección.

### Esta es una de las celdas más importantes del notebook

Porque junta:

- correspondencia visual,
- validación geométrica,
- y medida cuantitativa.

### Columna 1: matches filtrados

Te muestra el estado del problema después del matching descriptorial, pero antes de la clasificación robusta final.

### Columna 2: inliers RANSAC

Esto es lo que realmente sostiene la homografía.

Qué deberías ver:

- coherencia espacial,
- líneas razonables,
- soporte sobre regiones relevantes.

### Columna 3: outliers

Te muestra qué descartó el modelo.

Qué deberías observar:

- matches absurdos,
- conexiones erráticas,
- patrones incompatibles con la geometría dominante.

### Columna 4: histograma de distancias

Te permite evaluar si `ransac_thresh` está bien elegido.

#### Cómo leer el histograma

Si la mayoría de los matches válidos cae claramente por debajo del threshold, el valor elegido es razonable.

Si la distribución no muestra separación clara:

- o hay mucho ruido,
- o el threshold está mal elegido,
- o el modelo no explica bien el par.

### Parámetros importantes

#### `ransac_thresh`

Es el parámetro más importante de esta celda.

#### `bins=25`

No cambia el algoritmo, pero sí cómo leés la distribución de errores.

### Qué información relevante podés extraer

Esta celda te deja responder:

- ¿el matching descriptorial era bueno?
- ¿RANSAC logró encontrar una estructura geométrica dominante?
- ¿los outliers son pocos o muchos?
- ¿el threshold elegido tiene sentido?

---

## Celda 19

### Tipo

Markdown.

### Qué hace

Marca el paso desde análisis por etapas al pipeline completo.

### Qué cambia conceptualmente acá

Hasta ahora analizabas piezas del problema. Desde acá empezás a ejecutar la composición de la panorámica de punta a punta.

---

## Celda 20

### Qué hace

Llama a:

```python
run_triplet(...)
```

y ejecuta el pipeline completo:

- detección,
- ANMS,
- matching,
- RANSAC,
- canvas,
- warping,
- blending,
- exportación.

### Qué devuelve `result`

Entre otras cosas:

- `images`
- `homographies`
- `pair_results`
- `panorama`
- `warped_images`
- `warped_masks`
- `canvas_debug`
- `config`

### Qué imprime

- shape de la panorámica final
- matches e inliers por par

### Parámetros importantes

Todos los de `config`, pero especialmente:

- `max_size`
- `anms_keep`
- `ratio`
- `ransac_iters`
- `ransac_thresh`
- `blend_power`

### Qué información relevante te da

Esta celda responde una pregunta clave:

"¿todo el pipeline completo produce una panorámica plausible?"

### Qué deberías revisar si falla

- si la forma final es extraña,
- si algún par tiene muy pocos inliers,
- si los outputs intermedios exportados son coherentes.

---

## Celda 21

### Qué hace

Muestra la panorámica final.

### Cómo leer correctamente esta imagen

No alcanza con mirar si "quedó linda". Mirá:

- continuidad de líneas,
- presencia de dobles bordes,
- deformaciones,
- saltos visibles,
- regiones negras o mal mezcladas,
- alineación general de la escena.

### Qué problemas podés diagnosticar acá

#### Problemas geométricos

Se ven como:

- bordes duplicados,
- desalineaciones,
- contornos corridos.

#### Problemas de mezcla

Se ven como:

- costuras,
- cambios bruscos de intensidad,
- transiciones visibles.

### Parámetros relevantes

- `ransac_thresh`
- `blend_power`
- `anms_keep`
- `ratio`

### Regla práctica

Si la geometría está mal, no culpes primero al blending.

---

## Celda 22

### Tipo

Markdown.

### Qué hace

Introduce la etapa final de inspección del canvas, warps y máscaras.

### Por qué es muy útil

Porque muchas veces la panorámica final no te deja distinguir si el problema fue:

- mala homografía,
- mal canvas,
- o mala mezcla.

Estas visualizaciones sí.

---

## Celda 23

### Qué hace

Construye una figura que muestra:

- el canvas y los contornos proyectados,
- las tres imágenes warpeadas,
- la panorámica final,
- y las máscaras warpeadas.

### `canvas_outline`

Es una visualización muy importante.

Te permite ver:

- dónde cae cada imagen dentro del canvas global,
- cuánto se solapan,
- y si la traslación global quedó razonable.

### Primera fila

#### Panel 1: canvas y contornos

Sirve para diagnosticar:

- tamaño del canvas,
- posición relativa de imágenes,
- plausibilidad de la proyección global.

#### Paneles 2 a 4: warped 0, 1, 2

Te muestran cómo quedó cada imagen después de `cv2.warpPerspective`.

Esto es clave porque te permite ver si:

- una imagen quedó muy estirada,
- muy corrida,
- o mal alineada respecto del sistema de referencia.

### Segunda fila

#### Panel 1: panorama final

Resume la composición.

#### Paneles 2 a 4: máscaras

Te muestran qué regiones del canvas aporta cada imagen.

### Qué información relevante te da esta celda

Te deja separar tres preguntas:

1. ¿La geometría está bien?
2. ¿El canvas está bien construido?
3. ¿La superposición entre imágenes es razonable?

### Parámetros que más impactan esta celda

- `blend_power`
- `ransac_thresh`
- calidad de homografías previas

### Error típico

Mirar solo la panorámica y no estas visualizaciones. Si querés entender, esta celda es indispensable.

---

## Celda 24

### Qué hace

Lista todos los archivos exportados en `OUTPUT_DIR`.

### Por qué importa

No es solo una celda administrativa.

Te confirma:

- qué resultados quedaron guardados,
- qué material podés usar en el informe,
- y si el pipeline realmente exportó todo lo esperado.

### Qué outputs aparecen normalmente

- `features_raw_*`
- `features_anms_*`
- `matches_all_*`
- `matches_inliers_*`
- `matches_outliers_*`
- `projection_*`
- `warped_*`
- `mask_*`
- `canvas_outline.png`
- `panorama.png`

### Qué información relevante te da

Te permite verificar trazabilidad experimental:

"corrí este set con esta config y estos fueron los artefactos generados".

Eso es valioso para informe y para debugging.

---

## 5. Qué celdas son las más formativas

Si tu objetivo es entender de verdad, estas son las más importantes:

### Celda 5

Porque te enseña cómo se generan los datos de entrada geométrica.

### Celda 6

Porque te enseña por qué ANMS mejora la calidad estructural del conjunto de puntos.

### Celda 11

Porque te obliga a entender qué información necesita una homografía.

### Celda 15

Porque te muestra el corazón robusto del pipeline: RANSAC.

### Celda 18

Porque junta interpretación visual y cuantitativa.

### Celda 23

Porque te deja ver la anatomía completa de la panorámica.

---

## 6. Qué tocar primero si querés mejorar resultados

Si querés experimentar, no conviene tocar todo junto.

### Si faltan keypoints

Tocá:

- `nfeatures`
- `contrast_threshold`
- `max_size`

### Si los keypoints están muy concentrados

Tocá:

- `anms_keep`
- `anms_robust`

### Si hay muchos matches absurdos

Tocá:

- `ratio`
- `cross_check`

### Si RANSAC descarta demasiado

Tocá:

- `ransac_thresh`
- `ransac_iters`

### Si la panorámica alinea bien pero las costuras se ven

Tocá:

- `blend_power`

---

## 7. Cómo pensar experimentalmente

Cuando cambies un parámetro, tratá de mirar el efecto en la celda correcta:

- cambios en SIFT -> celdas 5 y 6
- cambios en matching -> celdas 8 y 9
- cambios en RANSAC -> celdas 15, 16 y 18
- cambios en blending -> celdas 21 y 23

Eso te evita una mala práctica muy común:

**evaluar todos los parámetros solo mirando la panorámica final**.

La panorámica final es importante, pero llega demasiado tarde en el pipeline. Para entender de verdad, hay que inspeccionar las causas intermedias.

---

## 8. Qué deberías poder explicar después de estudiar este notebook

Si realmente entendiste este flujo, deberías poder explicar con tus palabras:

1. por qué usamos SIFT antes de cualquier geometría,
2. por qué ANMS ayuda aunque descarte puntos,
3. qué información agrega Lowe ratio,
4. por qué cuatro correspondencias alcanzan para DLT,
5. por qué DLT solo no alcanza en presencia de outliers,
6. qué significa geométricamente el error de reproyección,
7. cómo decide RANSAC qué matches confiar,
8. por qué hace falta calcular un canvas global,
9. qué hace `cv2.warpPerspective`,
10. por qué blending no corrige una homografía mala.

Si podés responder eso sin repetir frases memorizadas, ya no estás “usando un notebook”: estás entendiendo visión geométrica.

---

## 9. Mini checklist mental para correr el TP con criterio

Antes de correr:

- ¿las imágenes tienen solapamiento?
- ¿la imagen ancla está bien elegida?

Después de features:

- ¿hay suficientes puntos?
- ¿están distribuidos?

Después de matching:

- ¿los matches parecen plausibles?

Después de RANSAC:

- ¿hay una proporción razonable de inliers?
- ¿los outliers son realmente malos?
- ¿el histograma valida el threshold?

Después del pipeline:

- ¿las imágenes warpeadas tienen sentido?
- ¿el canvas está bien?
- ¿las máscaras solapan razonablemente?
- ¿la panorámica final presenta continuidad?

---

## 10. Cierre

La enseñanza más importante de este notebook no es solo cómo “hacer una panorámica”.

Es aprender una forma de pensar problemas de visión:

- primero encontrás evidencia local,
- después imponés una estructura geométrica,
- después robustecés frente a ruido,
- y recién al final construís una salida visual agradable.

Ese orden importa.

Si intentás entender el TP solo desde la panorámica final, te perdés lo mejor. Si lo entendés celda por celda, empezás a ver cómo se combinan:

- percepción local,
- álgebra lineal,
- geometría proyectiva,
- robustez estadística,
- y representación visual.

Y ahí aparece la verdadera comprensión.
