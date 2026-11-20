"""Dashboard interactivo del Proyecto Integrador Dry Bean."""

import json
import sqlite3
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
DATAMART = ROOT / "data" / "datamart" / "drybean_datamart.sqlite"
METRICAS_SUP = ROOT / "outputs" / "evaluacion_modelos_supervisados.json"
METRICAS_UNSUP = ROOT / "outputs" / "evaluacion_modelos_no_supervisados.json"
PARAMETROS = ROOT / "outputs" / "resumen_parametros_modelos.json"

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
    .hero {background:linear-gradient(120deg,#103C65,#165DAD 62%,#087F72); color:white; padding:24px 28px; border-radius:16px; margin-bottom:18px; box-shadow:0 8px 24px #103c6528;}
    .hero h2,.hero p {color:white; margin:0;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h2>Inteligencia morfológica del frijol</h2><p>Data Mart estrella · Modelos predictivos · Indicadores ejecutivos</p></div>', unsafe_allow_html=True)
st.caption("Proyecto Integrador ECBD · Kevin Hernández Trejo · 23300950 · 10IDGS-G1")

if not DATA.exists() or not DATAMART.exists():
    st.error("Primero ejecuta los modelos y después: python src/exportar_sqlite_datamart.py")
    st.stop()

@st.cache_data
def cargar_datamart() -> pd.DataFrame:
    with sqlite3.connect(DATAMART) as con:
        base = pd.read_sql_query("SELECT * FROM vw_bean_bi", con)
    clusters = pd.read_csv(DATA, usecols=["Cluster", "PC1", "PC2"])
    return pd.concat([base.reset_index(drop=True), clusters.reset_index(drop=True)], axis=1)

df = cargar_datamart()
with open(METRICAS_SUP, encoding="utf-8") as f:
    supervisado = json.load(f)
with open(METRICAS_UNSUP, encoding="utf-8") as f:
    no_supervisado = json.load(f)

clases = sorted(df["variedad"].unique())
seleccion = st.sidebar.multiselect("Variedades", clases, default=clases)
df_f = df[df["variedad"].isin(seleccion)]
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
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Granos seleccionados", f"{len(df_f):,}", f"{len(df_f)/len(df):.1%} del total")
c2.metric("Variedades", df_f["variedad"].nunique())
c3.metric("Área promedio", f"{df_f['area'].mean():,.0f}")
c4.metric("Redondez promedio", f"{df_f['roundness'].mean():.3f}")
c5.metric("Exactitud modelo", f"{datos_clf['Accuracy']:.2%}")

tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs(["Resumen ejecutivo", "Datos", "Supervisado", "No supervisado", "Modelos", "Trazabilidad"])

with tab0:
    izquierda, derecha = st.columns([1.15, 1])
    resumen = df_f.groupby("variedad", as_index=False).agg(
        Registros=("id_grano", "count"), Area_promedio=("area", "mean"),
        Redondez=("roundness", "mean"), Compacidad=("compactness", "mean")
    )
    izquierda.plotly_chart(px.treemap(resumen, path=["variedad"], values="Registros", color="Area_promedio",
                                      color_continuous_scale="Blues", title="Participación y área promedio por variedad"), width="stretch")
    matriz = pd.crosstab(df_f["categoria_tamano"], df_f["categoria_forma"])
    derecha.plotly_chart(px.imshow(matriz, text_auto=True, color_continuous_scale="Teal",
                                   title="Cantidad por tamaño y forma", aspect="auto"), width="stretch")
    dominante = resumen.loc[resumen["Registros"].idxmax(), "variedad"]
    st.info(f"Lectura ejecutiva: **{dominante}** es la variedad con más registros en la selección. El Data Mart mantiene relaciones válidas entre variedad, tamaño, forma y las 16 mediciones morfológicas.")

with tab1:
    left, right = st.columns(2)
    conteos = df_f["variedad"].value_counts().rename_axis("Variedad").reset_index(name="Registros")
    left.plotly_chart(px.bar(conteos, x="Variedad", y="Registros", color="Variedad",
                             title="Distribución de variedades"), width="stretch")
    variable = right.selectbox("Variable morfológica", [c for c in ["area","perimeter","major_axis_length","minor_axis_length","aspect_ratio","eccentricity","extent","solidity","roundness","compactness"]], format_func=lambda c: c.replace("_", " ").title())
    right.plotly_chart(px.box(df_f, x="variedad", y=variable, color="variedad",
                              title=f"{variable} por variedad"), width="stretch")
    st.caption('Cómo explicarlo: las barras cuentan frijoles por variedad; las cajas comparan la mediana, dispersión y posibles valores extremos de cada medida.')
    st.dataframe(df_f.head(100), width="stretch")
    with st.expander('Diccionario bilingüe para la exposición'):
        st.dataframe(pd.DataFrame([{'Nombre original':k,'Significado en español':v} for k,v in ETIQUETAS.items()]), hide_index=True, width='stretch')

with tab2:
    st.subheader("Regresión de área (70/30)")
    tabla_reg = pd.DataFrame(supervisado["regresion_area"]).T.reset_index(names="Modelo")
    r1, r2 = st.columns([1.15, 1])
    r1.plotly_chart(px.bar(tabla_reg, x="Modelo", y="R2", color="Modelo",
                           range_y=[0.95, 1], title="R² en el 30 % reservado para prueba"), width="stretch")
    r2.dataframe(tabla_reg.style.format({"R2":"{:.4f}", "MAE":"{:,.2f}", "RMSE":"{:,.2f}"}),
                 hide_index=True, width="stretch")
    mejor_reg = tabla_reg.loc[tabla_reg["R2"].idxmax()]
    st.info(f"Random Forest obtiene R²={mejor_reg['R2']:.4f} y MAE={mejor_reg['MAE']:,.2f} píxeles. La regresión estima Area sin usar EquivDiameter, ConvexArea ni factores derivados directamente del área.")

    st.subheader("Clasificación de variedades (70/30)")
    tabla_clf = pd.DataFrame(supervisado["clasificacion_multiclase"]).T.reset_index(names="Modelo")
    fig = px.bar(tabla_clf, x="Modelo", y=["Accuracy", "Macro_Precision", "Macro_Recall", "Macro_F1"],
                 barmode="group", range_y=[0, 1], title="Métricas sobre el 30 % de prueba")
    st.plotly_chart(fig, width="stretch")
    st.dataframe(tabla_clf.style.format({c:"{:.2%}" for c in tabla_clf.columns if c != "Modelo"}), width="stretch")
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
                               hover_data=["variedad"], opacity=.65,
                               title="Proyección PCA coloreada por cluster"), width="stretch")
    eval_k = pd.DataFrame(no_supervisado["evaluacion_k"])
    a, b = st.columns(2)
    a.plotly_chart(px.line(eval_k, x="k", y="inercia", markers=True, title="Método del codo"), width="stretch")
    b.plotly_chart(px.line(eval_k, x="k", y="silhouette", markers=True, title="Coeficiente de silueta"), width="stretch")
    perfiles = pd.DataFrame(no_supervisado["perfiles_clusters"]).T
    perfiles.index.name = "Cluster"
    st.subheader("Características promedio de los clusters")
    st.dataframe(perfiles.style.format({c:"{:,.4f}" for c in perfiles.columns if c != "Registros"}), width="stretch")
    st.info("Los clusters representan perfiles morfológicos, no variedades oficiales. Se interpretan comparando tamaño, elongación, redondez, compacidad y solidez promedio.")
    st.caption("La variable Class no participó en K-means; solo se usa después para interpretar los grupos.")

with tab4:
    st.subheader("Parámetros aprendidos por los modelos")
    with open(PARAMETROS, encoding="utf-8") as f:
        parametros = json.load(f)

    st.markdown("**Regresión lineal múltiple**")
    st.code(
        f"Area = {parametros['regresion_lineal']['intercepto']:.6f} + suma(coeficiente_i × variable_i)",
        language="text",
    )
    coef_reg = pd.read_csv(ROOT / "outputs" / "coeficientes_regresion_lineal.csv")
    st.dataframe(coef_reg[["Variable", "Coeficiente"]].style.format({"Coeficiente":"{:.8f}"}),
                 hide_index=True, width="stretch")
    st.caption("Los coeficientes están expresados en las unidades originales. El signo indica la dirección del efecto, manteniendo constantes las demás variables.")

    izquierda, derecha = st.columns(2)
    importancia = pd.read_csv(ROOT / "outputs" / "importancia_random_forest_clasificacion.csv").head(10)
    izquierda.plotly_chart(px.bar(importancia.sort_values("Importancia"), x="Importancia", y="Variable",
                                   orientation="h", title="Variables relevantes para clasificar"), width="stretch")
    coef_log = pd.read_csv(ROOT / "outputs" / "coeficientes_regresion_logistica.csv")
    clase_modelo = derecha.selectbox("Coeficientes de la clase", sorted(coef_log["Clase"].unique()))
    derecha.dataframe(coef_log[coef_log["Clase"] == clase_modelo][["Variable", "Coeficiente"]]
                       .sort_values("Coeficiente", key=lambda s: s.abs(), ascending=False).head(10)
                       .style.format({"Coeficiente":"{:.8f}"}), hide_index=True, width="stretch")

    st.markdown("**Centroides de K-Means en las unidades originales**")
    centros = pd.read_csv(ROOT / "outputs" / "centros_clusters_originales.csv")
    columnas_centro = ["Cluster", "Area", "Perimeter", "AspectRatio", "Roundness", "Compactness", "Solidity"]
    st.dataframe(centros[columnas_centro].style.format({c:"{:,.4f}" for c in columnas_centro if c != "Cluster"}),
                 hide_index=True, width="stretch")
    st.info("Regresión logística clasifica la variedad, la regresión estima Area y K-Means descubre tres perfiles sin utilizar Class.")

with tab5:
    st.markdown("""
    1. El original se conserva sin cambios en `data/raw/`.
    2. El ETL elimina 68 duplicados y conserva 13,543 registros en `data/processed/`.
    3. Los modelos supervisados usan una partición 70 % entrenamiento y 30 % prueba.
    4. El análisis no supervisado estandariza, reduce dimensionalidad con PCA y agrupa con K-means.
    5. Las métricas, modelos y gráficas quedan guardados en `outputs/` y `modelos/`.
    6. SQL Server sigue siendo la fuente oficial; SQLite conserva una copia portátil del mismo esquema estrella.
    """)
    st.success("Data Mart SQLite activo · 13,543 hechos · 7 variedades · 4 tamaños · 4 formas · 0 claves inválidas")
    st.code(".venv\\Scripts\\python.exe -m streamlit run dashboard\\app.py", language="powershell")
