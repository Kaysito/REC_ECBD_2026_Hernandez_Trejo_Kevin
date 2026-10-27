"""
Modulo de Generacion de Graficos y Evidencias Visuales
Asignatura: Extraccion de Conocimiento en Bases de Datos (ECBD)
Estudiante: Kevin Hernandez Trejo (23300950)
"""

import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
OUTPUTS_DIR = "outputs"
os.makedirs(OUTPUTS_DIR, exist_ok=True)

df = pd.read_csv(os.path.join("data", "processed", "dry_beans_cleaned.csv"))

# 1. Grafica: Distribucion de clases tras limpieza
plt.figure(figsize=(9, 5))
conteo = df["Class"].value_counts().reset_index()
conteo.columns = ["Clase", "Cantidad"]
ax = sns.barplot(data=conteo, x="Clase", y="Cantidad", hue="Clase", palette="Blues_d", legend=False)
plt.title("Distribucion de Instancias por Variedad de Frijol (Post-ETL: 13,543 granos)", fontsize=13, fontweight="bold")
plt.xlabel("Variedad Botánica (Class)", fontsize=11)
plt.ylabel("Numero de Observaciones", fontsize=11)
for p in ax.patches:
    ax.annotate(f"{int(p.get_height()):,}", (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='bottom', fontsize=10, xytext=(0, 3), textcoords='offset points')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "distribucion_clases_limpias.png"), dpi=200)
plt.close()
print("1. Grafica de distribucion guardada.")

# 2. Grafica: Evaluacion de Regresion (Real vs Predicho)
reg_features = [
    "Perimeter", "MajorAxisLength", "MinorAxisLength",
    "AspectRatio", "Eccentricity", "Extent", "Solidity",
    "Roundness", "ShapeFactor3", "ShapeFactor4"
]
X_reg = df[reg_features]
y_reg = df["Area"]
X_reg_train, X_reg_test, y_reg_train, y_reg_test = train_test_split(
    X_reg, y_reg, test_size=0.20, random_state=42
)
model_rf_reg = joblib.load(os.path.join("modelos", "random_forest_regresor.joblib"))
y_pred_rf = model_rf_reg.predict(X_reg_test)

plt.figure(figsize=(7, 6))
plt.scatter(y_reg_test, y_pred_rf, alpha=0.35, color="#1f77b4", edgecolor="none", s=18)
min_val = min(y_reg_test.min(), y_pred_rf.min())
max_val = max(y_reg_test.max(), y_pred_rf.max())
plt.plot([min_val, max_val], [min_val, max_val], "r--", linewidth=2, label="Linea de Identidad (Prediccion Perfecta)")
plt.title("Regresion de Area: Valores Reales vs Predichos (Random Forest)", fontsize=12, fontweight="bold")
plt.xlabel("Area Real (pixeles)", fontsize=11)
plt.ylabel("Area Predicha (pixeles)", fontsize=11)
plt.legend(frameon=True)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "regresion_real_vs_predicho.png"), dpi=200)
plt.close()
print("2. Grafica de regresion guardada.")

# 3. Grafica: Matriz de Confusion Clasificacion Multiclase
clf_features = [col for col in df.columns if col != "Class"]
X_clf = df[clf_features]
y_clf = df["Class"]
X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
    X_clf, y_clf, test_size=0.20, random_state=42, stratify=y_clf
)
model_rf_clf = joblib.load(os.path.join("modelos", "random_forest_classifier.joblib"))
y_pred_clf = model_rf_clf.predict(X_test_c)

clases = sorted(df["Class"].unique())
cm = confusion_matrix(y_test_c, y_pred_clf, labels=clases)

plt.figure(figsize=(8, 6.5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=clases, yticklabels=clases, cbar=True)
plt.title("Matriz de Confusion Multiclase - Random Forest (Macro F1: 93.18%)", fontsize=12, fontweight="bold")
plt.xlabel("Clase Predicha", fontsize=11)
plt.ylabel("Clase Real", fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "matriz_confusion_multiclase.png"), dpi=200)
plt.close()
print("3. Matriz de confusion guardada.")

# 4. Grafica: Comparativa de Clasificadores
metricas = pd.DataFrame({
    "Modelo": ["Reg. Logística", "k-NN (k=5)", "Random Forest"],
    "Accuracy": [0.9192, 0.9155, 0.9203],
    "Macro F1": [0.9302, 0.9270, 0.9318]
})
metricas_melt = metricas.melt(id_vars="Modelo", var_name="Metrica", value_name="Score")

plt.figure(figsize=(8, 4.5))
ax = sns.barplot(data=metricas_melt, x="Modelo", y="Score", hue="Metrica", palette=["#4c72b0", "#55a868"])
plt.ylim(0.85, 0.96)
plt.title("Comparativa de Desempeno en Clasificacion Multiclase (7 Variedades)", fontsize=12, fontweight="bold")
plt.ylabel("Puntaje", fontsize=11)
for p in ax.patches:
    ax.annotate(f"{p.get_height():.3f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='bottom', fontsize=9, xytext=(0, 2), textcoords='offset points')
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS_DIR, "comparativa_metricas_clasificacion.png"), dpi=200)
plt.close()
print("4. Grafica comparativa de modelos guardada.")
print("Todas las evidencias graficas fueron generadas exitosamente en outputs/.")
