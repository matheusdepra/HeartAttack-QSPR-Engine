from __future__ import annotations

import argparse

from qspr_pipeline import calculate_topological_indices


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calcula indices topologicos a partir de um CSV com colunas de droga e SMILES."
    )
    parser.add_argument(
        "input_csv",
        nargs="?",
        default="targets_article_with_smiles.csv",
        help="CSV de entrada com SMILES (default: targets_article_with_smiles.csv).",
    )
    parser.add_argument(
        "-o",
        "--output-csv",
        default="topological_indices.csv",
        help="CSV de saida (default: topological_indices.csv).",
    )
    parser.add_argument(
        "--drug-column",
        default="Drug",
        help="Nome da coluna de identificacao da molecula (default: Drug).",
    )
    parser.add_argument(
        "--smiles-column",
        default="SMILES",
        help="Nome da coluna de SMILES (default: SMILES).",
    )
    parser.add_argument(
        "--no-edge-partition",
        action="store_true",
        help="Nao inclui a coluna edge_partition.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_df = calculate_topological_indices(
        input_csv=args.input_csv,
        output_csv=args.output_csv,
        drug_column=args.drug_column,
        smiles_column=args.smiles_column,
        include_edge_partition=not args.no_edge_partition,
    )
    error_count = int(out_df["error"].notna().sum()) if "error" in out_df.columns else 0
    print(out_df.head())
    print(f"\nTotal de moleculas processadas: {len(out_df)}")
    print(f"Total com erro: {error_count}")


if __name__ == "__main__":
    main()
