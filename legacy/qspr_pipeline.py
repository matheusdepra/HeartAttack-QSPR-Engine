from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from rdkit import Chem
from scipy.stats import linregress

DEFAULT_INDEX_COLUMNS = ["RI", "RR", "H", "SCI", "M1", "M2", "HM", "RM2", "F", "HF"]
DEFAULT_PROPERTY_COLUMNS = ["BP", "VP", "EV", "FP", "MR", "ST", "MV"]
INDEX_TITLES = {
    "RI": "Randic Index R(G)",
    "RR": "Reciprocal Randic Index RR(G)",
    "H": "Harmonic Index H(G)",
    "SCI": "Sum Connectivity Index SC(G)",
    "M1": "First Zagreb Index M1(G)",
    "M2": "Second Zagreb Index M2(G)",
    "HM": "Hyper Zagreb Index HM(G)",
    "RM2": "Redefined Second Zagreb Index RM2(G)",
    "F": "Forgotten Index F(G)",
    "HF": "Hyper Forgotten Index HF(G)",
}
INDEX_SYMBOLS = {
    "RI": "R(G)",
    "RR": "RR(G)",
    "H": "H(G)",
    "SCI": "SC(G)",
    "M1": "M1(G)",
    "M2": "M2(G)",
    "HM": "HM(G)",
    "RM2": "RM2(G)",
    "F": "F(G)",
    "HF": "HF(G)",
}
TABLE_NUMBER_BY_INDEX = {
    "RI": 3,
    "RR": 4,
    "H": 5,
    "SCI": 6,
    "M1": 7,
    "M2": 8,
    "HM": 9,
    "RM2": 10,
    "F": 11,
    "HF": 12,
}


def _normalize_columns(columns: Iterable[str] | None) -> list[str]:
    if columns is None:
        return []
    return [col.strip() for col in columns if str(col).strip()]


def _existing_columns(df: pd.DataFrame, columns: Sequence[str]) -> list[str]:
    return [col for col in columns if col in df.columns]


def edge_partition_from_mol(mol: Chem.Mol) -> Counter:
    degrees = {atom.GetIdx(): atom.GetDegree() for atom in mol.GetAtoms()}
    part: Counter = Counter()

    for bond in mol.GetBonds():
        a = bond.GetBeginAtomIdx()
        b = bond.GetEndAtomIdx()
        key = tuple(sorted((degrees[a], degrees[b])))
        part[key] += 1

    return part


def calc_indices_from_partition(part: Counter) -> dict[str, float]:
    values = {
        "RI": 0.0,
        "RR": 0.0,
        "H": 0.0,
        "SCI": 0.0,
        "M1": 0.0,
        "M2": 0.0,
        "HM": 0.0,
        "RM2": 0.0,
        "F": 0.0,
        "HF": 0.0,
    }

    for (du, dv), freq in part.items():
        values["RI"] += freq * (1.0 / np.sqrt(du * dv))
        values["RR"] += freq * np.sqrt(du * dv)
        values["H"] += freq * (2.0 / (du + dv))
        values["SCI"] += freq * (1.0 / np.sqrt(du + dv))
        values["M1"] += freq * (du + dv)
        values["M2"] += freq * (du * dv)
        values["HM"] += freq * ((du + dv) ** 2)
        values["RM2"] += freq * ((du - 1) * (dv - 1))
        values["F"] += freq * (du**2 + dv**2)
        values["HF"] += freq * ((du**2 + dv**2) ** 2)

    return values


def smiles_to_indices(smiles: str) -> tuple[Counter, dict[str, float]]:
    smiles_clean = (smiles or "").strip()
    if not smiles_clean:
        raise ValueError("SMILES vazio.")

    mol = Chem.MolFromSmiles(smiles_clean)
    if mol is None:
        raise ValueError(f"SMILES invalido: {smiles_clean}")

    mol = Chem.RemoveHs(mol)
    if mol.GetNumAtoms() == 0:
        raise ValueError(f"Molecula vazia apos remover H: {smiles_clean}")

    part = edge_partition_from_mol(mol)
    return part, calc_indices_from_partition(part)


def calculate_topological_indices(
    input_csv: str | Path,
    output_csv: str | Path = "topological_indices.csv",
    drug_column: str = "Drug",
    smiles_column: str = "SMILES",
    include_edge_partition: bool = True,
) -> pd.DataFrame:
    df = pd.read_csv(input_csv)

    missing = [col for col in [drug_column, smiles_column] if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas ausentes em {input_csv}: {missing}")

    results: list[dict[str, object]] = []
    for _, row in df.iterrows():
        drug = row.get(drug_column, "")
        smiles = row.get(smiles_column, "")
        out_row: dict[str, object] = {drug_column: drug, smiles_column: smiles}

        try:
            part, indices = smiles_to_indices(str(smiles))
            out_row.update(indices)
            if include_edge_partition:
                out_row["edge_partition"] = str(dict(part))
        except Exception as exc:  # noqa: BLE001
            out_row["error"] = str(exc)

        results.append(out_row)

    out_df = pd.DataFrame(results)
    out_df.to_csv(output_csv, index=False)
    return out_df


def merge_property_and_indices(
    properties_csv: str | Path,
    indices_csv: str | Path,
    output_csv: str | Path = "merged_qspr_data.csv",
    drug_column: str = "Drug",
    property_smiles_column: str = "SMILES",
    index_smiles_column: str = "SMILES",
    smiles_output_column: str = "SMILES",
    join: str = "inner",
) -> pd.DataFrame:
    df_prop = pd.read_csv(properties_csv)
    df_idx = pd.read_csv(indices_csv)

    missing_prop = [drug_column] if drug_column not in df_prop.columns else []
    missing_idx = [drug_column] if drug_column not in df_idx.columns else []
    if missing_prop:
        raise ValueError(f"Coluna '{drug_column}' ausente em {properties_csv}")
    if missing_idx:
        raise ValueError(f"Coluna '{drug_column}' ausente em {indices_csv}")

    merged = pd.merge(
        df_prop,
        df_idx,
        on=drug_column,
        how=join,
        suffixes=("_prop", "_idx"),
    )

    prop_col = property_smiles_column
    if property_smiles_column in df_prop.columns and property_smiles_column in df_idx.columns:
        prop_col = f"{property_smiles_column}_prop"

    idx_col = index_smiles_column
    if index_smiles_column in df_prop.columns and index_smiles_column in df_idx.columns:
        idx_col = f"{index_smiles_column}_idx"

    if prop_col in merged.columns and idx_col in merged.columns:
        merged["SMILES_match"] = merged[prop_col] == merged[idx_col]
        merged[smiles_output_column] = merged[prop_col]

        cols_to_drop = [c for c in [prop_col, idx_col] if c != smiles_output_column]
        merged = merged.drop(columns=cols_to_drop, errors="ignore")

    merged.to_csv(output_csv, index=False)
    return merged


def prepare_qspr_dataset(
    input_csv: str | Path,
    output_csv: str | Path = "qspr_clean.csv",
    property_columns: Sequence[str] | None = None,
    index_columns: Sequence[str] | None = None,
    extra_numeric_columns: Sequence[str] | None = None,
) -> pd.DataFrame:
    df = pd.read_csv(input_csv)
    df = df.replace(r"^\s*$", np.nan, regex=True)

    prop_cols = property_columns or DEFAULT_PROPERTY_COLUMNS
    idx_cols = index_columns or DEFAULT_INDEX_COLUMNS
    extra_cols = _normalize_columns(extra_numeric_columns)

    numeric_cols: list[str] = []
    numeric_cols.extend(_existing_columns(df, list(prop_cols)))
    numeric_cols.extend(_existing_columns(df, list(idx_cols)))
    numeric_cols.extend(_existing_columns(df, extra_cols))
    numeric_cols = list(dict.fromkeys(numeric_cols))

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.to_csv(output_csv, index=False)
    return df


def run_qspr(
    df: pd.DataFrame,
    property_columns: Sequence[str] | None = None,
    index_columns: Sequence[str] | None = None,
    output_csv: str | Path = "qspr_results.csv",
    min_points: int = 2,
) -> pd.DataFrame:
    prop_cols = _existing_columns(df, list(property_columns or DEFAULT_PROPERTY_COLUMNS))
    idx_cols = _existing_columns(df, list(index_columns or DEFAULT_INDEX_COLUMNS))

    if not prop_cols:
        raise ValueError("Nenhuma coluna de propriedade encontrada para regressao.")
    if not idx_cols:
        raise ValueError("Nenhuma coluna de indice topologico encontrada para regressao.")

    results: list[dict[str, float | int | str]] = []

    for prop in prop_cols:
        y_all = pd.to_numeric(df[prop], errors="coerce")

        for idx in idx_cols:
            x_all = pd.to_numeric(df[idx], errors="coerce")
            valid = pd.DataFrame({"x": x_all, "y": y_all}).dropna()

            n = len(valid)
            if n < max(min_points, 2):
                continue

            slope, intercept, r_value, p_value, std_err = linregress(valid["x"], valid["y"])
            results.append(
                {
                    "property": prop,
                    "index": idx,
                    "n": n,
                    "r": r_value,
                    "R2": r_value**2,
                    "p_value": p_value,
                    "slope": slope,
                    "intercept": intercept,
                    "std_err": std_err,
                }
            )

    out = pd.DataFrame(results)
    out.to_csv(output_csv, index=False)
    return out


def run_qspr_from_csv(
    input_csv: str | Path,
    output_csv: str | Path = "qspr_results.csv",
    property_columns: Sequence[str] | None = None,
    index_columns: Sequence[str] | None = None,
    min_points: int = 2,
) -> pd.DataFrame:
    df = pd.read_csv(input_csv)
    return run_qspr(
        df=df,
        property_columns=property_columns,
        index_columns=index_columns,
        output_csv=output_csv,
        min_points=min_points,
    )


def _safe_float(value: object, digits: int = 6) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "NA"
    if np.isnan(numeric) or np.isinf(numeric):
        return "NA"
    return f"{numeric:.{digits}g}"


def _build_equation(prop: str, idx: str, slope: float, intercept: float) -> str:
    return f"{prop} = ({_safe_float(slope)})*{idx} + ({_safe_float(intercept)})"


def _build_article_style_equation(
    prop: str,
    idx: str,
    slope: float,
    intercept: float,
    decimals: int = 4,
) -> str:
    symbol = INDEX_SYMBOLS.get(idx, f"{idx}(G)")
    intercept_str = f"{intercept:.{decimals}f}"
    slope_abs_str = f"{abs(slope):.{decimals}f}"
    sign = "+" if slope >= 0 else "-"
    return f"{prop}={intercept_str} {sign} {slope_abs_str}[{symbol}]"


def _classify_model(r2: float, p_value: float) -> str:
    if not np.isfinite(r2):
        return "invalid_nan"
    if r2 >= 0.90 and np.isfinite(p_value) and p_value < 0.05:
        return "excellent"
    if r2 >= 0.75 and np.isfinite(p_value) and p_value < 0.05:
        return "good"
    if r2 >= 0.50:
        return "moderate"
    return "weak"


def enrich_qspr_results(
    qspr_results: pd.DataFrame,
    qspr_data: pd.DataFrame,
    property_col: str = "property",
    index_col: str = "index",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = [property_col, index_col, "slope", "intercept", "R2", "r", "p_value", "n"]
    missing = [col for col in required if col not in qspr_results.columns]
    if missing:
        raise ValueError(f"Colunas ausentes no arquivo de resultados: {missing}")

    enriched_rows: list[dict[str, object]] = []
    prediction_rows: list[dict[str, object]] = []
    has_drug = "Drug" in qspr_data.columns

    for _, row in qspr_results.iterrows():
        prop = str(row[property_col])
        idx = str(row[index_col])
        slope = float(row["slope"])
        intercept = float(row["intercept"])

        if prop not in qspr_data.columns or idx not in qspr_data.columns:
            continue

        x = pd.to_numeric(qspr_data[idx], errors="coerce")
        y = pd.to_numeric(qspr_data[prop], errors="coerce")
        valid = pd.DataFrame({"x": x, "y": y}).dropna()

        if valid.empty:
            continue

        y_pred = slope * valid["x"] + intercept
        residuals = valid["y"] - y_pred

        rmse = float(np.sqrt(np.mean(np.square(residuals))))
        mae = float(np.mean(np.abs(residuals)))

        non_zero = valid["y"] != 0
        if non_zero.any():
            mape = float(np.mean(np.abs((valid.loc[non_zero, "y"] - y_pred.loc[non_zero]) / valid.loc[non_zero, "y"])) * 100.0)
        else:
            mape = np.nan

        r2 = float(row["R2"])
        n = int(len(valid))
        if n > 2 and np.isfinite(r2):
            adjusted_r2 = 1.0 - ((1.0 - r2) * (n - 1) / (n - 2))
        else:
            adjusted_r2 = np.nan

        p_value = float(row["p_value"]) if np.isfinite(row["p_value"]) else np.nan
        model_id = f"{prop}__{idx}"
        equation = _build_equation(prop, idx, slope, intercept)

        enriched_rows.append(
            {
                "model_id": model_id,
                "property": prop,
                "index": idx,
                "equation": equation,
                "n": n,
                "r": row["r"],
                "R2": r2,
                "adjusted_R2": adjusted_r2,
                "p_value": p_value,
                "slope": slope,
                "intercept": intercept,
                "std_err": row.get("std_err", np.nan),
                "RMSE": rmse,
                "MAE": mae,
                "MAPE_percent": mape,
                "model_quality": _classify_model(r2, p_value),
            }
        )

        for local_i, idx_valid in enumerate(valid.index):
            pred_row: dict[str, object] = {
                "model_id": model_id,
                "property": prop,
                "index": idx,
                "row_id": int(local_i),
                "x_value": float(valid.loc[idx_valid, "x"]),
                "y_observed": float(valid.loc[idx_valid, "y"]),
                "y_predicted": float(y_pred.loc[idx_valid]),
                "residual": float(residuals.loc[idx_valid]),
            }
            if has_drug:
                pred_row["Drug"] = qspr_data.loc[idx_valid, "Drug"]
            prediction_rows.append(pred_row)

    enriched_df = pd.DataFrame(enriched_rows)
    pred_df = pd.DataFrame(prediction_rows)
    return enriched_df, pred_df


def build_equations_catalog(
    qspr_results: pd.DataFrame,
    property_order: Sequence[str] | None = None,
    index_order: Sequence[str] | None = None,
    decimals: int = 4,
) -> pd.DataFrame:
    props = list(property_order or DEFAULT_PROPERTY_COLUMNS)
    idxs = list(index_order or DEFAULT_INDEX_COLUMNS)

    rows: list[dict[str, object]] = []
    for idx in idxs:
        idx_subset = qspr_results[qspr_results["index"] == idx]
        for prop in props:
            model = idx_subset[idx_subset["property"] == prop]
            if model.empty:
                continue
            model_row = model.iloc[0]
            slope = float(model_row["slope"])
            intercept = float(model_row["intercept"])
            rows.append(
                {
                    "index_code": idx,
                    "index_title": INDEX_TITLES.get(idx, idx),
                    "index_symbol": INDEX_SYMBOLS.get(idx, idx),
                    "property": prop,
                    "equation": _build_article_style_equation(
                        prop=prop,
                        idx=idx,
                        slope=slope,
                        intercept=intercept,
                        decimals=decimals,
                    ),
                    "slope": slope,
                    "intercept": intercept,
                    "n": model_row.get("n", np.nan),
                    "R2": model_row.get("R2", np.nan),
                    "p_value": model_row.get("p_value", np.nan),
                }
            )

    return pd.DataFrame(rows)


def build_equations_by_index_text(
    equations_catalog: pd.DataFrame,
    index_order: Sequence[str] | None = None,
) -> str:
    if equations_catalog.empty:
        return "No equations available."

    lines: list[str] = []
    idxs = list(index_order or DEFAULT_INDEX_COLUMNS)
    number = 1
    for idx in idxs:
        subset = equations_catalog[equations_catalog["index_code"] == idx]
        if subset.empty:
            continue

        lines.append(f"{number}. {INDEX_TITLES.get(idx, idx)}")
        for _, row in subset.iterrows():
            lines.append(str(row["equation"]))
        lines.append("")
        number += 1

    return "\n".join(lines).strip()


def _calc_f_statistic(r2: float, n: int) -> float:
    if n <= 2 or not np.isfinite(r2) or r2 >= 1.0:
        return np.nan
    if r2 <= 0.0:
        return 0.0
    return float((r2 / (1.0 - r2)) * (n - 2))


def build_article_statistical_tables(
    enriched_models: pd.DataFrame,
    property_order: Sequence[str] | None = None,
    index_order: Sequence[str] | None = None,
    significance_alpha: float = 0.05,
) -> pd.DataFrame:
    props = list(property_order or DEFAULT_PROPERTY_COLUMNS)
    idxs = list(index_order or DEFAULT_INDEX_COLUMNS)

    rows: list[dict[str, object]] = []
    for idx in idxs:
        idx_subset = enriched_models[enriched_models["index"] == idx]
        for prop in props:
            model = idx_subset[idx_subset["property"] == prop]
            if model.empty:
                continue

            m = model.iloc[0]
            n_val = int(m["n"]) if pd.notna(m["n"]) else np.nan
            p_val = float(m["p_value"]) if pd.notna(m["p_value"]) else np.nan
            r2_val = float(m["R2"]) if pd.notna(m["R2"]) else np.nan

            if np.isfinite(p_val):
                indicator = "Significant" if p_val < significance_alpha else "Not Significant"
            else:
                indicator = "Undefined"

            rows.append(
                {
                    "Table": TABLE_NUMBER_BY_INDEX.get(idx, np.nan),
                    "Index": INDEX_TITLES.get(idx, idx),
                    "Properties": prop,
                    "N": n_val,
                    "a": m["intercept"],
                    "b": m["slope"],
                    "r": m["r"],
                    "r2": r2_val,
                    "F": _calc_f_statistic(r2_val, n_val) if pd.notna(n_val) else np.nan,
                    "p": p_val,
                    "Indicator": indicator,
                    "index_code": idx,
                }
            )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["Table", "Properties"]).reset_index(drop=True)
    return out


def build_chapter5_report(
    qspr_results_csv: str | Path,
    qspr_data_csv: str | Path,
    output_dir: str | Path = "chapter5_outputs",
    top_k: int = 3,
    min_r2: float = 0.0,
) -> dict[str, Path]:
    results = pd.read_csv(qspr_results_csv)
    data = pd.read_csv(qspr_data_csv)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    enriched, predictions = enrich_qspr_results(results, data)
    if enriched.empty:
        raise ValueError("Nenhum modelo valido foi construido para o relatorio.")

    enriched = enriched.sort_values(["property", "R2", "p_value"], ascending=[True, False, True])
    valid = enriched[enriched["R2"].fillna(-np.inf) >= min_r2].copy()
    valid = valid[np.isfinite(valid["R2"])]

    top_models = valid.groupby("property", group_keys=False).head(max(top_k, 1))
    best_models = valid.groupby("property", group_keys=False).head(1)

    top_model_ids = set(top_models["model_id"])
    best_model_ids = set(best_models["model_id"])
    top_predictions = predictions[predictions["model_id"].isin(top_model_ids)].copy()
    best_predictions = predictions[predictions["model_id"].isin(best_model_ids)].copy()

    r2_matrix = enriched.pivot(index="property", columns="index", values="R2")
    p_matrix = enriched.pivot(index="property", columns="index", values="p_value")
    equations_catalog = build_equations_catalog(enriched)
    equations_text = build_equations_by_index_text(equations_catalog)
    article_tables = build_article_statistical_tables(enriched)

    all_models_path = out_dir / "chapter5_all_models.csv"
    top_models_path = out_dir / "chapter5_top_models_per_property.csv"
    best_models_path = out_dir / "chapter5_best_models.csv"
    top_predictions_path = out_dir / "chapter5_top_model_predictions.csv"
    best_predictions_path = out_dir / "chapter5_best_model_predictions.csv"
    r2_matrix_path = out_dir / "chapter5_r2_matrix.csv"
    p_matrix_path = out_dir / "chapter5_pvalue_matrix.csv"
    equations_csv_path = out_dir / "chapter5_equations_by_index.csv"
    equations_md_path = out_dir / "chapter5_equations_by_index.md"
    article_tables_csv_path = out_dir / "chapter5_tables_3_to_12.csv"
    article_tables_md_path = out_dir / "chapter5_tables_3_to_12.md"
    report_path = out_dir / "chapter5_report.md"

    enriched.to_csv(all_models_path, index=False)
    top_models.to_csv(top_models_path, index=False)
    best_models.to_csv(best_models_path, index=False)
    top_predictions.to_csv(top_predictions_path, index=False)
    best_predictions.to_csv(best_predictions_path, index=False)
    r2_matrix.to_csv(r2_matrix_path)
    p_matrix.to_csv(p_matrix_path)
    equations_catalog.to_csv(equations_csv_path, index=False)
    equations_md_path.write_text(equations_text + "\n", encoding="utf-8")
    article_tables.to_csv(article_tables_csv_path, index=False)

    article_lines: list[str] = []
    if article_tables.empty:
        article_lines.append("No statistical tables available.")
    else:
        for idx in DEFAULT_INDEX_COLUMNS:
            subset = article_tables[article_tables["index_code"] == idx].copy()
            if subset.empty:
                continue
            table_num = int(subset["Table"].iloc[0])
            article_lines.append(f"Table {table_num}")
            article_lines.append(f"Statistical data for {INDEX_TITLES.get(idx, idx)}.")
            article_lines.append(
                "| Properties | N | a | b | r | r2 | F | p | Indicator |"
            )
            article_lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")
            for _, row in subset.iterrows():
                article_lines.append(
                    "| {prop} | {N} | {a} | {b} | {r} | {r2} | {F} | {p} | {ind} |".format(
                        prop=row["Properties"],
                        N=int(row["N"]) if pd.notna(row["N"]) else "NA",
                        a=_safe_float(row["a"], 6),
                        b=_safe_float(row["b"], 6),
                        r=_safe_float(row["r"], 6),
                        r2=_safe_float(row["r2"], 6),
                        F=_safe_float(row["F"], 6),
                        p=_safe_float(row["p"], 6),
                        ind=row["Indicator"],
                    )
                )
            article_lines.append("")
    article_tables_md_path.write_text("\n".join(article_lines).strip() + "\n", encoding="utf-8")

    lines: list[str] = []
    lines.append("# Chapter 5 - Regression Models")
    lines.append("")
    lines.append("## 5.1 Statistical Parameters")
    lines.append(
        f"Source models: `{Path(qspr_results_csv).name}` | "
        f"Source data: `{Path(qspr_data_csv).name}`"
    )
    lines.append(f"Total models evaluated: **{len(enriched)}**")
    lines.append(
        f"Selection rule: `R2 >= {min_r2}` and finite metrics | Top `{max(top_k, 1)}` per property."
    )
    lines.append("")
    lines.append("### Best model per property")
    lines.append("")
    lines.append("| Property | Index | Equation | n | r | R2 | Adj.R2 | p-value | RMSE | MAE | Quality |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for _, row in best_models.iterrows():
        lines.append(
            "| {property} | {index} | `{equation}` | {n} | {r} | {R2} | {adjusted_R2} | {p} | {rmse} | {mae} | {quality} |".format(
                property=row["property"],
                index=row["index"],
                equation=row["equation"],
                n=int(row["n"]),
                r=_safe_float(row["r"], 4),
                R2=_safe_float(row["R2"], 4),
                adjusted_R2=_safe_float(row["adjusted_R2"], 4),
                p=_safe_float(row["p_value"], 3),
                rmse=_safe_float(row["RMSE"], 4),
                mae=_safe_float(row["MAE"], 4),
                quality=row["model_quality"],
            )
        )
    lines.append("")
    all_properties = sorted(set(enriched["property"]))
    selected_properties = set(best_models["property"])
    missing_properties = [prop for prop in all_properties if prop not in selected_properties]
    if missing_properties:
        lines.append("### Properties without selected model")
        lines.append("")
        lines.append("| Property | Reason |")
        lines.append("|---|---|")
        for prop in missing_properties:
            subset = enriched[enriched["property"] == prop]
            finite_subset = subset[np.isfinite(subset["R2"])]
            if finite_subset.empty:
                reason = "No finite R2 (possible zero variance in target)."
            else:
                best_r2 = float(finite_subset["R2"].max())
                reason = f"Best R2 ({best_r2:.4f}) below threshold {min_r2:.4f}."
            lines.append(f"| {prop} | {reason} |")
        lines.append("")

    lines.append("## 5.2 Regression Equations Grouped by Index")
    lines.append("")
    lines.extend(equations_text.splitlines())
    lines.append("")

    lines.append("## 5.3 Top Candidate Models")
    lines.append("")
    for prop, group in top_models.groupby("property"):
        lines.append(f"### {prop}")
        lines.append("")
        lines.append("| Rank | Index | Equation | R2 | p-value | RMSE | MAE |")
        lines.append("|---:|---|---|---:|---:|---:|---:|")
        for rank, (_, row) in enumerate(group.iterrows(), start=1):
            lines.append(
                "| {rank} | {index} | `{equation}` | {R2} | {p} | {rmse} | {mae} |".format(
                    rank=rank,
                    index=row["index"],
                    equation=row["equation"],
                    R2=_safe_float(row["R2"], 4),
                    p=_safe_float(row["p_value"], 3),
                    rmse=_safe_float(row["RMSE"], 4),
                    mae=_safe_float(row["MAE"], 4),
                )
            )
        lines.append("")

    lines.append("## 5.4 Statistical Tables (Article Format)")
    lines.append("")
    lines.extend(article_lines)
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "all_models": all_models_path,
        "top_models": top_models_path,
        "best_models": best_models_path,
        "top_predictions": top_predictions_path,
        "best_predictions": best_predictions_path,
        "r2_matrix": r2_matrix_path,
        "pvalue_matrix": p_matrix_path,
        "equations_csv": equations_csv_path,
        "equations_markdown": equations_md_path,
        "article_tables_csv": article_tables_csv_path,
        "article_tables_markdown": article_tables_md_path,
        "markdown_report": report_path,
    }
