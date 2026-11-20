"""Genera el proyecto PbixProj que se compila como plantilla Power BI (.pbit)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "powerbi" / "DryBean_Dashboard_PbixProj"
THEME = Path(r"C:\Users\crepe\AppData\Local\Temp\pbi-sample\pbix\StaticResources\SharedResources\BaseThemes\CY19SU12.json")
PROJECT = "DryBean_ECBD_Kevin"

TABLES = {
    "DryBean_Analitica": {
        "columns": [
            ("id_grano", "int64"), ("id_variedad", "int64"), ("id_tamano", "int64"),
            ("id_forma", "int64"), ("id_tiempo", "int64"), ("area", "int64"), ("perimeter", "double"),
            ("major_axis_length", "double"), ("minor_axis_length", "double"),
            ("convex_area", "int64"), ("equiv_diameter", "double"),
            ("aspect_ratio", "double"), ("eccentricity", "double"),
            ("extent", "double"), ("solidity", "double"), ("roundness", "double"),
            ("compactness", "double"), ("shape_factor_1", "double"),
            ("shape_factor_2", "double"), ("shape_factor_3", "double"),
            ("shape_factor_4", "double"), ("fecha_carga", "string"),
            ("variedad", "string"), ("categoria_tamano", "string"),
            ("categoria_forma", "string"), ("fecha", "string"), ("anio", "int64"),
            ("trimestre", "int64"), ("mes", "int64"), ("nombre_mes", "string"),
            ("dia", "int64"), ("dia_semana", "int64"), ("nombre_dia", "string"),
        ],
        "measures": [
            ("Total Granos", "COUNTROWS ( DryBean_Analitica )", "#,0"),
            ("Variedades Analizadas", "DISTINCTCOUNT ( DryBean_Analitica[variedad] )", "0"),
            ("Area Promedio", "AVERAGE ( DryBean_Analitica[area] )", "#,0"),
            ("Perimetro Promedio", "AVERAGE ( DryBean_Analitica[perimeter] )", "#,0.00"),
            ("Redondez Promedio", "AVERAGE ( DryBean_Analitica[roundness] )", "0.000"),
            ("Compacidad Promedio", "AVERAGE ( DryBean_Analitica[compactness] )", "0.000"),
            ("Solidez Promedio", "AVERAGE ( DryBean_Analitica[solidity] )", "0.000"),
            ("Area Minima", "MIN ( DryBean_Analitica[area] )", "#,0"),
            ("Area Maxima", "MAX ( DryBean_Analitica[area] )", "#,0"),
        ],
    },
}

RELATIONSHIPS = []

M_TYPES = {"int64": "Int64.Type", "string": "Text.Type", "double": "type number"}
PBI_TYPES = {"int64": "int64", "string": "string", "double": "double"}


def jwrite(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_root() -> None:
    jwrite(OUT / ".pbixproj.json", {"version": "1.0", "settings": {"model": {"serializationMode": "Default"}}})
    (OUT / "Version.txt").write_text("1.25", encoding="utf-8")
    jwrite(OUT / "ReportMetadata.json", {"Version": 5, "AutoCreatedRelationships": [], "FileDescription": "Dry Bean ECBD", "CreatedFrom": "Cloud", "CreatedFromRelease": "2021.11"})
    jwrite(OUT / "ReportSettings.json", {"Version": 1, "ReportSettings": {}, "QueriesSettings": {"TypeDetectionEnabled": True, "RelationshipImportEnabled": True, "RunBackgroundAnalysis": True, "Version": "2.81.5831.821"}})
    jwrite(OUT / "DiagramLayout.json", {
        "version": "1.1.0", "diagrams": [{"ordinal": 0, "scrollPosition": {"x": 0, "y": 0},
        "nodes": [{"location": {"x": 40 + 260 * i, "y": 40}, "nodeIndex": t,
                   "size": {"height": 260, "width": 220}, "zIndex": i + 1}
                  for i, t in enumerate(TABLES)], "name": "Modelo estrella", "zoomValue": 85,
        "pinKeyFieldsToTop": True, "showExtraHeaderInfo": False, "hideKeyFieldsWhenCollapsed": False}],
        "selectedDiagram": "Modelo estrella", "defaultDiagram": "Modelo estrella"})


def write_model() -> None:
    jwrite(OUT / "Model" / "database.json", {
        "name": PROJECT, "compatibilityLevel": 1550,
        "model": {"culture": "es-MX", "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
                  "defaultPowerBIDataSourceVersion": "powerBI_V3", "sourceQueryCulture": "es-MX",
                  "relationships": [{"name": n, "fromTable": ft, "fromColumn": fc, "toTable": tt, "toColumn": tc}
                                    for n, ft, fc, tt, tc in RELATIONSHIPS],
                  "annotations": [{"name": "__PBI_TimeIntelligenceEnabled", "value": "0"},
                                  {"name": "PBIDesktopVersion", "value": "2.159.1231.0 (26.10)"},
                                  {"name": "PBI_QueryOrder", "value": json.dumps(list(TABLES), separators=(",", ":"))}]}}
    )
    for table, spec in TABLES.items():
        tdir = OUT / "Model" / "tables" / table
        jwrite(tdir / "table.json", {"name": table})
        for col, dtype in spec["columns"]:
            jwrite(tdir / "columns" / f"{col}.json", {
                "name": col, "dataType": PBI_TYPES[dtype], "sourceColumn": col,
                "summarizeBy": "sum" if table.startswith("fact_") and dtype in {"int64", "double"} and not col.startswith("id_") else "none",
                "annotations": [{"name": "SummarizationSetBy", "value": "User"}]})
        for name, dax, fmt in spec["measures"]:
            mdir = tdir / "measures"; mdir.mkdir(parents=True, exist_ok=True)
            (mdir / f"{name}.dax").write_text(dax + "\n", encoding="utf-8")
            (mdir / f"{name}.xml").write_text(f'<Measure Name="{name}">\n  <FormatString>{fmt}</FormatString>\n</Measure>', encoding="utf-8")

        typed = ",\n            ".join(f'{{"{c}", {M_TYPES[d]}}}' for c, d in spec["columns"])
        sql_query = ("SELECT f.id_grano, f.id_variedad, f.id_tamano, f.id_forma, f.id_tiempo, f.area, f.perimeter, "
                     "f.major_axis_length, f.minor_axis_length, f.convex_area, f.equiv_diameter, "
                     "f.aspect_ratio, f.eccentricity, f.extent, f.solidity, f.roundness, f.compactness, "
                     "f.shape_factor_1, f.shape_factor_2, f.shape_factor_3, f.shape_factor_4, "
                     "CONVERT(varchar(19), f.fecha_carga, 120) AS fecha_carga, "
                     "v.nombre_variedad AS variedad, t.categoria_tamano, fo.categoria_forma, "
                     "CONVERT(varchar(10), ti.fecha, 23) AS fecha, ti.anio, ti.trimestre, ti.mes, "
                     "ti.nombre_mes, ti.dia, ti.dia_semana, ti.nombre_dia "
                     "FROM dbo.fact_bean_morphology f "
                     "INNER JOIN dbo.dim_variedad v ON f.id_variedad=v.id_variedad "
                     "INNER JOIN dbo.dim_tamano t ON f.id_tamano=t.id_tamano "
                     "INNER JOIN dbo.dim_forma fo ON f.id_forma=fo.id_forma "
                     "INNER JOIN dbo.dim_tiempo ti ON f.id_tiempo=ti.id_tiempo")
        m = (f'let\n    Source = Sql.Database("(localdb)\\MSSQLLocalDB", "DryBean_DataMart", '
             f'[Query="{sql_query}"]),\n'
             f'    Typed = Table.TransformColumnTypes(Source, {{\n            {typed}\n        }}, "en-US")\n'
             'in\n    Typed\n')
        q = OUT / "Model" / "queries" / f"{table}.m"; q.parent.mkdir(parents=True, exist_ok=True); q.write_text(m, encoding="utf-8")


def entity(alias): return {"SourceRef": {"Source": alias}}
def measure(alias, table, prop): return {"Measure": {"Expression": entity(alias), "Property": prop}, "Name": f"{table}.{prop}", "NativeReferenceName": prop}
def column(alias, table, prop): return {"Column": {"Expression": entity(alias), "Property": prop}, "Name": f"{table}.{prop}", "NativeReferenceName": prop}


def visual(name, vtype, pos, froms, selects, projections, order_by=None):
    query = {"Version": 2, "From": [{"Name": a, "Entity": t, "Type": 0} for a, t in froms], "Select": selects}
    if order_by: query["OrderBy"] = order_by
    return {"name": name, "layouts": [{"id": 0, "position": pos}], "singleVisual": {
        "visualType": vtype, "projections": projections, "prototypeQuery": query, "drillFilterOtherVisuals": True}}


def page_one_visuals():
    fact = "DryBean_Analitica"
    specs = []
    cards = [("Total Granos", 30), ("Variedades Analizadas", 285), ("Area Promedio", 540), ("Redondez Promedio", 795), ("Compacidad Promedio", 1050)]
    for i, (m, x) in enumerate(cards):
        s = measure("f", fact, m)
        specs.append((f"{i:05d}_card", visual(f"card{i:016d}", "card", {"x": x, "y": 25, "z": i, "width": 225, "height": 90}, [("f", fact)], [s], {"Values": [{"queryRef": f"{fact}.{m}"}]})))
    total = measure("f", fact, "Total Granos")
    variedad = column("f", fact, "variedad")
    specs.append(("00005_bar_variedad", visual("bar00000000000000001", "clusteredBarChart", {"x": 30, "y": 140, "z": 5, "width": 590, "height": 245}, [("f", fact)], [variedad, total], {"Category": [{"queryRef": f"{fact}.variedad"}], "Y": [{"queryRef": f"{fact}.Total Granos"}]}, [{"Direction": 2, "Expression": {"Measure": {"Expression": entity("f"), "Property": "Total Granos"}}}])))
    area = measure("f", fact, "Area Promedio")
    specs.append(("00006_col_area", visual("col00000000000000002", "clusteredColumnChart", {"x": 640, "y": 140, "z": 6, "width": 610, "height": 245}, [("f", fact)], [variedad, area], {"Category": [{"queryRef": f"{fact}.variedad"}], "Y": [{"queryRef": f"{fact}.Area Promedio"}]})))
    for i, (field, x) in enumerate([("variedad", 30), ("categoria_tamano", 240), ("categoria_forma", 450)]):
        c = column("f", fact, field)
        specs.append((f"{7+i:05d}_slicer", visual(f"slicer{i:014d}", "slicer", {"x": x, "y": 410, "z": 7+i, "width": 190, "height": 260}, [("f", fact)], [c], {"Values": [{"queryRef": f"{fact}.{field}"}]})))
    cols = [variedad, column("f", fact, "categoria_tamano"), column("f", fact, "categoria_forma"), total, area, measure("f", fact, "Redondez Promedio")]
    specs.append(("00010_table", visual("table0000000000000001", "tableEx", {"x": 660, "y": 410, "z": 10, "width": 590, "height": 260}, [("f", fact)], cols, {"Values": [{"queryRef": c["Name"]} for c in cols]})))
    return specs


def page_two_visuals():
    fact = "DryBean_Analitica"; specs = []
    for i, (m, x) in enumerate([("Perimetro Promedio", 30), ("Solidez Promedio", 285), ("Area Minima", 540), ("Area Maxima", 795)]):
        s = measure("f", fact, m)
        specs.append((f"{i:05d}_card", visual(f"p2card{i:014d}", "card", {"x": x, "y": 25, "z": i, "width": 225, "height": 90}, [("f", fact)], [s], {"Values": [{"queryRef": f"{fact}.{m}"}]})))
    total = measure("f", fact, "Total Granos")
    tamano = column("f", fact, "categoria_tamano")
    specs.append(("00004_pie", visual("pie00000000000000001", "donutChart", {"x": 30, "y": 145, "z": 4, "width": 390, "height": 245}, [("f", fact)], [tamano, total], {"Category": [{"queryRef": f"{fact}.categoria_tamano"}], "Y": [{"queryRef": f"{fact}.Total Granos"}]})))
    forma = column("f", fact, "categoria_forma")
    specs.append(("00005_bar", visual("p2bar000000000000001", "clusteredBarChart", {"x": 440, "y": 145, "z": 5, "width": 400, "height": 245}, [("f", fact)], [forma, total], {"Category": [{"queryRef": f"{fact}.categoria_forma"}], "Y": [{"queryRef": f"{fact}.Total Granos"}]})))
    variedad = column("f", fact, "variedad")
    comp = measure("f", fact, "Compacidad Promedio")
    red = measure("f", fact, "Redondez Promedio")
    specs.append(("00006_col", visual("p2col000000000000001", "clusteredColumnChart", {"x": 860, "y": 145, "z": 6, "width": 390, "height": 245}, [("f", fact)], [variedad, comp, red], {"Category": [{"queryRef": f"{fact}.variedad"}], "Y": [{"queryRef": f"{fact}.Compacidad Promedio"}, {"queryRef": f"{fact}.Redondez Promedio"}]})))
    cols = [variedad, total, measure("f", fact, "Area Promedio"), measure("f", fact, "Perimetro Promedio"), red, comp, measure("f", fact, "Solidez Promedio")]
    specs.append(("00007_table", visual("p2table00000000000001", "tableEx", {"x": 30, "y": 420, "z": 7, "width": 1220, "height": 250}, [("f", fact)], cols, {"Values": [{"queryRef": c["Name"]} for c in cols]})))
    return specs


def write_report() -> None:
    theme_name = THEME.stem
    jwrite(OUT / "Report" / "report.json", {"id": 0, "layoutOptimization": 0, "resourcePackages": [{"resourcePackage": {"disabled": False, "name": "SharedResources", "type": 2, "items": [{"name": theme_name, "path": f"BaseThemes/{THEME.name}", "type": 202}]}}]})
    jwrite(OUT / "Report" / "config.json", {"version": "5.9", "themeCollection": {"baseTheme": {"name": theme_name, "version": "5.10", "type": 2}}, "activeSectionIndex": 0, "defaultDrillFilterOtherVisuals": True, "settings": {"useNewFilterPaneExperience": True}})
    dst = OUT / "StaticResources" / "SharedResources" / "BaseThemes" / THEME.name; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(THEME, dst)
    pages = [("Resumen ejecutivo", page_one_visuals()), ("Detalle morfológico", page_two_visuals())]
    for ordinal, (name, visuals) in enumerate(pages):
        sec = OUT / "Report" / "sections" / f"{ordinal:03d}_{name.replace(' ', '_')}"
        jwrite(sec / "section.json", {"displayName": name, "displayOption": 1, "height": 720, "name": f"ReportSection{ordinal}", "ordinal": ordinal, "width": 1280})
        jwrite(sec / "config.json", {}); jwrite(sec / "filters.json", [])
        for folder, cfg in visuals:
            vd = sec / "visualContainers" / folder; pos = cfg["layouts"][0]["position"]
            jwrite(vd / "visualContainer.json", {k: pos[k] for k in ("height", "width", "x", "y", "z")})
            jwrite(vd / "config.json", cfg); jwrite(vd / "filters.json", [])


def main() -> None:
    if not THEME.exists(): raise FileNotFoundError(f"Tema base no encontrado: {THEME}")
    if OUT.exists():
        for p in sorted(OUT.rglob("*"), reverse=True):
            if p.is_file(): p.unlink()
    write_root(); write_model(); write_report()
    print(f"Proyecto PbixProj generado: {OUT}")
    print(f"Archivos: {sum(1 for p in OUT.rglob('*') if p.is_file())}")


if __name__ == "__main__": main()
