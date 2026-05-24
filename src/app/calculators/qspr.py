"""
QSPR Analysis Module
====================
Ported and adapted from legacy/qspr_pipeline.py.

Workflow:
  1. Export drug data from SQLite to a DataFrame (properties + topological indices)
  2. Run pairwise linear regression: each index vs each property
  3. Enrich results with RMSE, MAE, R², adjusted R², F-statistic
  4. Build article-style tables, equations and Markdown report
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
from scipy.stats import linregress

from app.calculators.topological import INDEX_NAMES, INDEX_TITLES, INDEX_SYMBOLS

PROPERTY_COLUMNS = ["BP", "VP", "EV", "FP", "MR", "ST", "MV", "MW", "Complexity"]

# Map DB column names → uppercase labels used in the article
DB_PROP_MAP = {
    "bp": "BP", "vp": "VP", "ev": "EV",
    "fp": "FP", "mr": "MR", "st": "ST", "mv": "MV",
    "mw": "MW", "complexity": "Complexity"
}
DB_INDEX_MAP = {
    "ti_abc": "ABC", "ti_ga": "GA",
    "ti_ri": "RI", "ti_rr": "RR", "ti_h": "H", "ti_sci": "SCI",
    "ti_m1": "M1", "ti_m2": "M2", "ti_hm": "HM", "ti_rm2": "RM2",
    "ti_f": "F",  "ti_hf": "HF",
}

TABLE_NUMBER_BY_INDEX = {
    "ABC": 5, "RA": 6, "S": 7, "GA": 8, "M1": 9, "M2": 10, "HM": 11, "H": 12, "F": 13,
    "RI": 3, "RR": 4, "SCI": 6, "RM2": 10, "HF": 12,
}


# ---------------------------------------------------------------------------
# Data export from DB
# ---------------------------------------------------------------------------

def export_db_to_dataframe(session) -> pd.DataFrame:
    """Pull all drugs from the master SQLite table into a tidy DataFrame."""
    from app.models.drug import Drug
    drugs = session.query(Drug).all()
    return _build_df_from_records(drugs)

def export_analysis_to_dataframe(session, analysis_id: int) -> pd.DataFrame:
    """Pull drugs for a specific analysis, using snapshots/overwrites."""
    from app.models.analysis import AnalysisItem
    from app.models.drug import Drug
    items = session.query(AnalysisItem).filter_by(analysis_id=analysis_id).all()
    
    rows = []
    for item in items:
        # Get drug for indices (indices are not overwritten in AnalysisItem)
        drug = session.query(Drug).get(item.drug_id)
        row = {"Drug": drug.name, "SMILES": drug.smiles}
        
        # Pull properties from the AnalysisItem (snapshot)
        for db_col, label in DB_PROP_MAP.items():
            row[label] = getattr(item, db_col, None)
            
        # Pull indices from the master Drug record
        for db_col, label in DB_INDEX_MAP.items():
            row[label] = getattr(drug, db_col, None)
        rows.append(row)
        
    df = pd.DataFrame(rows)
    return _cleanup_numeric_cols(df)

def _build_df_from_records(drugs) -> pd.DataFrame:
    rows = []
    for drug in drugs:
        row = {"Drug": drug.name, "SMILES": drug.smiles}
        for db_col, label in DB_PROP_MAP.items():
            row[label] = getattr(drug, db_col, None)
        for db_col, label in DB_INDEX_MAP.items():
            row[label] = getattr(drug, db_col, None)
        rows.append(row)
    df = pd.DataFrame(rows)
    return _cleanup_numeric_cols(df)

def _cleanup_numeric_cols(df: pd.DataFrame) -> pd.DataFrame:
    for col in PROPERTY_COLUMNS + INDEX_NAMES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# ---------------------------------------------------------------------------
# Linear regression
# ---------------------------------------------------------------------------

def run_qspr(df: pd.DataFrame, min_points: int = 3) -> pd.DataFrame:
    """Run pairwise linear regression: each topological index vs each property."""
    results = []
    prop_cols = [c for c in PROPERTY_COLUMNS if c in df.columns]
    idx_cols  = [c for c in INDEX_NAMES     if c in df.columns]

    for prop in prop_cols:
        y_all = pd.to_numeric(df[prop], errors="coerce")
        for idx in idx_cols:
            x_all = pd.to_numeric(df[idx], errors="coerce")
            valid = pd.DataFrame({"x": x_all, "y": y_all}).dropna()
            n = len(valid)
            if n < max(min_points, 2):
                continue
            slope, intercept, r, p, se = linregress(valid["x"], valid["y"])
            results.append({
                "property": prop, "index": idx, "n": n,
                "r": r, "R2": r ** 2, "p_value": p,
                "slope": slope, "intercept": intercept, "std_err": se,
            })
    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Enrichment (RMSE, MAE, MAPE, adjusted R²)
# ---------------------------------------------------------------------------

def enrich_results(
    qspr_df: pd.DataFrame,
    data_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    enriched_rows, pred_rows = [], []
    has_drug = "Drug" in data_df.columns

    for _, row in qspr_df.iterrows():
        prop, idx = str(row["property"]), str(row["index"])
        if prop not in data_df.columns or idx not in data_df.columns:
            continue

        slope, intercept = float(row["slope"]), float(row["intercept"])
        x = pd.to_numeric(data_df[idx], errors="coerce")
        y = pd.to_numeric(data_df[prop], errors="coerce")
        valid = pd.DataFrame({"x": x, "y": y}).dropna()
        if valid.empty:
            continue

        y_pred   = slope * valid["x"] + intercept
        residuals = valid["y"] - y_pred
        r2   = float(row["R2"])
        n    = len(valid)
        rmse = float(np.sqrt(np.mean(np.square(residuals))))
        mae  = float(np.mean(np.abs(residuals)))
        non_zero = valid["y"] != 0
        mape = float(np.mean(np.abs(
            (valid.loc[non_zero, "y"] - y_pred.loc[non_zero]) /
            valid.loc[non_zero, "y"]
        )) * 100.0) if non_zero.any() else np.nan
        adj_r2 = (1.0 - (1.0 - r2) * (n - 1) / (n - 2)) if n > 2 else np.nan
        p_val  = float(row["p_value"]) if np.isfinite(row["p_value"]) else np.nan

        quality = (
            "excellent" if r2 >= 0.90 and p_val < 0.05 else
            "good"      if r2 >= 0.75 and p_val < 0.05 else
            "moderate"  if r2 >= 0.50 else "weak"
        )

        model_id = f"{prop}__{idx}"
        enriched_rows.append({
            "model_id": model_id, "property": prop, "index": idx,
            "equation": f"{prop} = ({slope:.6g})*{idx} + ({intercept:.6g})",
            "n": n, "r": row["r"], "R2": r2, "adjusted_R2": adj_r2,
            "p_value": p_val, "slope": slope, "intercept": intercept,
            "std_err": row.get("std_err", np.nan),
            "RMSE": rmse, "MAE": mae, "MAPE_percent": mape,
            "model_quality": quality,
        })

        for local_i, vid in enumerate(valid.index):
            pred_row = {
                "model_id": model_id, "property": prop, "index": idx,
                "row_id": local_i,
                "x_value": float(valid.loc[vid, "x"]),
                "y_observed": float(valid.loc[vid, "y"]),
                "y_predicted": float(y_pred.loc[vid]),
                "residual": float(residuals.loc[vid]),
            }
            if has_drug:
                pred_row["Drug"] = data_df.loc[vid, "Drug"]
            pred_rows.append(pred_row)

    return pd.DataFrame(enriched_rows), pd.DataFrame(pred_rows)


# ---------------------------------------------------------------------------
# Article-style output builders
# ---------------------------------------------------------------------------

def _safe(v, digits=6) -> str:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return "NA"
    return "NA" if (np.isnan(f) or np.isinf(f)) else f"{f:.{digits}g}"


def _f_stat(r2, n):
    if n <= 2 or not np.isfinite(r2) or r2 >= 1.0:
        return np.nan
    return float((r2 / (1.0 - r2)) * (n - 2))


def build_equations_catalog(enriched: pd.DataFrame, decimals: int = 4) -> pd.DataFrame:
    rows = []
    for idx in INDEX_NAMES:
        for prop in PROPERTY_COLUMNS:
            m = enriched[(enriched["index"] == idx) & (enriched["property"] == prop)]
            if m.empty:
                continue
            r = m.iloc[0]
            sign = "+" if r["slope"] >= 0 else "-"
            eq = f"{prop}={r['intercept']:.{decimals}f} {sign} {abs(r['slope']):.{decimals}f}[{INDEX_SYMBOLS.get(idx,idx)}]"
            rows.append({
                "index_code": idx, "index_title": INDEX_TITLES.get(idx, idx),
                "index_symbol": INDEX_SYMBOLS.get(idx, idx),
                "property": prop, "equation": eq,
                "slope": r["slope"], "intercept": r["intercept"],
                "n": r["n"], "R2": r["R2"], "p_value": r["p_value"],
            })
    return pd.DataFrame(rows)


def build_article_tables(enriched: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for idx in INDEX_NAMES:
        for prop in PROPERTY_COLUMNS:
            m = enriched[(enriched["index"] == idx) & (enriched["property"] == prop)]
            if m.empty:
                continue
            r = m.iloc[0]
            n, r2, p = int(r["n"]), float(r["R2"]), float(r["p_value"])
            ind = "Significant" if np.isfinite(p) and p < 0.05 else "Not Significant"
            rows.append({
                "Table": TABLE_NUMBER_BY_INDEX.get(idx, np.nan),
                "Index": INDEX_TITLES.get(idx, idx),
                "Properties": prop, "N": n,
                "a": r["intercept"], "b": r["slope"],
                "r": r["r"], "r2": r2,
                "F": _f_stat(r2, n), "p": p,
                "Indicator": ind, "index_code": idx,
            })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["Table", "Properties"]).reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Full report builder
# ---------------------------------------------------------------------------

def build_report(
    session,
    output_dir: str = "data/qspr_results",
    min_points: int = 3,
    top_k: int = 3,
    analysis_id: int | None = None,
) -> dict[str, Path]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if analysis_id:
        df = export_analysis_to_dataframe(session, analysis_id)
    else:
        df = export_db_to_dataframe(session)
        
    df.to_csv(out_dir / "qspr_data.csv", index=False)

    raw = run_qspr(df, min_points=min_points)
    enriched, predictions = enrich_results(raw, df)
    enriched = enriched.sort_values(["property", "R2"], ascending=[True, False])

    equations  = build_equations_catalog(enriched)
    art_tables = build_article_tables(enriched)

    best   = enriched.groupby("property", group_keys=False).head(1)
    top    = enriched.groupby("property", group_keys=False).head(top_k)
    r2_mat = enriched.pivot(index="property", columns="index", values="R2")
    p_mat  = enriched.pivot(index="property", columns="index", values="p_value")

    # Save CSVs
    paths: dict[str, Path] = {}
    for name, frame in [
        ("all_models",       enriched),
        ("best_models",      best),
        ("top_models",       top),
        ("predictions",      predictions),
        ("equations",        equations),
        ("article_tables",   art_tables),
        ("r2_matrix",        r2_mat),
        ("pvalue_matrix",    p_mat),
        ("qspr_data",        df),
    ]:
        p = out_dir / f"{name}.csv"
        frame.to_csv(p, index=(name in ("r2_matrix", "pvalue_matrix")))
        paths[name] = p

    # Markdown report
    lines = ["# QSPR Report — Heart Attack Drugs", ""]
    lines += ["## Best model per property", "",
              "| Property | Index | Equation | n | r | R² | Adj.R² | p | RMSE | Quality |",
              "|---|---|---|---:|---:|---:|---:|---:|---:|---|"]
    for _, r in best.iterrows():
        lines.append(
            f"| {r['property']} | {r['index']} | `{r['equation']}` | {int(r['n'])} "
            f"| {_safe(r['r'],4)} | {_safe(r['R2'],4)} | {_safe(r['adjusted_R2'],4)} "
            f"| {_safe(r['p_value'],3)} | {_safe(r['RMSE'],4)} | {r['model_quality']} |"
        )
    lines += ["", "## Statistical Tables (Article Format)", ""]
    for idx in INDEX_NAMES:
        sub = art_tables[art_tables["index_code"] == idx]
        if sub.empty:
            continue
        tnum = int(sub["Table"].iloc[0])
        lines += [f"### Table {tnum} — {INDEX_TITLES.get(idx, idx)}", "",
                  "| Properties | N | a | b | r | r² | F | p | Indicator |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
        for _, r in sub.iterrows():
            lines.append(
                f"| {r['Properties']} | {int(r['N'])} | {_safe(r['a'],6)} "
                f"| {_safe(r['b'],6)} | {_safe(r['r'],6)} | {_safe(r['r2'],6)} "
                f"| {_safe(r['F'],6)} | {_safe(r['p'],6)} | {r['Indicator']} |"
            )
        lines.append("")

    lines += ["## Regression Equations by Index", ""]
    for idx in INDEX_NAMES:
        sub = equations[equations["index_code"] == idx]
        if sub.empty:
            continue
        lines.append(f"### {INDEX_TITLES.get(idx, idx)}")
        for _, r in sub.iterrows():
            lines.append(f"- {r['equation']}")
        lines.append("")

    report_path = out_dir / "qspr_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    paths["report"] = report_path

    return paths
