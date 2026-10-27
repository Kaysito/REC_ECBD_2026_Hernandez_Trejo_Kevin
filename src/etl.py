"""
Modulo ETL para la preparacion y limpieza del Dry Bean Dataset
Asignatura: Extraccion de Conocimiento en Bases de Datos (ECBD)
Estudiante: Kevin Hernandez Trejo (23300950)
Unidad II: Preparacion de los datos
"""

import os
import json
import pandas as pd
import numpy as np

RAW_DATA_PATH = os.path.join("data", "raw", "dry_bean_dataset", "DryBeanDataset", "Dry_Bean_Dataset.xlsx")
PROCESSED_DATA_PATH = os.path.join("data", "processed", "dry_beans_cleaned.csv")
SUMMARY_PATH = os.path.join("data", "processed", "etl_summary.json")

def ejecutar_etl():
    print("=" * 60)
    print("INICIANDO PROCESO ETL - DRY BEAN DATASET")
    print("=" * 60)
    
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"No se encontro el archivo original en: {RAW_DATA_PATH}")
    
    print(f"1. Cargando datos originales desde: {RAW_DATA_PATH}")
    df_raw = pd.read_excel(RAW_DATA_PATH)
    filas_iniciales, cols_iniciales = df_raw.shape
    print(f"   -> Dimensiones iniciales: {filas_iniciales} filas x {cols_iniciales} columnas")
    
    # 2. Verificacion de valores nulos / faltantes
    nulos_totales = df_raw.isnull().sum().sum()
    print(f"2. Verificacion de valores faltantes: {nulos_totales} nulos detectados.")
    
    # 3. Deteccion y eliminacion de duplicados exactos
    duplicados_exactos = df_raw.duplicated().sum()
    print(f"3. Deteccion de duplicados exactos: {duplicados_exactos} filas duplicadas encontradas.")
    
    df_cleaned = df_raw.drop_duplicates().copy()
    filas_limpias, cols_limpias = df_cleaned.shape
    print(f"   -> Filas despues de deduplicacion: {filas_limpias} filas")
    
    # 4. Normalizacion de nombres de columnas
    rename_cols = {
        "AspectRation": "AspectRatio",
        "roundness": "Roundness"
    }
    df_cleaned = df_cleaned.rename(columns=rename_cols)
    print(f"4. Nombres de columnas estandarizados: {list(rename_cols.keys())} -> {list(rename_cols.values())}")
    
    # 5. Distribucion por clase
    dist_clases = df_cleaned["Class"].value_counts().to_dict()
    print("5. Distribucion de instancias por clase (limpias):")
    for clase, cant in dist_clases.items():
        print(f"   - {clase:10s}: {cant:5d} registros ({cant / filas_limpias * 100:.2f}%)")
        
    # 6. Exportacion de datos limpios
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    df_cleaned.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"6. Dataset limpio guardado en: {PROCESSED_DATA_PATH}")
    
    # 7. Resumen de metadatos del ETL
    resumen = {
        "dataset_nombre": "Dry Bean Dataset",
        "filas_originales": filas_iniciales,
        "columnas_originales": cols_iniciales,
        "valores_faltantes": int(nulos_totales),
        "duplicados_removidos": int(duplicados_exactos),
        "filas_procesadas": filas_limpias,
        "columnas_procesadas": cols_limpias,
        "distribucion_clases": dist_clases,
        "columnas_normalizadas": rename_cols,
        "columnas_finales": list(df_cleaned.columns)
    }
    
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=4, ensure_ascii=False)
    print(f"7. Metadatos de auditoria exportados a: {SUMMARY_PATH}")
    print("=" * 60)
    print("ETL COMPLETADO CON EXITO")
    print("=" * 60)
    return df_cleaned

if __name__ == "__main__":
    ejecutar_etl()
