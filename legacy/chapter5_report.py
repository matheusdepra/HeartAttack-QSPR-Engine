from __future__ import annotations

import argparse
from pathlib import Path

from qspr_pipeline import build_chapter5_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera arquivos de apresentacao dos modelos QSPR para formato de capitulo 5."
    )
    parser.add_argument(
        "qspr_results_csv",
        nargs="?",
        default="targets_article_qspr_results.csv",
        help="CSV com resultados de regressao (default: targets_article_qspr_results.csv).",
    )
    parser.add_argument(
        "qspr_data_csv",
        nargs="?",
        default="targets_article_qspr_clean.csv",
        help="CSV base usado na regressao (default: targets_article_qspr_clean.csv).",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=None,
        help=(
            "Diretorio de saida. "
            "Default: <nome_do_results_csv>_chapter5 (sem extensao)."
        ),
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Top modelos por propriedade (default: 3).",
    )
    parser.add_argument(
        "--min-r2",
        type=float,
        default=0.0,
        help="Filtra modelos com R2 minimo (default: 0.0).",
    )
    return parser.parse_args()


def _default_output_dir(results_csv: str) -> Path:
    p = Path(results_csv)
    return Path(f"{p.stem}_chapter5")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir) if args.output_dir else _default_output_dir(args.qspr_results_csv)
    paths = build_chapter5_report(
        qspr_results_csv=args.qspr_results_csv,
        qspr_data_csv=args.qspr_data_csv,
        output_dir=output_dir,
        top_k=args.top_k,
        min_r2=args.min_r2,
    )

    print("Arquivos gerados para apresentacao do capitulo 5:")
    for key, path in paths.items():
        print(f"- {key}: {path.resolve()}")


if __name__ == "__main__":
    main()
