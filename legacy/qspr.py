from __future__ import annotations

import argparse

from qspr_pipeline import DEFAULT_INDEX_COLUMNS, DEFAULT_PROPERTY_COLUMNS, run_qspr_from_csv


def parse_columns(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa regressao QSPR (1 indice vs 1 propriedade).")
    parser.add_argument(
        "input_csv",
        nargs="?",
        default="qspr_clean.csv",
        help="CSV de entrada para regressao (default: qspr_clean.csv).",
    )
    parser.add_argument(
        "-o",
        "--output-csv",
        default="qspr_results.csv",
        help="CSV de saida com resultados (default: qspr_results.csv).",
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
        "--min-points",
        type=int,
        default=2,
        help="Minimo de pontos validos por regressao (default: 2).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out = run_qspr_from_csv(
        input_csv=args.input_csv,
        output_csv=args.output_csv,
        property_columns=parse_columns(args.properties),
        index_columns=parse_columns(args.indices),
        min_points=args.min_points,
    )
    print(out.head())
    print(f"\nTotal de regressões executadas: {len(out)}")


if __name__ == "__main__":
    main()
