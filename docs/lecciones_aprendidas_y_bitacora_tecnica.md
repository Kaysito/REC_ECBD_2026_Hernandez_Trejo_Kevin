# Bitacora Tecnica: Lecciones Aprendidas, Trampas Matematicas y Errores Prevenidos

**Proyecto:** Clasificacion automatica y analisis morfologico de variedades de frijol  
**Asignatura:** Extraccion de Conocimiento en Bases de Datos (ECBD) - Recursamiento 2026  
**Estudiante:** Kevin Hernandez Trejo (Matricula: 23300950)  
**Ubicacion:** `docs/lecciones_aprendidas_y_bitacora_tecnica.md`  

---

## 1. Proposito de este Documento

Este documento recopila de manera sistematica los hallazgos analiticos, las trampas matematicas ocultas en los datos, los errores detectados y prevenidos durante el desarrollo de las Unidades I, II y III, asi como las reglas de diseno que deben preservarse para las Unidades IV (Clustering/PCA) y V (Dashboard Power BI).

---

## 2. Trampa Matematica 1: Fuga Silenciosa en la Regresion de Area (*Data Leakage*)

### El Problema Inicial
En la planeacion original se identifico correctamente que `EquivDiameter` ($Ed = \sqrt{4A/\pi}$) y `ConvexArea` (correlacion $0.9999$) debian excluirse porque calcular el area a partir de ellas seria trivial.

### El Error Detectado en la Auditoria a Fondo
Al auditar algebraicamente las 16 columnas restantes contra el `Area`, descubrimos que **otros 3 descriptores de forma tambien contienen el Area directamente en su formula matematica de extraccion**:

$$\text{ShapeFactor1} = \frac{\text{MajorAxisLength}}{\text{Area}} \quad (\text{diferencia calculada vs real: } 0.0000000000)$$

$$\text{ShapeFactor2} = \frac{\text{MinorAxisLength}}{\text{Area}}$$

$$\text{Compactness} = \frac{\text{EquivDiameter}}{\text{MajorAxisLength}} = \frac{\sqrt{4 \times \text{Area} / \pi}}{\text{MajorAxisLength}}$$

Si estos factores se dejan dentro del modelo de regresion, un modelo lineal puede despejar matematicamente el area ($\text{Area} = \frac{\text{MajorAxisLength}}{\text{ShapeFactor1}}$), arrojando un $R^2 = 0.9987$ engañoso que no predice morfologicamente la superficie, sino que simplemente invierte una division aritmetica.

### La Solucion Implementada
Se purifico estrictamente el conjunto de predictores de regresion a **10 descriptores genuinamente no derivados del area**:
- Contorno y extension: `Perimeter`, `MajorAxisLength`, `MinorAxisLength`.
- Razones de aspecto y excentricidad: `AspectRatio`, `Eccentricity`, `Extent`, `Solidity`.
- Indices de forma independientes: `Roundness`, `ShapeFactor3`, `ShapeFactor4`.

### Impacto en Resultados
- **Regresion Lineal (Honesta):** $R^2 = 0.9799$ | $MAE = 3,112.06$ px | $RMSE = 4,237.15$ px.
- **Random Forest Regressor (No Lineal):** $R^2 = 0.9997$ | $MAE = 191.79$ px | $RMSE = 527.65$ px.
*Leccion:* El modelo no lineal Random Forest reconstruye la superficie con extrema exactitud ($MAE < 200$ px) capturando la curvatura real de la semilla sin recurrir a ninguna variable con trampa de division.

---

## 3. Trampa Metodologica 2: Origen Concentrado de los 68 Duplicados

### El Hallazgo
El dataset crudo contiene 13,611 filas. El analisis de unicidad identifico 68 filas duplicadas exactas en las 17 variables.
Al desglosarlas por variedad de frijol, se revelo que:
- `BARBUNYA`: 0 duplicados
- `BOMBAY`: 0 duplicados
- `CALI`: 0 duplicados
- `DERMASON`: 0 duplicados
- **`HOROZ`**: **68 duplicados (100% de la redundancia concentrada en esta clase)**
- `SEKER`: 0 duplicados
- `SIRA`: 0 duplicados

### Riesgo Evitado
Si se realiza la particion *Train/Test* antes de limpiar, aproximadamente 13 o 14 duplicados exactos habrian caido en el conjunto de prueba habiendo sido vistos en el de entrenamiento. El clasificador recordaria el patron exacto, distorsionando el recall especifico de `HOROZ`.
*Regla permanente:* **La deduplicacion siempre debe ejecutarse como primer paso del ETL antes de cualquier particionamiento.**

---

## 4. Trampa Metodologica 3: Desbalance de Clases y Metrica Adecuada

### El Escenario
- Variedad dominante: `DERMASON` con 3,546 observaciones (26.18%).
- Variedad minoritaria: `BOMBAY` con 522 observaciones (3.85%).
- Ratio de desbalance: **6.79 a 1**.

### Riesgo Evitado
El uso exclusivo de `Accuracy` puede encubrir un mal rendimiento en clases pequenas (un clasificador tonto que prediga solo las clases mayoritarias podria obtener un Accuracy alto).
*Regla permanente:*
1. La division de datos debe ser siempre **estratificada** (`stratify=y`).
2. La metrica principal de comparacion y seleccion de clasificadores es **Macro F1-Score** (promedio no ponderado donde la clase minoritaria BOMBAY pesa exactamente lo mismo que la mayoritaria DERMASON).
3. `Accuracy` y `Weighted F1` se reportan unicamente como metricas secundarias de apoyo.

---

## 5. Trampa de Ingenieria 4: Restricciones de GitHub y Almacenamiento

### El Error Detectado
El modelo `random_forest_regresor.joblib` entrenado con 100 arboles profundos genero un archivo binario de **98.35 MB**, rozando el limite maximo absoluto de GitHub (100 MB por archivo). Un push con un archivo de 100 MB genera un bloqueo permanente del repositorio remoto.

### La Solucion
Se configuro la compresion zlib interna de `joblib`:
```python
joblib.dump(modelo, ruta, compress=3)
```
- `random_forest_regresor.joblib`: redujo de 98.35 MB a **18.98 MB** (reduccion del 80%).
- `random_forest_classifier.joblib`: redujo a **2.54 MB**.
*Regla permanente:* Todos los modelos serializados en `modelos/` deben guardarse con `compress=3` o superior.

---

## 6. Diagnostico de Confusion entre Variedades (Para la Unidad III avanzada)

Del analisis de la matriz de confusion se derivan los siguientes patrones morfológicos:
1. **Facilidad de separacion:**
   - `BOMBAY`: $100\%$ de acierto. Es la semilla mas voluminosa (area media $> 170,000$ px), geometricamente aislada de las demas.
   - `SEKER`: $> 95\%$ de acierto. Posee una redondez casi esferica ($Roundness > 0.95$) que la distingue claramente.
2. **Zona de solapamiento morfologico:**
   - `DERMASON` vs `SIRA`: Representan el $75\%$ de las clasificaciones erroneas del modelo. Ambas son variedades pequenas, aplanadas y de coloracion blanca.
   - `BARBUNYA` vs `CALI`: Comparten elongaciones y longitudes de eje mayor muy proximas.
*Estrategia para el cierre de U3:* Aplicar escalado robusto (`RobustScaler`) o tecnicas de ensamble ponderado para maximizar el margen de decision entre `DERMASON` y `SIRA`.

---

## 7. Checklist para Futuras Fases (Unidad IV y V)

- [ ] **Unidad IV (Clustering y PCA):**
  - Estandarizar previamente las 16 variables con `StandardScaler`.
  - Excluir la columna `Class` durante el ajuste de k-Means y PCA (analisis 100% no supervisado).
  - Determinar el numero optimo de clusters $k$ mediante el Metodo del Codo (Inercia) y la puntuacion Silhouette (no imponer $k=7$ de forma arbitraria).
  - Contrastar descriptivamente la distribucion de clusters contra las 7 clases registradas.
- [ ] **Unidad V (Dashboard Power BI):**
  - Conectar Power BI a las vistas creadas en el Data Mart (`vw_resumen_morfologico_variedad` y `vw_distribucion_tamano_variedad`).
  - Disenar storytelling enfocado en la separacion de clases y el perfil morfologico por variedad.
