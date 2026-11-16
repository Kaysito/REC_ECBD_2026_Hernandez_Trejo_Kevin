"""Dashboard interactivo del Proyecto Integrador Dry Bean."""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Traducción de presentación: conserva intactos archivos y nombres del modelo.
ETIQUETAS = dict(zip(
    ['Area','Perimeter','MajorAxisLength','MinorAxisLength','AspectRatio','Eccentricity','ConvexArea','EquivDiameter','Extent','Solidity','Roundness','Compactness','ShapeFactor1','ShapeFactor2','ShapeFactor3','ShapeFactor4','Class','Cluster','PC1','PC2'],
    ['Área','Perímetro','Longitud del eje mayor','Longitud del eje menor','Relación de aspecto','Excentricidad','Área convexa','Diámetro equivalente','Ocupación del rectángulo','Solidez','Redondez','Compacidad','Factor de forma 1','Factor de forma 2','Factor de forma 3','Factor de forma 4','Variedad','Grupo','Componente principal 1','Componente principal 2']))
px.defaults.template = 'plotly_white'
px.defaults.color_discrete_sequence = ['#165DAD','#C45100','#087F72','#763C9F','#AC2450','#596B12','#39465E']
px.defaults.labels = ETIQUETAS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "dry_beans_clustered.csv"
METRICAS_SUP = ROOT / "outputs" / "evaluacion_modelos_supervisados.json"
METRICAS_UNSUP = ROOT / "outputs" / "evaluacion_modelos_no_supervisados.json"

st.set_page_config(page_title="Dry Bean | Kevin Hernández", page_icon="🫘", layout="wide")
st.markdown("""
<style>
    .stApp {background:#F3F6FA; color:#172B42;}
    .block-container {padding-top: 2.5rem; max-width:1500px;}
    [data-testid="stSidebar"] {background:#E5EDF5; color:#172B42;}
    [data-testid="stMetric"] {background:#FFFFFF; color:#172B42; border:1px solid #CBD7E4; border-top:4px solid #165DAD; padding:20px; border-radius:12px; box-shadow:0 3px 12px #172b4208;}
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {color:#172B42;}
    h1, h2, h3 {color:#103C65;}
    .stTabs [role="tab"] {color:#172B42; font-weight:600; padding:14px 20px;}
    .stTabs [aria-selected="true"] {background:#DCEBFA; color:#103C65; border-radius:8px;}
</style>
""", unsafe_allow_html=True)

st.title("Clasificación y análisis morfológico de variedades de frijol")
st.caption("Proyecto Integrador ECBD · Kevin Hernández Trejo · 23300950 · 10IDGS-G1")
st.markdown('**De las medidas a las variedades.** Explora la forma de los frijoles, compara modelos y descubre agrupaciones naturales.')

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
traducir = st.sidebar.toggle('Mostrar nombres en español', value=True)
st.sidebar.caption('Traducción visual local · sin costo de API · archivos originales intactos')
if not seleccion:
    st.info('Selecciona al menos una variedad para explorar los datos.')
    st.stop()
st.sidebar.markdown("**Fuente:** UCI Machine Learning Repository")
st.sidebar.info("El filtro modifica las visualizaciones, pero no reentrena los modelos.")

mejor_clf, datos_clf = max(
    supervisado["clasificacion_multiclase"].items(), key=lambda x: x[1]["Macro_F1"]
)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Registros procesados", f"{len(df):,}")
c2.metric("Variedades", df["Class"].nunique())
c3.metric("Mejor clasificador", mejor_clf.replace("_", " "))
c4.metric("Exactitud en prueba", f"{datos_clf['Accuracy']:.2%}")

tab1, tab2, tab3, tab4 = st.tabs(["Datos", "Supervisado", "No supervisado", "Trazabilidad"])

with tab1:
    left, right = st.columns(2)
    conteos = df_f["Class"].value_counts().rename_axis("Variedad").reset_index(name="Registros")
    left.plotly_chart(px.bar(conteos, x="Variedad", y="Registros", color="Variedad",
                             title="Distribución de variedades"), width="stretch")
    variable = right.selectbox("Variable morfológica", [c for c in df.select_dtypes("number").columns if c not in ["Cluster", "PC1", "PC2"]], format_func=lambda c: ETIQUETAS.get(c,c) if traducir else c)
    right.plotly_chart(px.box(df_f, x="Class", y=variable, color="Class",
                              title=f"{variable} por variedad"), width="stretch")
    st.caption('Cómo explicarlo: las barras cuentan frijoles por variedad; las cajas comparan la mediana, dispersión y posibles valores extremos de cada medida.')
    st.dataframe(df_f.head(100).rename(columns=ETIQUETAS) if traducir else df_f.head(100), width="stretch")
    with st.expander('Diccionario bilingüe para la exposición'):
        st.dataframe(pd.DataFrame([{'Nombre original':k,'Significado en español':v} for k,v in ETIQUETAS.items()]), hide_index=True, width='stretch')

with tab2:
    st.subheader("Comparación de modelos de clasificación (70/30)")
    tabla_clf = pd.DataFrame(supervisado["clasificacion_multiclase"]).T.reset_index(names="Modelo")
    fig = px.bar(tabla_clf, x="Modelo", y=["Accuracy", "Macro_F1", "Weighted_F1"],
                 barmode="group", range_y=[0, 1], title="Métricas sobre el 30 % de prueba")
    st.plotly_chart(fig, width="stretch")
    st.dataframe(tabla_clf.style.format({"Accuracy":"{:.2%}", "Macro_F1":"{:.2%}", "Weighted_F1":"{:.2%}"}), width="stretch")
    st.info("El 70 % de los registros se utilizó para entrenamiento y el 30 % quedó reservado para evaluación.")
    st.caption('Exactitud: proporción total de aciertos. F1 macro: promedio del F1 de las siete variedades, dando el mismo peso a cada una. F1 ponderado: considera cuántos registros tiene cada variedad.')

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
