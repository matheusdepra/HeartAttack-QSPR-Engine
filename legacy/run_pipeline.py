from __future__ import annotations

import argparse
from pathlib import Path

from qspr_pipeline import (
    DEFAULT_INDEX_COLUMNS,
    DEFAULT_PROPERTY_COLUMNS,
    build_chapter5_report,
    calculate_topological_indices,
    merge_property_and_indices,
    prepare_qspr_dataset,
    run_qspr,
)


def parse_columns(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa pipeline QSPR completo a partir de um CSV base."
    )
    parser.add_argument(
        "input_csv",
        nargs="?",
        default="targets_article.csv",
        help="CSV base de propriedades (default: targets_article.csv).",
    )
    parser.add_argument(
        "--smiles-source-csv",
        default=None,
        help=(
            "CSV usado para calcular indices (deve conter SMILES). "
            "Se omitido, tenta <input>_with_smiles.csv e depois o proprio input."
        ),
    )
    parser.add_argument(
        "--drug-column",
        default="Drug",
        help="Coluna usada para identificar moleculas (default: Drug).",
    )
    parser.add_argument(
        "--smiles-column",
        default="SMILES",
        help="Coluna de SMILES (default: SMILES).",
    )
    parser.add_argument(
        "--properties",
        default=",".join(DEFAULT_PROPERTY_COLUMNS),
        help="Colunas de propriedades separadas por virgula.",
    )
    parser.add_argument(
        "--indices",
        default=",".join(DEFAULT_INDEX_COLUMNS),
        help="Colunas de indices separadas por virgula.",
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Diretorio de saida para os arquivos gerados (default: .).",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        help="Prefixo para arquivos de saida (default: nome do CSV base).",
    )
    parser.add_argument(
        "--min-points",
        type=int,
        default=2,
        help="Minimo de pontos validos por regressao (default: 2).",
    )
    parser.add_argument(
        "--chapter5-report",
        action="store_true",
        help="Gera pacote de apresentacao dos modelos (estilo capitulo 5).",
    )
    parser.add_argument(
        "--chapter5-top-k",
        type=int,
        default=3,
        help="Top modelos por propriedade no relatorio do capitulo 5 (default: 3).",
    )
    parser.add_argument(
        "--chapter5-min-r2",
        type=float,
        default=0.0,
        help="R2 minimo para selecao no relatorio do capitulo 5 (default: 0.0).",
    )
    return parser.parse_args()


def resolve_smiles_source(input_csv: Path, explicit_path: str | None) -> Path:
    if explicit_path:
        return Path(explicit_path).resolve()

    inferred = input_csv.with_name(f"{input_csv.stem}_with_smiles.csv")
    if inferred.exists():
        return inferred.resolve()
    return input_csv


def main() -> None:
    args = parse_args()

    input_csv = Path(args.input_csv).resolve()
    if not input_csv.exists():
        raise FileNotFoundError(f"Arquivo de entrada nao encontrado: {input_csv}")

    smiles_source_csv = resolve_smiles_source(input_csv, args.smiles_source_csv)
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    prefix = args.prefix or input_csv.stem
    indices_csv = out_dir / f"{prefix}_topological_indices.csv"
    merged_csv = out_dir / f"{prefix}_merged_qspr_data.csv"
    clean_csv = out_dir / f"{prefix}_qspr_clean.csv"
    results_csv = out_dir / f"{prefix}_qspr_results.csv"

    property_cols = parse_columns(args.properties)
    index_cols = parse_columns(args.indices)

    df_indices = calculate_topological_indices(
        input_csv=smiles_source_csv,
        output_csv=indices_csv,
        drug_column=args.drug_column,
        smiles_column=args.smiles_column,
        include_edge_partition=True,
    )

    df_merged = merge_property_and_indices(
        properties_csv=input_csv,
        indices_csv=indices_csv,
        output_csv=merged_csv,
        drug_column=args.drug_column,
        property_smiles_column=args.smiles_column,
        index_smiles_column=args.smiles_column,
        join="inner",
    )

    df_clean = prepare_qspr_dataset(
        input_csv=merged_csv,
        output_csv=clean_csv,
        property_columns=property_cols,
        index_columns=index_cols,
    )

    df_qspr = run_qspr(
        df=df_clean,
        property_columns=property_cols,
        index_columns=index_cols,
        output_csv=results_csv,
        min_points=args.min_points,
    )

    chapter5_dir = out_dir / f"{prefix}_chapter5"
    chapter5_paths = None
    if args.chapter5_report:
        chapter5_paths = build_chapter5_report(
            qspr_results_csv=results_csv,
            qspr_data_csv=clean_csv,
            output_dir=chapter5_dir,
            top_k=args.chapter5_top_k,
            min_r2=args.chapter5_min_r2,
        )

    print(f"CSV base: {input_csv}")
    print(f"CSV para indices (SMILES): {smiles_source_csv}")
    print(f"Indices calculados: {len(df_indices)} linhas -> {indices_csv}")
    print(f"Merge concluido: {len(df_merged)} linhas -> {merged_csv}")
    print(f"Dataset limpo: {len(df_clean)} linhas -> {clean_csv}")
    print(f"Regressoes QSPR: {len(df_qspr)} linhas -> {results_csv}")
    if chapter5_paths:
        print(f"Relatorio capitulo 5: {chapter5_paths['markdown_report']}")


if __name__ == "__main__":
    main()
