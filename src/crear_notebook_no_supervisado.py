"""Genera el notebook didactico y ejecutable de la Unidad IV."""

from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
salida = ROOT / "notebooks" / "03_modelos_no_supervisados.ipynb"
nb = nbf.v4.new_notebook()
nb["metadata"]["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nb["metadata"]["language_info"] = {"name": "python", "version": "3"}

nb["cells"] = [
    nbf.v4.new_markdown_cell("""# Unidad IV — Análisis no supervisado

**Estudiante:** Kevin Hernández Trejo · **Matrícula:** 23300950 · **Grupo:** 10IDGS-G1  
**Proyecto:** Clasificación automática y análisis morfológico de variedades de frijol

Objetivo: descubrir agrupaciones naturales sin utilizar `Class` para entrenar. Se aplica estandarización, PCA, K-means, método del codo y coeficiente de silueta."""),
    nbf.v4.new_code_cell("""from pathlib import Path
import sys, json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()
sys.path.insert(0, str(ROOT))
from src.modelos_no_supervisados import ejecutar_modelado_no_supervisado
print('Raíz del proyecto:', ROOT)"""),
    nbf.v4.new_markdown_cell("""## 1. Ejecutar el análisis completo

Esta celda trabaja con el dataset procesado. `Class` queda excluida de las variables de entrada de K-means y solo se utiliza al final como referencia interpretativa."""),
    nbf.v4.new_code_cell("""%cd $ROOT
resumen = ejecutar_modelado_no_supervisado()"""),
    nbf.v4.new_markdown_cell("""## 2. ¿Por qué estandarizar?

Las variables tienen escalas diferentes. `Area` puede medir decenas de miles y otras variables están entre cero y uno. `StandardScaler` evita que las variables de mayor magnitud dominen las distancias de K-means."""),
    nbf.v4.new_code_cell("""evaluacion_k = pd.DataFrame(resumen['evaluacion_k'])
evaluacion_k"""),
    nbf.v4.new_markdown_cell("""## 3. Selección del número de grupos

- **Inercia:** suma de distancias internas; disminuye al aumentar `k`. Se busca un codo.
- **Silhouette:** combina cohesión y separación; cuanto más cerca de 1, mejor.
- Se selecciona el `k` con mayor silhouette entre 2 y 10. Esto es una decisión basada en los datos, no en conocer previamente las siete clases."""),
    nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(12,4))
axes[0].plot(evaluacion_k['k'], evaluacion_k['inercia'], marker='o')
axes[0].set(title='Método del codo', xlabel='k', ylabel='Inercia')
axes[1].plot(evaluacion_k['k'], evaluacion_k['silhouette'], marker='o', color='#009688')
axes[1].set(title='Coeficiente de silueta', xlabel='k', ylabel='Silhouette')
plt.tight_layout(); plt.show()
print('Mejor k:', resumen['mejor_k_segun_silhouette'])"""),
    nbf.v4.new_markdown_cell("""## 4. PCA

PCA transforma las variables correlacionadas en componentes que concentran la información. Aquí se conservan los componentes necesarios para explicar al menos 90 % de la varianza; los dos primeros permiten visualizar los grupos."""),
    nbf.v4.new_code_cell("""df_cluster = pd.read_csv(ROOT / 'data/processed/dry_beans_clustered.csv')
print('Componentes para >=90%:', resumen['componentes_pca_para_90_por_ciento'])
print('Varianza acumulada:', f\"{resumen['varianza_explicada_acumulada']:.2%}\")
df_cluster[['PC1','PC2','Cluster','Class']].head()"""),
    nbf.v4.new_code_cell("""muestra = df_cluster.sample(5000, random_state=42)
plt.figure(figsize=(10,7))
sns.scatterplot(data=muestra, x='PC1', y='PC2', hue='Cluster', palette='tab10', s=20, alpha=.65)
plt.title('Clusters K-means proyectados en PCA'); plt.show()"""),
    nbf.v4.new_markdown_cell("""## 5. Comparación interpretativa con las clases

La tabla cruzada **no entrena** el algoritmo. Sirve para observar qué variedades aparecen dentro de cada grupo. ARI y NMI comparan ambas particiones; valores moderados indican que los grupos morfológicos no equivalen exactamente a las etiquetas botánicas."""),
    nbf.v4.new_code_cell("""tabla = pd.crosstab(df_cluster['Cluster'], df_cluster['Class'])
display(tabla)
display(pd.DataFrame([resumen['comparacion_externa_solo_interpretativa']]))"""),
    nbf.v4.new_markdown_cell("""## Conclusión

K-means encontró grupos naturales basados exclusivamente en características numéricas. El mejor `k` se eligió por silhouette. Que el resultado no sea necesariamente siete es válido: una clase botánica puede compartir forma con otra y una misma variedad puede contener variación morfológica. El agrupamiento complementa la clasificación supervisada, pero no la sustituye.""")
]

salida.parent.mkdir(exist_ok=True)
nbf.write(nb, salida)
print(salida)
