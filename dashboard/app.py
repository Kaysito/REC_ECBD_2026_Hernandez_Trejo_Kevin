"""Dashboard interactivo del Proyecto Integrador Dry Bean."""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "dry_beans_clustered.csv"
METRICAS_SUP = ROOT / "outputs" / "evaluacion_modelos_supervisados.json"
METRICAS_UNSUP = ROOT / "outputs" / "evaluacion_modelos_no_supervisados.json"

st.set_page_config(page_title="Dry Bean | Kevin Hernández", page_icon="🫘", layout="wide")
st.markdown("""
<style>
    .block-container {padding-top: 1.5rem;}
    [data-testid="stMetric"] {background:#f5f8fa; border-left:5px solid #174a73; padding:12px; border-radius:7px;}
    h1, h2, h3 {color:#174a73;}
</style>
""", unsafe_allow_html=True)

st.title("Clasificación y análisis morfológico de variedades de frijol")
st.caption("Proyecto Integrador ECBD · Kevin Hernández Trejo · 23300950 · 10IDGS-G1")

if not DATA.exists():
    st.error("Primero ejecuta: python src/modelos_no_supervisados.py")
    st.stop()

df = pd.read_csv(DATA)
with open(METRICAS_SUP, encoding="utf-8") as f:
    supervisado = json.load(f)
with open(METRICAS_UNSUP, encoding="utf-8") as f:
    no_supervisado = json.load(f)

clases = sorted(df["Class"].unique())
seleccion = st.sidebar.multiselect("Variedades", clases, default=clases)
df_f = df[df["Class"].isin(seleccion)]
st.sidebar.markdown("**Fuente:** UCI Machine Learning Repository")
st.sidebar.info("El filtro modifica las visualizaciones, pero no reentrena los modelos.")

mejor_clf, datos_clf = max(
    supervisado["clasificacion_multiclase"].items(), key=lambda x: x[1]["Macro_F1"]
)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Registros procesados", f"{len(df):,}")
c2.metric("Variedades", df["Class"].nunique())
c3.metric("Mejor clasificador", mejor_clf.replace("_", " "))
c4.metric("Accuracy", f"{datos_clf['Accuracy']:.2%}")

tab1, tab2, tab3, tab4 = st.tabs(["Datos", "Supervisado", "No supervisado", "Trazabilidad"])

with tab1:
    left, right = st.columns(2)
    conteos = df_f["Class"].value_counts().rename_axis("Variedad").reset_index(name="Registros")
    left.plotly_chart(px.bar(conteos, x="Variedad", y="Registros", color="Variedad",
                             title="Distribución de variedades"), width="stretch")
    variable = right.selectbox("Variable morfológica", [c for c in df.select_dtypes("number").columns if c not in ["Cluster", "PC1", "PC2"]])
    right.plotly_chart(px.box(df_f, x="Class", y=variable, color="Class",
                              title=f"{variable} por variedad"), width="stretch")
    st.dataframe(df_f.head(100), width="stretch")

with tab2:
    st.subheader("Comparación de modelos de clasificación (70/30)")
    tabla_clf = pd.DataFrame(supervisado["clasificacion_multiclase"]).T.reset_index(names="Modelo")
    fig = px.bar(tabla_clf, x="Modelo", y=["Accuracy", "Macro_F1", "Weighted_F1"],
                 barmode="group", range_y=[0, 1], title="Métricas sobre el 30 % de prueba")
    st.plotly_chart(fig, width="stretch")
    st.dataframe(tabla_clf.style.format({"Accuracy":"{:.2%}", "Macro_F1":"{:.2%}", "Weighted_F1":"{:.2%}"}), width="stretch")
    st.info("El 70 % de los registros se utilizó para entrenamiento y el 30 % quedó reservado para evaluación.")

with tab3:
    k = no_supervisado["mejor_k_segun_silhouette"]
    u1, u2, u3 = st.columns(3)
    u1.metric("k seleccionado", k)
    u2.metric("Silhouette", f"{no_supervisado['silhouette_mejor_k']:.4f}")
    u3.metric("Componentes PCA (≥90 %)", no_supervisado["componentes_pca_para_90_por_ciento"])
    muestra = df_f.sample(min(5000, len(df_f)), random_state=42) if len(df_f) else df_f
    st.plotly_chart(px.scatter(muestra, x="PC1", y="PC2", color=muestra["Cluster"].astype(str),
                               hover_data=["Class"], opacity=.65,
                               title="Proyección PCA coloreada por cluster"), width="stretch")
    eval_k = pd.DataFrame(no_supervisado["evaluacion_k"])
    a, b = st.columns(2)
    a.plotly_chart(px.line(eval_k, x="k", y="inercia", markers=True, title="Método del codo"), width="stretch")
    b.plotly_chart(px.line(eval_k, x="k", y="silhouette", markers=True, title="Coeficiente de silueta"), width="stretch")
    st.caption("La variable Class no participó en K-means; solo se usa después para interpretar los grupos.")

with tab4:
    st.markdown("""
    1. El original se conserva sin cambios en `data/raw/`.
    2. El ETL elimina 68 duplicados y conserva 13,543 registros en `data/processed/`.
    3. Los modelos supervisados usan una partición 70 % entrenamiento y 30 % prueba.
    4. El análisis no supervisado estandariza, reduce dimensionalidad con PCA y agrupa con K-means.
    5. Las métricas, modelos y gráficas quedan guardados en `outputs/` y `modelos/`.
    """)
    st.code(".venv\\Scripts\\python.exe -m streamlit run dashboard\\app.py", language="powershell")
