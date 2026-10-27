"""
Modulo de Modelado Supervisado: Regresion y Clasificacion Multiclase
Asignatura: Extraccion de Conocimiento en Bases de Datos (ECBD)
Estudiante: Kevin Hernandez Trejo (23300950)
Unidad III: Analisis Supervisado (Hito de Revision Funcional)
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, f1_score, classification_report, confusion_matrix
)

PROCESSED_DATA_PATH = os.path.join("data", "processed", "dry_beans_cleaned.csv")
MODELS_DIR = "modelos"
OUTPUTS_DIR = "outputs"

def ejecutar_modelado_supervisado():
    print("=" * 70)
    print("INICIANDO ANALISIS SUPERVISADO: REGRESION Y CLASIFICACION")
    print("=" * 70)
    
    if not os.path.exists(PROCESSED_DATA_PATH):
        raise FileNotFoundError(f"No se encontro el dataset procesado en: {PROCESSED_DATA_PATH}")
        
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    
    df = pd.read_csv(PROCESSED_DATA_PATH)
    print(f"Dataset cargado: {df.shape[0]} observaciones y {df.shape[1]} columnas.\n")
    
    # =========================================================================
    # PARTE 1: MODELO DE REGRESION (Objetivo: Area continua)
    # =========================================================================
    print("-" * 70)
    print("1. MODELOS DE REGRESION (Prediccion de la variable continua 'Area')")
    print("-" * 70)
    print("Control de fuga de informacion: Se excluyen 'EquivDiameter' (relacion")
    print("matematica determinista directa) y 'ConvexArea' (envolvente redundante).")
    
    reg_features = [
        # Geometria de contorno (no derivadas de Area directamente)
        "Perimeter", "MajorAxisLength", "MinorAxisLength",
        # Proporciones de forma (adimensionales)
        "AspectRatio", "Eccentricity", "Extent", "Solidity",
        "Roundness",
        # NOTA: Se excluyen deliberadamente:
        # - EquivDiameter: sqrt(4*Area/pi) -> derivada exacta de Area
        # - ConvexArea:    correlacion 0.9999 con Area, envolvente convexo
        # - ShapeFactor1:  = MajorAxisLength / Area -> formula directa (correlacion -0.848 inversa)
        # - ShapeFactor2:  = MinorAxisLength / Area -> formula directa (correlacion -0.641)
        # - Compactness:   = EquivDiameter / MajorAxisLength -> derivada de EquivDiameter
        # Factores de forma independientes residuales
        "ShapeFactor3", "ShapeFactor4"
    ]
    
    X_reg = df[reg_features]
    y_reg = df["Area"]
    
    # Division train/test 80/20
    X_reg_train, X_reg_test, y_reg_train, y_reg_test = train_test_split(
        X_reg, y_reg, test_size=0.20, random_state=42
    )
    print(f"Conjunto Regresion: {X_reg_train.shape[0]} train, {X_reg_test.shape[0]} test.")
    
    # Modelo 1: Regresion Lineal Multiple (Baseline)
    reg_lr = Pipeline([
        ("scaler", StandardScaler()),
        ("model", LinearRegression())
    ])
    reg_lr.fit(X_reg_train, y_reg_train)
    y_pred_lr = reg_lr.predict(X_reg_test)
    
    # Modelo 2: Random Forest Regressor
    reg_rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    reg_rf.fit(X_reg_train, y_reg_train)
    y_pred_rf = reg_rf.predict(X_reg_test)
    
    # Metricas de Regresion
    metricas_reg = {
        "LinearRegression": {
            "R2": float(r2_score(y_reg_test, y_pred_lr)),
            "MAE": float(mean_absolute_error(y_reg_test, y_pred_lr)),
            "RMSE": float(np.sqrt(mean_squared_error(y_reg_test, y_pred_lr)))
        },
        "RandomForestRegressor": {
            "R2": float(r2_score(y_reg_test, y_pred_rf)),
            "MAE": float(mean_absolute_error(y_reg_test, y_pred_rf)),
            "RMSE": float(np.sqrt(mean_squared_error(y_reg_test, y_pred_rf)))
        }
    }
    
    print("\nResultados de Modelos de Regresion:")
    for modelo, m in metricas_reg.items():
        print(f" - {modelo:22s} -> R2: {m['R2']:.4f} | MAE: {m['MAE']:8.2f} px | RMSE: {m['RMSE']:8.2f} px")
        
    # Guardar modelos de regresion
    joblib.dump(reg_lr, os.path.join(MODELS_DIR, "regresion_lineal.joblib"), compress=3)
    joblib.dump(reg_rf, os.path.join(MODELS_DIR, "random_forest_regresor.joblib"), compress=3)
    
    # =========================================================================
    # PARTE 2: MODELO DE CLASIFICACION MULTICLASE (Objetivo: Class - 7 clases)
    # =========================================================================
    print("\n" + "-" * 70)
    print("2. MODELOS DE CLASIFICACION MULTICLASE (Prediccion de 'Class')")
    print("-" * 70)
    
    clf_features = [col for col in df.columns if col != "Class"]
    X_clf = df[clf_features]
    y_clf = df["Class"]
    
    # Particion estratificada obligatoria por desbalance de clases
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(
        X_clf, y_clf, test_size=0.20, random_state=42, stratify=y_clf
    )
    print(f"Conjunto Clasificacion: {X_train_c.shape[0]} train, {X_test_c.shape[0]} test (Estratificado).")
    
    # Modelos de Clasificacion
    clasificadores = {
        "Regresion_Logistica": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=42))
        ]),
        "kNN_Classifier": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", KNeighborsClassifier(n_neighbors=5))
        ]),
        "Random_Forest_Classifier": RandomForestClassifier(
            n_estimators=120, max_depth=15, random_state=42, n_jobs=-1
        )
    }
    
    resultados_clf = {}
    reportes_detallados = {}
    
    for nombre, modelo in clasificadores.items():
        print(f"Entrenando {nombre}...")
        modelo.fit(X_train_c, y_train_c)
        y_pred = modelo.predict(X_test_c)
        
        acc = accuracy_score(y_test_c, y_pred)
        macro_f1 = f1_score(y_test_c, y_pred, average="macro")
        weighted_f1 = f1_score(y_test_c, y_pred, average="weighted")
        
        resultados_clf[nombre] = {
            "Accuracy": float(acc),
            "Macro_F1": float(macro_f1),
            "Weighted_F1": float(weighted_f1)
        }
        
        reportes_detallados[nombre] = classification_report(y_test_c, y_pred, output_dict=True)
        joblib.dump(modelo, os.path.join(MODELS_DIR, f"{nombre.lower()}.joblib"), compress=3)
        
    print("\nResultados Comparativos de Clasificacion Multiclase:")
    print(f"{'Modelo':26s} | {'Accuracy':10s} | {'Macro F1':10s} | {'Weighted F1':11s}")
    print("-" * 65)
    for nombre, res in resultados_clf.items():
        print(f"{nombre:26s} | {res['Accuracy']:.4f}     | {res['Macro_F1']:.4f}     | {res['Weighted_F1']:.4f}")
        
    # Mejor modelo de clasificacion
    mejor_clf = max(resultados_clf.items(), key=lambda x: x[1]["Macro_F1"])
    print(f"\nModelo mas destacado por Macro F1: {mejor_clf[0]} (Macro F1: {mejor_clf[1]['Macro_F1']:.4f})")
    
    # Matriz de confusion del mejor modelo
    mejor_modelo_obj = clasificadores[mejor_clf[0]]
    y_pred_mejor = mejor_modelo_obj.predict(X_test_c)
    clases_ordenadas = sorted(list(df["Class"].unique()))
    cm = confusion_matrix(y_test_c, y_pred_mejor, labels=clases_ordenadas)
    
    # Exportar reporte resumen a JSON
    reporte_supervisado = {
        "regresion_area": metricas_reg,
        "clasificacion_multiclase": resultados_clf,
        "clases": clases_ordenadas,
        "matriz_confusion_mejor_modelo": {
            "modelo": mejor_clf[0],
            "matriz": cm.tolist()
        }
    }
    
    resumen_json_path = os.path.join(OUTPUTS_DIR, "evaluacion_modelos_supervisados.json")
    with open(resumen_json_path, "w", encoding="utf-8") as f:
        json.dump(reporte_supervisado, f, indent=4, ensure_ascii=False)
        
    print(f"\nReporte JSON de metricas guardado en: {resumen_json_path}")
    print("=" * 70)
    print("ENTRENAMIENTO Y EVALUACION SUPERVISADA FINALIZADA CON EXITO")
    print("=" * 70)
    
    return reporte_supervisado

if __name__ == "__main__":
    ejecutar_modelado_supervisado()
