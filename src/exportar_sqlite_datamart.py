"""Crea una copia portátil SQLite del Data Mart estrella Dry Bean.

SQL Server permanece como fuente oficial. Este archivo permite demostraciones,
consultas locales y conexión mediante ODBC sin alterar el modelo dimensional.
"""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "processed" / "dry_beans_cleaned.csv"
DB = ROOT / "data" / "datamart" / "drybean_datamart.sqlite"
BI_DIR = ROOT / "data" / "bi"


VARIEDADES = [
    (1, "BARBUNYA", "BAR", "Grano pinto moteado, mediano a grande"),
    (2, "BOMBAY", "BOM", "Grano blanco de tamaño muy grande"),
    (3, "CALI", "CAL", "Grano alargado rojizo o pardo"),
    (4, "DERMASON", "DER", "Grano blanco y plano, medio-pequeño"),
    (5, "HOROZ", "HOR", "Grano cilíndrico y alargado"),
    (6, "SEKER", "SEK", "Grano esférico y compacto"),
    (7, "SIRA", "SIR", "Grano pequeño de elevada excentricidad"),
]

TAMANOS = [
    (1, "Pequeño", 0, 45001, "Área menor a 45,001 píxeles"),
    (2, "Mediano", 45001, 70001, "Área entre 45,001 y 70,000 píxeles"),
    (3, "Grande", 70001, 110001, "Área entre 70,001 y 110,000 píxeles"),
    (4, "Muy Grande", 110001, 300001, "Área desde 110,001 píxeles"),
]

FORMAS = [
    (1, "Casi Esférica", 1.00, 1.30, "Relación de aspecto menor a 1.30"),
    (2, "Semi-Ovalada", 1.30, 1.65, "Relación de aspecto menor a 1.65"),
    (3, "Elongada", 1.65, 2.05, "Relación de aspecto menor a 2.05"),
    (4, "Muy Elongada", 2.05, 3.50, "Relación de aspecto desde 2.05"),
]


def crear_datamart() -> Path:
    df = pd.read_csv(CSV)
    if len(df) != 13_543:
        raise ValueError(f"Se esperaban 13,543 registros limpios; se encontraron {len(df):,}.")

    DB.parent.mkdir(parents=True, exist_ok=True)
    BI_DIR.mkdir(parents=True, exist_ok=True)
    if DB.exists():
        DB.unlink()

    with sqlite3.connect(DB) as con:
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript(
            """
            CREATE TABLE dim_variedad (
                id_variedad INTEGER PRIMARY KEY,
                nombre_variedad TEXT NOT NULL UNIQUE,
                codigo_variedad TEXT NOT NULL,
                descripcion_agronomica TEXT
            );
            CREATE TABLE dim_tamano (
                id_tamano INTEGER PRIMARY KEY,
                categoria_tamano TEXT NOT NULL UNIQUE,
                rango_area_min REAL NOT NULL,
                rango_area_max REAL NOT NULL,
                descripcion TEXT
            );
            CREATE TABLE dim_forma (
                id_forma INTEGER PRIMARY KEY,
                categoria_forma TEXT NOT NULL UNIQUE,
                rango_aspect_ratio_min REAL NOT NULL,
                rango_aspect_ratio_max REAL NOT NULL,
                descripcion TEXT
            );
            CREATE TABLE dim_tiempo (
                id_tiempo INTEGER PRIMARY KEY,
                fecha TEXT NOT NULL UNIQUE,
                anio INTEGER NOT NULL,
                trimestre INTEGER NOT NULL,
                mes INTEGER NOT NULL,
                nombre_mes TEXT NOT NULL,
                dia INTEGER NOT NULL,
                dia_semana INTEGER NOT NULL,
                nombre_dia TEXT NOT NULL
            );
            CREATE TABLE fact_bean_morphology (
                id_grano INTEGER PRIMARY KEY,
                id_variedad INTEGER NOT NULL REFERENCES dim_variedad(id_variedad),
                id_tamano INTEGER NOT NULL REFERENCES dim_tamano(id_tamano),
                id_forma INTEGER NOT NULL REFERENCES dim_forma(id_forma),
                id_tiempo INTEGER NOT NULL REFERENCES dim_tiempo(id_tiempo),
                area INTEGER NOT NULL,
                perimeter REAL NOT NULL,
                major_axis_length REAL NOT NULL,
                minor_axis_length REAL NOT NULL,
                convex_area INTEGER NOT NULL,
                equiv_diameter REAL NOT NULL,
                aspect_ratio REAL NOT NULL,
                eccentricity REAL NOT NULL,
                extent REAL NOT NULL,
                solidity REAL NOT NULL,
                roundness REAL NOT NULL,
                compactness REAL NOT NULL,
                shape_factor_1 REAL NOT NULL,
                shape_factor_2 REAL NOT NULL,
                shape_factor_3 REAL NOT NULL,
                shape_factor_4 REAL NOT NULL,
                fecha_carga TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX ix_fact_variedad ON fact_bean_morphology(id_variedad);
            CREATE INDEX ix_fact_tamano ON fact_bean_morphology(id_tamano);
            CREATE INDEX ix_fact_forma ON fact_bean_morphology(id_forma);
            CREATE INDEX ix_fact_tiempo ON fact_bean_morphology(id_tiempo);
            CREATE INDEX ix_fact_area ON fact_bean_morphology(area);
            """
        )
        con.executemany("INSERT INTO dim_variedad VALUES (?,?,?,?)", VARIEDADES)
        con.executemany("INSERT INTO dim_tamano VALUES (?,?,?,?,?)", TAMANOS)
        con.executemany("INSERT INTO dim_forma VALUES (?,?,?,?,?)", FORMAS)
        fecha_carga = date.today()
        id_tiempo = int(fecha_carga.strftime("%Y%m%d"))
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        con.execute(
            "INSERT INTO dim_tiempo VALUES (?,?,?,?,?,?,?,?,?)",
            (id_tiempo, fecha_carga.isoformat(), fecha_carga.year, (fecha_carga.month - 1) // 3 + 1,
             fecha_carga.month, meses[fecha_carga.month - 1], fecha_carga.day,
             fecha_carga.isoweekday(), dias[fecha_carga.weekday()]),
        )

        variedad = {nombre: clave for clave, nombre, *_ in VARIEDADES}
        id_tamano = pd.cut(
            df["Area"], bins=[-float("inf"), 45000, 70000, 110000, float("inf")],
            labels=[1, 2, 3, 4]
        ).astype(int)
        id_forma = pd.cut(
            df["AspectRatio"], bins=[-float("inf"), 1.30, 1.65, 2.05, float("inf")],
            labels=[1, 2, 3, 4], right=False
        ).astype(int)

        hechos = pd.DataFrame({
            "id_grano": range(1, len(df) + 1),
            "id_variedad": df["Class"].map(variedad),
            "id_tamano": id_tamano,
            "id_forma": id_forma,
            "id_tiempo": id_tiempo,
            "area": df["Area"],
            "perimeter": df["Perimeter"],
            "major_axis_length": df["MajorAxisLength"],
            "minor_axis_length": df["MinorAxisLength"],
            "convex_area": df["ConvexArea"],
            "equiv_diameter": df["EquivDiameter"],
            "aspect_ratio": df["AspectRatio"],
            "eccentricity": df["Eccentricity"],
            "extent": df["Extent"],
            "solidity": df["Solidity"],
            "roundness": df["Roundness"],
            "compactness": df["Compactness"],
            "shape_factor_1": df["ShapeFactor1"],
            "shape_factor_2": df["ShapeFactor2"],
            "shape_factor_3": df["ShapeFactor3"],
            "shape_factor_4": df["ShapeFactor4"],
        })
        hechos.to_sql("fact_bean_morphology", con, if_exists="append", index=False)

        con.executescript(
            """
            CREATE VIEW vw_bean_bi AS
            SELECT f.*, v.nombre_variedad AS variedad,
                   t.categoria_tamano, fo.categoria_forma,
                   ti.fecha, ti.anio, ti.trimestre, ti.mes, ti.nombre_mes,
                   ti.dia, ti.dia_semana, ti.nombre_dia
            FROM fact_bean_morphology f
            JOIN dim_variedad v USING(id_variedad)
            JOIN dim_tamano t USING(id_tamano)
            JOIN dim_forma fo USING(id_forma)
            JOIN dim_tiempo ti USING(id_tiempo);

            CREATE VIEW vw_kpi_variedad AS
            SELECT v.nombre_variedad AS variedad, COUNT(*) AS total_granos,
                   ROUND(AVG(f.area),2) AS area_promedio,
                   ROUND(AVG(f.roundness),4) AS redondez_promedio,
                   ROUND(AVG(f.compactness),4) AS compacidad_promedio
            FROM fact_bean_morphology f
            JOIN dim_variedad v USING(id_variedad)
            GROUP BY v.nombre_variedad;
            """
        )
        errores_fk = con.execute("PRAGMA foreign_key_check").fetchall()
        total = con.execute("SELECT COUNT(*) FROM fact_bean_morphology").fetchone()[0]
        if total != 13_543 or errores_fk:
            raise RuntimeError(f"Validación fallida: total={total}, errores_fk={errores_fk}")

        pd.read_sql_query("SELECT * FROM vw_bean_bi", con).to_csv(
            BI_DIR / "drybean_powerbi.csv", index=False, encoding="utf-8-sig"
        )
        pd.read_sql_query("SELECT * FROM vw_kpi_variedad", con).to_csv(
            BI_DIR / "kpi_variedad.csv", index=False, encoding="utf-8-sig"
        )

    print(f"Data Mart SQLite creado: {DB}")
    print("Hechos: 13,543 | Dimensiones: 7 variedades, 4 tamaños, 4 formas y tiempo | FK: 0 errores")
    return DB


if __name__ == "__main__":
    crear_datamart()
