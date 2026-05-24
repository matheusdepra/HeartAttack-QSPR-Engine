"""
CLI: Generate QSPR report and visualisation plots for all drugs in the database.

Usage (from project root):
    ./venv/bin/python -m src.generate_qspr_report
    ./venv/bin/python -m src.generate_qspr_report --output data/qspr_results
"""
import logging
import argparse
import os
import pandas as pd

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.drug import Drug
from app.calculators.qspr import build_report
from app.visualizers.report_plots import generate_structure_grid, generate_correlation_figures

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main(output_dir: str | None = None) -> None:
    logger.info("Starting QSPR report generation...")
    db = SessionLocal()
    resolved_output_dir = output_dir or str(settings.QSPR_RESULTS_DIR)

    try:
        paths = build_report(db, output_dir=resolved_output_dir)

        drugs = db.query(Drug).all()
        drugs_df = pd.DataFrame([{"name": d.name, "smiles": d.smiles} for d in drugs])

        plot_dir = str(settings.PLOTS_DIR)
        os.makedirs(plot_dir, exist_ok=True)

        generate_structure_grid(drugs_df, os.path.join(plot_dir, "molecule_structures.png"))

        all_models_df = pd.read_csv(paths["all_models"])
        generate_correlation_figures(all_models_df, plot_dir)

        logger.info(f"Report:  {paths['report']}")
        logger.info(f"Figures: {plot_dir}")
        print(f"\nReport generated: {paths['report']}")
        print(f"Figures generated in: {plot_dir}")

    except Exception as e:
        logger.error(f"Error generating QSPR report: {e}", exc_info=True)
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QSPR report generator")
    parser.add_argument("--output", default=str(settings.QSPR_RESULTS_DIR), help="Output directory for results")
    args = parser.parse_args()
    main(args.output)
