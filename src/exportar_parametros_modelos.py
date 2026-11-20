"""Exporta los parámetros aprendidos por los modelos a formatos legibles."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "dry_beans_cleaned.csv"
MODELOS = ROOT / "modelos"
OUTPUTS = ROOT / "outputs"


def coeficientes_en_escala_original(pipeline, nombres):
    scaler = pipeline.named_steps["scaler"]
    model = pipeline.named_steps.get("model", pipeline.named_steps.get("clf"))
    coef = np.asarray(model.coef_)
    if coef.ndim == 1:
        coef = coef.reshape(1, -1)
    coef_original = coef / scaler.scale_
    intercepto_original = np.asarray(model.intercept_).reshape(-1) - np.sum(
        coef * scaler.mean_ / scaler.scale_, axis=1
    )
    return coef_original, intercepto_original


def exportar_parametros():
    OUTPUTS.mkdir(exist_ok=True)
    df = pd.read_csv(DATA)

    variables_regresion = [
        "Perimeter", "MajorAxisLength", "MinorAxisLength", "AspectRatio",
        "Eccentricity", "Extent", "Solidity", "Roundness",
        "ShapeFactor3", "ShapeFactor4",
    ]
    variables_clasificacion = [c for c in df.columns if c != "Class"]

    regresion = joblib.load(MODELOS / "regresion_lineal.joblib")
    coef_reg, intercepto_reg = coeficientes_en_escala_original(regresion, variables_regresion)
    tabla_reg = pd.DataFrame({"Variable": variables_regresion, "Coeficiente": coef_reg[0]})
    tabla_reg["Valor_absoluto"] = tabla_reg["Coeficiente"].abs()
    tabla_reg = tabla_reg.sort_values("Valor_absoluto", ascending=False)
    tabla_reg.to_csv(OUTPUTS / "coeficientes_regresion_lineal.csv", index=False)

    logistica = joblib.load(MODELOS / "regresion_logistica.joblib")
    coef_log, interceptos_log = coeficientes_en_escala_original(logistica, variables_clasificacion)
    clases = list(logistica.named_steps["clf"].classes_)
    filas_log = []
    for indice, clase in enumerate(clases):
        for variable, coeficiente in zip(variables_clasificacion, coef_log[indice]):
            filas_log.append({
                "Clase": clase,
                "Variable": variable,
                "Coeficiente": float(coeficiente),
                "Intercepto": float(interceptos_log[indice]),
            })
    pd.DataFrame(filas_log).to_csv(OUTPUTS / "coeficientes_regresion_logistica.csv", index=False)

    rf_clf = joblib.load(MODELOS / "random_forest_classifier.joblib")
    importancia_clf = pd.DataFrame({
        "Variable": variables_clasificacion,
        "Importancia": rf_clf.feature_importances_,
    }).sort_values("Importancia", ascending=False)
    importancia_clf.to_csv(OUTPUTS / "importancia_random_forest_clasificacion.csv", index=False)

    rf_reg = joblib.load(MODELOS / "random_forest_regresor.joblib")
    importancia_reg = pd.DataFrame({
        "Variable": variables_regresion,
        "Importancia": rf_reg.feature_importances_,
    }).sort_values("Importancia", ascending=False)
    importancia_reg.to_csv(OUTPUTS / "importancia_random_forest_regresion.csv", index=False)

    scaler_cluster = joblib.load(MODELOS / "standard_scaler_clustering.joblib")
    pca = joblib.load(MODELOS / "pca.joblib")
    kmeans = joblib.load(MODELOS / "kmeans.joblib")
    centros_originales = scaler_cluster.inverse_transform(pca.inverse_transform(kmeans.cluster_centers_))
    tabla_centros = pd.DataFrame(centros_originales, columns=variables_clasificacion)
    tabla_centros.insert(0, "Cluster", range(len(tabla_centros)))
    tabla_centros.to_csv(OUTPUTS / "centros_clusters_originales.csv", index=False)

    resumen = {
        "regresion_lineal": {
            "objetivo": "Area",
            "intercepto": float(intercepto_reg[0]),
            "formula": "Area = intercepto + suma(coeficiente_i * variable_i)",
            "escala": "Coeficientes convertidos a las unidades originales",
        },
        "regresion_logistica": {
            "objetivo": "Class",
            "clases": clases,
            "formula": "P(clase) = softmax(intercepto_clase + suma(coeficiente_clase_i * variable_i))",
        },
        "random_forest": {
            "clasificacion": "Importancia de variables por reducción promedio de impureza",
            "regresion": "Importancia de variables por reducción promedio del error",
        },
        "kmeans": {
            "clusters": int(kmeans.n_clusters),
            "representacion": "Centroides transformados de PCA a las unidades morfológicas originales",
        },
    }
    with open(OUTPUTS / "resumen_parametros_modelos.json", "w", encoding="utf-8") as archivo:
        json.dump(resumen, archivo, indent=2, ensure_ascii=False)

    print("Parámetros de regresión, clasificación y clustering exportados en outputs/.")
    return resumen


if __name__ == "__main__":
    exportar_parametros()

