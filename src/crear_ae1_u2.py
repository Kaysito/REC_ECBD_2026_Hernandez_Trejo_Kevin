"""Genera el notebook ejecutable de exploracion para la AE1 de Unidad II."""

from pathlib import Path
import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks" / "Hernandez_Trejo_Kevin_U2_AE1_Exploracion.ipynb"


def md(text):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text):
    return nbf.v4.new_code_cell(text.strip())


cells = [
    md("""
# Exploración y diagnóstico del Dry Bean Dataset

**Actividad de Evaluación 1 - Unidad II**  
**Estudiante:** Kevin Hernandez Trejo · **Matrícula:** 23300950 · **Grupo:** 10IDGS-G1  
**Proyecto:** Clasificación automática y análisis morfológico de variedades de frijol  
**Dataset:** Dry Bean Dataset · **Fuente:** UCI Machine Learning Repository  

## Propósito

Explorar el archivo original sin modificarlo, documentar su estructura y sus variables, diagnosticar su calidad, describir estadísticamente las mediciones morfológicas y proponer variables para regresión, clasificación y agrupamiento.

> Este notebook solo lee `data/raw/`. No elimina duplicados, no imputa valores y no sobrescribe el dataset original.
"""),
    md("""
## 1. Preparación del entorno y localización del archivo

Se importan Pandas para la exploración y Matplotlib/Seaborn para las gráficas. La búsqueda del directorio raíz permite ejecutar el notebook desde la carpeta del repositorio o desde `notebooks/`.
"""),
    code("""
from pathlib import Path
import hashlib
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display

sns.set_theme(style="whitegrid", palette="colorblind")
pd.set_option("display.max_columns", 30)
pd.set_option("display.float_format", lambda x: f"{x:,.6f}")

cwd = Path.cwd().resolve()
ROOT = cwd if (cwd / "data").exists() else cwd.parent
DATA_PATH = ROOT / "data" / "raw" / "dry_bean_dataset" / "DryBeanDataset" / "Dry_Bean_Dataset.xlsx"
assert DATA_PATH.exists(), f"No se encontró el dataset: {DATA_PATH}"

raw_hash_before = hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()
print(f"Archivo: {DATA_PATH.relative_to(ROOT)}")
print(f"SHA-256 inicial: {raw_hash_before}")
"""),
    md("""
**Interpretación.** La ruta apunta al Excel original dentro de `data/raw/`. La huella SHA-256 permitirá comprobar al final que el archivo permaneció sin modificaciones.
"""),
    md("""
## 2. Identificación y carga del dataset

El Dry Bean Dataset contiene mediciones obtenidas al segmentar imágenes de granos con un sistema de visión por computadora. Cada fila representa un grano; las 16 variables predictoras describen tamaño, proporción y forma, mientras `Class` identifica una de siete variedades.

- **Formato utilizado:** XLSX.
- **Fuente:** UCI Machine Learning Repository, DOI 10.24432/C50S4B.
- **Tipo de fuente:** datos biométricos/morfológicos generados por máquina a partir de imágenes.
- **Estructura:** datos estructurados en una tabla de filas y columnas.
"""),
    code("""
df = pd.read_excel(DATA_PATH)
print("Dataset cargado correctamente.")
"""),
    md("""
**Interpretación.** `pd.read_excel()` carga el libro en un `DataFrame` sin alterar el archivo. Todo el diagnóstico posterior se realiza en memoria.
"""),
    md("## 3. Exploración inicial con Pandas"),
    md("### 3.1 Primeras filas: `df.head()`"),
    code("df.head()"),
    md("""
**Interpretación.** Las primeras cinco filas confirman que las mediciones morfológicas son numéricas y que `Class` es la etiqueta categórica. Cada renglón representa un grano distinto.
"""),
    md("### 3.2 Dimensiones: `df.shape`"),
    code("df.shape"),
    md("""
**Interpretación.** El conjunto contiene **13,611 registros y 17 columnas**: 16 características morfológicas y una variable de clase.
"""),
    md("### 3.3 Nombres de columnas: `df.columns`"),
    code("df.columns"),
    md("""
**Interpretación.** Los nombres conservan la forma original de UCI. Se detectan dos detalles de nomenclatura para una etapa posterior: `AspectRation` parece un error tipográfico de *AspectRatio* y `roundness` no sigue la capitalización de las demás variables. En esta actividad no se renombran.
"""),
    md("### 3.4 Resumen estructural: `df.info()`"),
    code("""
buffer = io.StringIO()
df.info(buf=buffer)
print(buffer.getvalue())
"""),
    md("""
**Interpretación.** Las 17 columnas tienen 13,611 valores no nulos. `Area` y `ConvexArea` son enteras; 14 mediciones son `float64`; `Class` es texto. La estructura es adecuada para análisis tabular.
"""),
    md("### 3.5 Tipos de datos: `df.dtypes`"),
    code("df.dtypes"),
    md("""
**Interpretación.** Los tipos son coherentes con el significado de las variables. No se detectan números almacenados como texto ni fechas que requieran conversión.
"""),
    md("### 3.6 Estadística descriptiva general: `df.describe()`"),
    code("df.describe().T"),
    md("""
**Interpretación.** Las escalas varían ampliamente: `Area` se mide en decenas de miles de píxeles, mientras los factores de forma usan valores pequeños o proporciones entre 0 y 1. Para clustering y algoritmos sensibles a distancia será necesario estandarizar más adelante, pero aquí no se transforma nada.
"""),
    md("""
## 4. Diccionario de datos y clasificación de variables

Las descripciones se basan en la documentación oficial del dataset. Las variables numéricas son cuantitativas; `Area` y `ConvexArea` son discretas por ser conteos de píxeles, las demás mediciones se tratan como continuas y `Class` es cualitativa nominal.
"""),
    code("""
descripciones = {
    "Area": ("Número de píxeles dentro del contorno del grano", "Cuantitativa", "Discreta", "px²", "Objetivo de regresión y descriptor de tamaño"),
    "Perimeter": ("Longitud del borde del grano", "Cuantitativa", "Continua", "px", "Tamaño y forma; predictor"),
    "MajorAxisLength": ("Longitud del eje mayor de la elipse equivalente", "Cuantitativa", "Continua", "px", "Alargamiento y tamaño"),
    "MinorAxisLength": ("Longitud del eje menor perpendicular al eje mayor", "Cuantitativa", "Continua", "px", "Ancho y tamaño"),
    "AspectRation": ("Razón entre eje mayor y eje menor", "Cuantitativa", "Continua", "Adimensional", "Distinguir granos redondos y alargados"),
    "Eccentricity": ("Excentricidad de la elipse equivalente", "Cuantitativa", "Continua", "0 a <1", "Descriptor de elongación"),
    "ConvexArea": ("Píxeles del menor polígono convexo que contiene al grano", "Cuantitativa", "Discreta", "px²", "Tamaño de la envolvente convexa"),
    "EquivDiameter": ("Diámetro del círculo con la misma área", "Cuantitativa", "Continua", "px", "Tamaño equivalente; derivado de Area"),
    "Extent": ("Proporción del área respecto a la caja delimitadora", "Cuantitativa", "Continua", "0 a 1", "Ocupación espacial"),
    "Solidity": ("Proporción entre Area y ConvexArea", "Cuantitativa", "Continua", "0 a 1", "Regularidad y convexidad"),
    "roundness": ("Índice de redondez 4πArea/Perimeter²", "Cuantitativa", "Continua", "0 a 1", "Separación por circularidad"),
    "Compactness": ("Relación EquivDiameter/MajorAxisLength", "Cuantitativa", "Continua", "0 a 1", "Compacidad del grano"),
    "ShapeFactor1": ("Primer factor morfológico", "Cuantitativa", "Continua", "Adimensional", "Patrón de forma para modelado"),
    "ShapeFactor2": ("Segundo factor morfológico", "Cuantitativa", "Continua", "Adimensional", "Patrón de forma para modelado"),
    "ShapeFactor3": ("Tercer factor morfológico", "Cuantitativa", "Continua", "0 a 1", "Patrón de forma para modelado"),
    "ShapeFactor4": ("Cuarto factor morfológico", "Cuantitativa", "Continua", "0 a 1", "Patrón de forma para modelado"),
    "Class": ("Variedad registrada del frijol", "Cualitativa", "Nominal", "Categoría", "Objetivo de clasificación; contraste de clusters"),
}

diccionario = pd.DataFrame([
    {
        "Variable": c,
        "Descripción": descripciones[c][0],
        "Tipo Python": str(df[c].dtype),
        "Tipo de variable": descripciones[c][1],
        "Clasificación": descripciones[c][2],
        "Unidad": descripciones[c][3],
        "Posible utilidad": descripciones[c][4],
    }
    for c in df.columns
])
display(diccionario)
"""),
    md("""
**Interpretación.** El diccionario documenta las 17 columnas. La mayoría son mediciones continuas de forma; `Class` es la única variable cualitativa. Algunas variables son matemáticamente derivadas de otras, aspecto importante para prevenir fuga de información en regresión.
"""),
    md("## 5. Diagnóstico de calidad"),
    md("### 5.1 Valores faltantes: `df.isnull().sum()`"),
    code("""
faltantes = pd.DataFrame({
    "Faltantes": df.isnull().sum(),
    "Porcentaje": df.isnull().mean().mul(100)
})
display(faltantes)
print(f"Total de valores faltantes: {int(faltantes['Faltantes'].sum())}")
"""),
    md("""
**Interpretación.** No existen valores faltantes en ninguna columna. No se requiere imputación. Si aparecieran en futuras capturas, se evaluaría el mecanismo de ausencia antes de decidir entre imputar o excluir.
"""),
    md("### 5.2 Registros duplicados: `df.duplicated().sum()`"),
    code("""
duplicados = int(df.duplicated().sum())
print(f"Duplicados exactos: {duplicados}")
print(f"Porcentaje: {duplicados / len(df) * 100:.3f}%")
display(df[df.duplicated(keep=False)]["Class"].value_counts().rename("Filas involucradas"))
"""),
    md("""
**Interpretación.** Hay **68 duplicados exactos (0.500%)**; todas las parejas duplicadas pertenecen a `HOROZ`. Podrían deberse a repetición en la consolidación o a mediciones idénticas registradas más de una vez. En una etapa posterior se conservará una copia cruda y se deduplicará antes de dividir entrenamiento y prueba. Aquí no se elimina nada.
"""),
    md("### 5.3 Rangos, categorías y consistencia"),
    code("""
numeric = df.select_dtypes(include="number")
checks = pd.Series({
    "Valores numéricos negativos": int((numeric < 0).sum().sum()),
    "Eccentricity fuera de [0,1)": int(((df["Eccentricity"] < 0) | (df["Eccentricity"] >= 1)).sum()),
    "Extent fuera de (0,1]": int(((df["Extent"] <= 0) | (df["Extent"] > 1)).sum()),
    "Solidity fuera de (0,1]": int(((df["Solidity"] <= 0) | (df["Solidity"] > 1)).sum()),
    "roundness fuera de (0,1]": int(((df["roundness"] <= 0) | (df["roundness"] > 1)).sum()),
    "Compactness fuera de (0,1]": int(((df["Compactness"] <= 0) | (df["Compactness"] > 1)).sum()),
    "Clases vacías o con espacios": int(df["Class"].isna().sum() + (df["Class"] != df["Class"].str.strip()).sum()),
})
display(checks.to_frame("Incidencias"))
print("Clases:", sorted(df["Class"].unique()))
"""),
    md("""
**Interpretación.** No se detectan valores negativos, proporciones fuera de sus límites teóricos ni categorías vacías o inconsistentes. Los problemas identificados son los 68 duplicados y dos nombres de columnas que conviene normalizar posteriormente.
"""),
    md("## 6. Análisis estadístico inicial"),
    code("""
variables_clave = ["Area", "Perimeter", "AspectRation"]
estadisticas = df[variables_clave].agg(["mean", "median", "min", "max", "std"]).T
estadisticas.columns = ["Media", "Mediana", "Mínimo", "Máximo", "Desv. estándar"]
display(estadisticas)
"""),
    md("""
**Interpretación.** `Area` y `Perimeter` muestran medias mayores que sus medianas, señal de asimetría hacia granos grandes. `AspectRation` tiene menor dispersión relativa, pero su rango de 1.02 a 2.43 distingue granos casi redondos de otros alargados. Estas tres variables resumen tamaño, contorno y proporción.
"""),
    md("## 7. Detección inicial de valores atípicos"),
    code("""
outlier_rows = []
for col in variables_clave:
    q1, q3 = df[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    count = int(((df[col] < low) | (df[col] > high)).sum())
    outlier_rows.append([col, q1, q3, low, high, count, count / len(df) * 100])
outliers = pd.DataFrame(outlier_rows, columns=["Variable", "Q1", "Q3", "Límite inferior", "Límite superior", "Atípicos IQR", "%"])
display(outliers)

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
for ax, col in zip(axes, variables_clave):
    sns.boxplot(data=df, x=col, ax=ax, color="#66b3a6")
    ax.set_title(f"Boxplot de {col}")
    ax.set_xlabel(col)
plt.suptitle("Detección inicial de valores atípicos por regla IQR", fontweight="bold")
plt.tight_layout()
plt.show()
"""),
    md("""
**Interpretación.** La regla IQR marca 551 casos en `Area`, 500 en `Perimeter` y 473 en `AspectRation`. No son automáticamente errores: el dataset reúne siete variedades con tamaños y formas diferentes, y las mediciones permanecen positivas y físicamente coherentes. Se conservarán; después se estudiarán por clase y con métodos robustos antes de decidir cualquier tratamiento.
"""),
    md("## 8. Visualización inicial"),
    md("### 8.1 Distribución de variedades"),
    code("""
counts = df["Class"].value_counts()
plt.figure(figsize=(10, 5))
sns.barplot(x=counts.index, y=counts.values, hue=counts.index, palette="viridis", legend=False)
plt.title("Número de granos por variedad")
plt.xlabel("Variedad")
plt.ylabel("Registros")
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()
"""),
    md("""
**Interpretación.** `DERMASON` es la clase más frecuente (3,546) y `BOMBAY` la menos frecuente (522). El desbalance obliga a usar división estratificada y métricas por clase, como macro F1, en la clasificación posterior.
"""),
    md("### 8.2 Histograma de área"),
    code("""
plt.figure(figsize=(9, 5))
sns.histplot(data=df, x="Area", hue="Class", bins=45, element="step", stat="density", common_norm=False)
plt.title("Distribución del área por variedad")
plt.xlabel("Área (px²)")
plt.ylabel("Densidad")
plt.tight_layout()
plt.show()
"""),
    md("""
**Interpretación.** Las variedades ocupan zonas distintas de tamaño: `BOMBAY` concentra áreas mayores, mientras `DERMASON`, `SEKER` y `SIRA` se ubican en rangos menores con solapamiento. `Area` es informativa, pero no basta por sí sola para separar todas las clases.
"""),
    md("### 8.3 Relación entre ejes morfológicos"),
    code("""
plt.figure(figsize=(9, 6))
sns.scatterplot(data=df, x="MajorAxisLength", y="MinorAxisLength", hue="Class", s=18, alpha=0.55)
plt.title("Eje mayor frente a eje menor por variedad")
plt.xlabel("Longitud del eje mayor (px)")
plt.ylabel("Longitud del eje menor (px)")
plt.legend(title="Variedad", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()
plt.show()
"""),
    md("""
**Interpretación.** Existe una relación positiva entre ambos ejes. Algunas variedades se separan por tamaño, pero otras se superponen; por ello el modelo deberá combinar ejes con proporciones y factores de forma.
"""),
    md("### 8.4 Correlaciones entre mediciones"),
    code("""
plt.figure(figsize=(13, 10))
sns.heatmap(numeric.corr(), cmap="vlag", center=0, vmin=-1, vmax=1, square=True, cbar_kws={"label": "Correlación"})
plt.title("Matriz de correlación de variables numéricas")
plt.tight_layout()
plt.show()
"""),
    md("""
**Interpretación.** `Area`, `ConvexArea` y `EquivDiameter` están fuertemente relacionadas porque describen o derivan del tamaño. Para predecir `Area` se excluirán `EquivDiameter` y, en el modelo principal, `ConvexArea`, evitando una predicción casi determinística y fuga de información.
"""),
    md("## 9. Propuestas para análisis posteriores"),
    md("""
### Regresión

- **Objetivo:** `Area`.
- **Propósito:** estimar el tamaño en píxeles a partir de contorno, ejes y forma.
- **Entradas candidatas:** `Perimeter`, `MajorAxisLength`, `MinorAxisLength`, `AspectRation`, `Eccentricity`, `Extent`, `Solidity`, `roundness`, `Compactness` y factores de forma.
- **Control:** excluir `EquivDiameter` por derivarse directamente de `Area` y excluir/revisar `ConvexArea` por su dependencia geométrica.

### Clasificación

- **Objetivo:** `Class`.
- **Clases:** BARBUNYA, BOMBAY, CALI, DERMASON, HOROZ, SEKER y SIRA.
- **Entradas:** las 16 mediciones numéricas, con selección y evaluación para evitar redundancia.
- **Justificación:** responde directamente al objetivo de clasificación automática definido en Unidad I.

### Agrupamiento

- **Sin objetivo durante el ajuste.**
- **Variables candidatas:** `Area`, `Perimeter`, `MajorAxisLength`, `MinorAxisLength`, `AspectRation`, `Eccentricity`, `Extent`, `Solidity`, `roundness`, `Compactness` y `ShapeFactor1` a `ShapeFactor4`.
- **Preparación futura:** deduplicación y estandarización, porque las escalas son diferentes.
- **Propósito:** comprobar si surgen perfiles naturales de tamaño y forma y después contrastarlos descriptivamente con `Class`.
"""),
    md("## 10. Conclusión del diagnóstico"),
    md("""
1. **Información:** 13,611 granos con 16 mediciones morfológicas y una etiqueta de siete variedades.
2. **Calidad general:** alta; estructura consistente, tipos correctos y completitud del 100%.
3. **Problemas:** 68 duplicados exactos, desbalance de clases, nombres `AspectRation`/`roundness` no normalizados y observaciones extremas que deben estudiarse.
4. **Variables que requieren tratamiento:** nombres de columnas, todas las numéricas antes de clustering por diferencia de escalas y variables derivadas al modelar `Area`.
5. **Faltantes:** no existen.
6. **Duplicados:** sí, 68 (0.500%), asociados a `HOROZ`.
7. **Atípicos:** la regla IQR detecta casos, pero son plausibles y no se eliminan en esta actividad.
8. **Transformaciones futuras:** deduplicar en una copia procesada, normalizar nombres, separar predictores/objetivos, estandarizar cuando corresponda y codificar `Class` para ciertos algoritmos.
9. **Aptitud:** los datos son adecuados para continuar, siempre que se controle duplicación, desbalance y fuga de información.
10. **Conocimiento esperado:** variables que distinguen variedades, clases que se confunden, capacidad de estimar tamaño y existencia de grupos morfológicos naturales.
"""),
    md("## 11. Comprobación de integridad del archivo original"),
    code("""
raw_hash_after = hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()
print(f"SHA-256 inicial: {raw_hash_before}")
print(f"SHA-256 final:   {raw_hash_after}")
print("Archivo original sin cambios:", raw_hash_before == raw_hash_after)
assert raw_hash_before == raw_hash_after
"""),
    md("""
**Interpretación final.** La misma huella antes y después demuestra que el notebook solo leyó el dataset y que el archivo original permaneció intacto en `data/raw/`.

## Referencias

- UCI Machine Learning Repository. (2020). *Dry Bean* [Data set]. https://doi.org/10.24432/C50S4B
- Koklu, M., & Özkan, I. A. (2020). Multiclass classification of dry beans using computer vision and machine learning techniques. *Computers and Electronics in Agriculture, 174*, 105507. https://doi.org/10.1016/j.compag.2020.105507
"""),
]

nb = nbf.v4.new_notebook(
    cells=cells,
    metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    },
)
OUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, OUT)
print(OUT)
