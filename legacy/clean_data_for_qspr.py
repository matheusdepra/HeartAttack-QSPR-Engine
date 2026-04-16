from __future__ import annotations

import argparse

from qspr_pipeline import (
    DEFAULT_INDEX_COLUMNS,
    DEFAULT_PROPERTY_COLUMNS,
    prepare_qspr_dataset,
)


def parse_columns(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Limpa e prepara o dataset para regressao QSPR."
    )
    parser.add_argument(
        "input_csv",
        nargs="?",
        default="merged_qspr_data.csv",
        help="CSV de entrada (default: merged_qspr_data.csv).",
    )
    parser.add_argument(
        "-o",
        "--output-csv",
        default="qspr_clean.csv",
        help="CSV de saida (default: qspr_clean.csv).",
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
        "--extra-numeric",
        default="",
        help="Outras colunas numericas separadas por virgula.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    properties = parse_columns(args.properties)
    indices = parse_columns(args.indices)
    extra_numeric = parse_columns(args.extra_numeric)

    df = prepare_qspr_dataset(
        input_csv=args.input_csv,
        output_csv=args.output_csv,
        property_columns=properties,
        index_columns=indices,
        extra_numeric_columns=extra_numeric,
    )
    print(df.dtypes)
    cols_to_show = [col for col in ["Drug"] + properties if col in df.columns][:10]
    if cols_to_show:
        print(df[cols_to_show].head())


if __name__ == "__main__":
    main()
