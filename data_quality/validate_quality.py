"""
=============================================================================
  Data Quality Validation Script
  Proyecto Final - AWS Academy Data Engineering (Ruta A)
  Rol 2: Data Quality Engineer
=============================================================================
  Este script ejecuta 10 reglas de validación sobre los 4 datasets de
  Sea Around Us y genera un reporte HTML con los resultados.
  
  Uso:
    python validate_quality.py
  
  Requisitos:
    pip install pandas jinja2
=============================================================================
"""

import pandas as pd
import os
from datetime import datetime

# -------------------------------------------------------------------------
# CONFIGURACION
# -------------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data_full")
OUTPUT_DIR = os.path.dirname(__file__)

FILES = {
    "global":         os.path.join(DATA_DIR, "global.csv"),
    "eez":            os.path.join(DATA_DIR, "eez.csv"),
    "high_seas":      os.path.join(DATA_DIR, "high_seas.csv"),
    "fishing_entity": os.path.join(DATA_DIR, "fishing_entity.csv"),
}

# -------------------------------------------------------------------------
# CARGA DE DATOS
# -------------------------------------------------------------------------
def load_datasets():
    """Carga los 4 CSV en un diccionario de DataFrames."""
    datasets = {}
    for name, path in FILES.items():
        print(f"  Cargando {name}...")
        datasets[name] = pd.read_csv(path, low_memory=False)
        print(f"    -> {len(datasets[name]):,} filas, {len(datasets[name].columns)} columnas")
    return datasets

# -------------------------------------------------------------------------
# REGLAS DE CALIDAD
# -------------------------------------------------------------------------
def run_all_rules(datasets):
    """
    Ejecuta las 10 reglas de calidad y devuelve una lista de resultados.
    Cada resultado es un diccionario con:
      id, name, severity, dataset, total_rows, passed, failed, status, details
    """
    results = []

    for ds_name, df in datasets.items():

        total = len(df)

        # ==================================================================
        # DQ-01: Completitud de campos criticos (year, tonnes, fishing_entity)
        # ==================================================================
        critical_cols = [c for c in ["year", "tonnes", "fishing_entity"] if c in df.columns]
        nulls = df[critical_cols].isnull().any(axis=1).sum()
        results.append({
            "id": "DQ-01", "name": "Completitud de campos criticos",
            "severity": "Alta", "dataset": ds_name,
            "total_rows": total, "passed": total - nulls, "failed": int(nulls),
            "status": "PASS" if nulls == 0 else "FAIL",
            "details": f"Campos evaluados: {critical_cols}. Filas con al menos un nulo: {nulls:,}"
        })

        # ==================================================================
        # DQ-02: Validez temporal (year entre 1950 y 2018)
        # ==================================================================
        if "year" in df.columns:
            df_year = pd.to_numeric(df["year"], errors="coerce")
            out_of_range = ((df_year < 1950) | (df_year > 2018)).sum()
            results.append({
                "id": "DQ-02", "name": "Validez temporal (1950-2018)",
                "severity": "Alta", "dataset": ds_name,
                "total_rows": total, "passed": total - int(out_of_range), "failed": int(out_of_range),
                "status": "PASS" if out_of_range == 0 else "FAIL",
                "details": f"Filas con year fuera de [1950, 2018]: {out_of_range:,}"
            })

        # ==================================================================
        # DQ-03: No negatividad de tonelaje (tonnes >= 0)
        # ==================================================================
        if "tonnes" in df.columns:
            tonnes_num = pd.to_numeric(df["tonnes"], errors="coerce")
            negatives = (tonnes_num < 0).sum()
            results.append({
                "id": "DQ-03", "name": "No negatividad de tonelaje",
                "severity": "Alta", "dataset": ds_name,
                "total_rows": total, "passed": total - int(negatives), "failed": int(negatives),
                "status": "PASS" if negatives == 0 else "FAIL",
                "details": f"Registros con tonnes < 0: {negatives:,}"
            })

        # ==================================================================
        # DQ-04: No negatividad de valor economico (landed_value >= 0)
        # ==================================================================
        if "landed_value" in df.columns:
            lv = pd.to_numeric(df["landed_value"], errors="coerce")
            non_null_lv = lv.dropna()
            neg_lv = (non_null_lv < 0).sum()
            results.append({
                "id": "DQ-04", "name": "No negatividad de valor economico",
                "severity": "Media", "dataset": ds_name,
                "total_rows": len(non_null_lv), "passed": len(non_null_lv) - int(neg_lv), "failed": int(neg_lv),
                "status": "PASS" if neg_lv == 0 else "FAIL",
                "details": f"Registros con landed_value < 0 (excluyendo nulos): {neg_lv:,}"
            })

        # ==================================================================
        # DQ-05: Valores validos de sector pesquero
        # ==================================================================
        if "fishing_sector" in df.columns:
            valid_sectors = {"Industrial", "Artisanal", "Subsistence", "Recreational"}
            invalid = ~df["fishing_sector"].isin(valid_sectors) & df["fishing_sector"].notna()
            inv_count = invalid.sum()
            results.append({
                "id": "DQ-05", "name": "Valores validos de sector pesquero",
                "severity": "Media", "dataset": ds_name,
                "total_rows": total, "passed": total - int(inv_count), "failed": int(inv_count),
                "status": "PASS" if inv_count == 0 else "FAIL",
                "details": f"Valores invalidos: {df.loc[invalid, 'fishing_sector'].unique().tolist()[:5] if inv_count > 0 else 'Ninguno'}"
            })

        # ==================================================================
        # DQ-06: Valores validos de tipo de captura
        # ==================================================================
        if "catch_type" in df.columns:
            valid_catch = {"Landings", "Discards"}
            invalid_ct = ~df["catch_type"].isin(valid_catch) & df["catch_type"].notna()
            inv_ct_count = invalid_ct.sum()
            results.append({
                "id": "DQ-06", "name": "Valores validos de tipo de captura",
                "severity": "Media", "dataset": ds_name,
                "total_rows": total, "passed": total - int(inv_ct_count), "failed": int(inv_ct_count),
                "status": "PASS" if inv_ct_count == 0 else "FAIL",
                "details": f"Valores invalidos: {df.loc[invalid_ct, 'catch_type'].unique().tolist()[:5] if inv_ct_count > 0 else 'Ninguno'}"
            })

        # ==================================================================
        # DQ-07: Valores validos de estado de reporte
        # ==================================================================
        if "reporting_status" in df.columns:
            valid_rs = {"Reported", "Unreported"}
            invalid_rs = ~df["reporting_status"].isin(valid_rs) & df["reporting_status"].notna()
            inv_rs_count = invalid_rs.sum()
            results.append({
                "id": "DQ-07", "name": "Valores validos de estado de reporte",
                "severity": "Media", "dataset": ds_name,
                "total_rows": total, "passed": total - int(inv_rs_count), "failed": int(inv_rs_count),
                "status": "PASS" if inv_rs_count == 0 else "FAIL",
                "details": f"Valores invalidos: {df.loc[invalid_rs, 'reporting_status'].unique().tolist()[:5] if inv_rs_count > 0 else 'Ninguno'}"
            })

        # ==================================================================
        # DQ-08: Consistencia captura-descarte vs uso final
        # ==================================================================
        if "catch_type" in df.columns and "end_use_type" in df.columns:
            discards_dhc = (
                (df["catch_type"] == "Discards") &
                (df["end_use_type"] == "Direct human consumption")
            ).sum()
            results.append({
                "id": "DQ-08", "name": "Consistencia captura vs uso final",
                "severity": "Baja", "dataset": ds_name,
                "total_rows": total, "passed": total - int(discards_dhc), "failed": int(discards_dhc),
                "status": "PASS" if discards_dhc == 0 else "WARN",
                "details": f"Registros con Discards + Direct human consumption (contradiccion): {discards_dhc:,}"
            })

        # ==================================================================
        # DQ-09: Unicidad de registros (duplicados completos)
        # ==================================================================
        dupes = df.duplicated().sum()
        results.append({
            "id": "DQ-09", "name": "Unicidad de registros",
            "severity": "Media", "dataset": ds_name,
            "total_rows": total, "passed": total - int(dupes), "failed": int(dupes),
            "status": "PASS" if dupes == 0 else "FAIL",
            "details": f"Filas completamente duplicadas: {dupes:,}"
        })

    # ======================================================================
    # DQ-10: Integridad referencial (fishing_entity entre fuentes)
    # ======================================================================
    if "global" in datasets and "fishing_entity" in datasets["global"].columns:
        global_entities = set(datasets["global"]["fishing_entity"].dropna().unique())

        for ds_name in ["eez", "high_seas", "fishing_entity"]:
            if ds_name in datasets:
                col = "fishing_entity" if "fishing_entity" in datasets[ds_name].columns else None
                if col:
                    other_entities = set(datasets[ds_name][col].dropna().unique())
                    matched = other_entities & global_entities
                    pct = (len(matched) / len(other_entities) * 100) if other_entities else 100
                    results.append({
                        "id": "DQ-10", "name": f"Integridad referencial ({ds_name} vs global)",
                        "severity": "Alta", "dataset": ds_name,
                        "total_rows": len(other_entities),
                        "passed": len(matched),
                        "failed": len(other_entities) - len(matched),
                        "status": "PASS" if pct >= 80 else "FAIL",
                        "details": f"{len(matched)}/{len(other_entities)} entidades encontradas en global ({pct:.1f}%)"
                    })

    return results


# -------------------------------------------------------------------------
# GENERACION DE REPORTE HTML
# -------------------------------------------------------------------------
def generate_html_report(results):
    """Genera un archivo HTML profesional con los resultados de calidad."""

    total_rules = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    warned = sum(1 for r in results if r["status"] == "WARN")
    score = (passed / total_rules * 100) if total_rules > 0 else 0

    rows_html = ""
    for r in results:
        color = "#27ae60" if r["status"] == "PASS" else ("#e74c3c" if r["status"] == "FAIL" else "#f39c12")
        sev_color = "#e74c3c" if r["severity"] == "Alta" else ("#f39c12" if r["severity"] == "Media" else "#3498db")
        rows_html += f"""
        <tr>
            <td><strong>{r['id']}</strong></td>
            <td>{r['name']}</td>
            <td><span style="background:{sev_color};color:white;padding:2px 8px;border-radius:4px;font-size:12px">{r['severity']}</span></td>
            <td>{r['dataset']}</td>
            <td style="text-align:right">{r['total_rows']:,}</td>
            <td style="text-align:right;color:#27ae60"><strong>{r['passed']:,}</strong></td>
            <td style="text-align:right;color:#e74c3c"><strong>{r['failed']:,}</strong></td>
            <td><span style="background:{color};color:white;padding:4px 12px;border-radius:4px;font-weight:bold">{r['status']}</span></td>
            <td style="font-size:13px;color:#555">{r['details']}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte de Calidad de Datos - Sea Around Us</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f6fa; color: #2c3e50; padding: 30px; }}
        .header {{ background: linear-gradient(135deg, #2c3e50, #3498db); color: white; padding: 30px 40px; border-radius: 12px; margin-bottom: 25px; }}
        .header h1 {{ font-size: 28px; margin-bottom: 5px; }}
        .header p {{ opacity: 0.85; font-size: 14px; }}
        .summary {{ display: flex; gap: 15px; margin-bottom: 25px; }}
        .card {{ flex: 1; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; }}
        .card .number {{ font-size: 36px; font-weight: bold; }}
        .card .label {{ font-size: 13px; color: #7f8c8d; margin-top: 5px; }}
        .green {{ color: #27ae60; }}
        .red {{ color: #e74c3c; }}
        .orange {{ color: #f39c12; }}
        .blue {{ color: #3498db; }}
        table {{ width: 100%; background: white; border-collapse: collapse; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        th {{ background: #2c3e50; color: white; padding: 12px 15px; text-align: left; font-size: 13px; text-transform: uppercase; }}
        td {{ padding: 10px 15px; border-bottom: 1px solid #ecf0f1; font-size: 14px; }}
        tr:hover {{ background: #f8f9fa; }}
        .footer {{ text-align: center; margin-top: 25px; color: #95a5a6; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Reporte de Calidad de Datos</h1>
        <p>Proyecto Final AWS Data Engineering - Sea Around Us Fisheries Dataset</p>
        <p>Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="summary">
        <div class="card"><div class="number blue">{total_rules}</div><div class="label">Total de Validaciones</div></div>
        <div class="card"><div class="number green">{passed}</div><div class="label">Pasaron (PASS)</div></div>
        <div class="card"><div class="number red">{failed}</div><div class="label">Fallaron (FAIL)</div></div>
        <div class="card"><div class="number orange">{warned}</div><div class="label">Advertencias (WARN)</div></div>
        <div class="card"><div class="number" style="color:{'#27ae60' if score >= 80 else '#e74c3c'}">{score:.0f}%</div><div class="label">Score Global</div></div>
    </div>

    <table>
        <thead>
            <tr>
                <th>ID</th><th>Regla</th><th>Severidad</th><th>Dataset</th>
                <th>Total Filas</th><th>Pasaron</th><th>Fallaron</th><th>Estado</th><th>Detalles</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>

    <div class="footer">
        <p>Data Quality Report | AWS Academy Data Engineering Capstone | Rol 2: Data Quality Engineer</p>
    </div>
</body>
</html>"""

    output_path = os.path.join(OUTPUT_DIR, "report.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n  Reporte generado en: {output_path}")
    return output_path


# -------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("  DATA QUALITY VALIDATION - Sea Around Us")
    print("=" * 60)

    print("\n[1/3] Cargando datasets...")
    datasets = load_datasets()

    print("\n[2/3] Ejecutando 10 reglas de calidad...")
    results = run_all_rules(datasets)

    print("\n[3/3] Generando reporte HTML...")
    generate_html_report(results)

    # Resumen en consola
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    warned = sum(1 for r in results if r["status"] == "WARN")
    print(f"\n  RESULTADO: {passed} PASS | {failed} FAIL | {warned} WARN")
    print("=" * 60)
