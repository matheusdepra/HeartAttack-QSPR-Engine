from __future__ import annotations

import argparse

from qspr_pipeline import merge_property_and_indices


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Faz merge entre propriedades e indices topologicos."
    )
    parser.add_argument(
        "properties_csv",
        nargs="?",
        default="targets_article_with_smiles.csv",
        help="CSV de propriedades (default: targets_article_with_smiles.csv).",
    )
    parser.add_argument(
        "indices_csv",
        nargs="?",
        default="topological_indices.csv",
        help="CSV de indices topologicos (default: topological_indices.csv).",
    )
    parser.add_argument(
        "-o",
        "--output-csv",
        default="merged_qspr_data.csv",
        help="CSV de saida (default: merged_qspr_data.csv).",
    )
    parser.add_argument(
        "--drug-column",
        default="Drug",
        help="Coluna usada para merge (default: Drug).",
    )
    parser.add_argument(
        "--property-smiles-column",
        default="SMILES",
        help="Coluna de SMILES no CSV de propriedades (default: SMILES).",
    )
    parser.add_argument(
        "--index-smiles-column",
        default="SMILES",
        help="Coluna de SMILES no CSV de indices (default: SMILES).",
    )
    parser.add_argument(
        "--join",
        choices=["inner", "left", "right", "outer"],
        default="inner",
        help="Tipo de join (default: inner).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = merge_property_and_indices(
        properties_csv=args.properties_csv,
        indices_csv=args.indices_csv,
        output_csv=args.output_csv,
        drug_column=args.drug_column,
        property_smiles_column=args.property_smiles_column,
        index_smiles_column=args.index_smiles_column,
        join=args.join,
    )
    print(df.head())
    print(f"\nTotal de moleculas: {len(df)}")
    if "SMILES_match" in df.columns:
        mismatch_count = int((~df["SMILES_match"]).sum())
        print(f"SMILES divergentes: {mismatch_count}")


if __name__ == "__main__":
    main()
