"""
CLI Pipeline: fetch drugs from a text file, sync with PubChem, and persist to DB.

Usage (from project root):
    ./venv/bin/python -m src.main
    ./venv/bin/python -m src.main --source data/raw/drogas_iniciais.txt
"""
import logging
import argparse
from pathlib import Path

# Bootstrap the app package (sets up DB engine via config)
from app.core.database import SessionLocal
from app.models.drug import Drug
from app.scrapers.pubchem import process_drug_pubchem
from app.calculators.topological import calculate_for_drug

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run_pipeline(source_path: str = "data/raw/drogas_iniciais.txt") -> None:
    logger.info("Starting ingestion pipeline...")
    db = SessionLocal()

    try:
        drug_file = Path(source_path)
        if not drug_file.exists():
            logger.error(f"Source file not found: {drug_file}")
            return

        drug_names = [line.strip() for line in drug_file.read_text().splitlines() if line.strip()]
        logger.info(f"Found {len(drug_names)} drugs to process from {drug_file}")

        for name in drug_names:
            existing = db.query(Drug).filter_by(name=name).first()
            if existing:
                logger.info(f"[SKIP] {name} — already in database.")
                continue

            logger.info(f"[FETCH] {name} — querying PubChem...")
            try:
                pubchem_data = process_drug_pubchem(name)
            except Exception as e:
                logger.warning(f"[WARN] PubChem failed for {name}: {e}")
                pubchem_data = {}

            smiles = pubchem_data.get("smiles")
            ti = None
            if smiles:
                try:
                    ti = calculate_for_drug(name, smiles)
                    logger.info(f"[CALC] {name} — RI={ti['RI']:.4f}, M1={ti['M1']:.4f}")
                except Exception as e:
                    logger.warning(f"[WARN] Topological indices failed for {name}: {e}")

            drug = Drug(
                name=name,
                **{k: v for k, v in pubchem_data.items() if k != "name"},
                ti_abc=ti["ABC"] if ti else None,
                ti_ga=ti["GA"] if ti else None,
                ti_ri=ti["RI"] if ti else None,
                ti_rr=ti["RR"] if ti else None,
                ti_h=ti["H"] if ti else None,
                ti_sci=ti["SCI"] if ti else None,
                ti_m1=ti["M1"] if ti else None,
                ti_m2=ti["M2"] if ti else None,
                ti_hm=ti["HM"] if ti else None,
                ti_rm2=ti["RM2"] if ti else None,
                ti_f=ti["F"] if ti else None,
                ti_hf=ti["HF"] if ti else None,
            )
            db.add(drug)
            db.commit()
            logger.info(f"[SAVED] {name}")

    finally:
        db.close()

    logger.info("Pipeline completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Drug ingestion pipeline")
    parser.add_argument("--source", default="data/raw/drogas_iniciais.txt", help="Path to drug names .txt file")
    args = parser.parse_args()
    run_pipeline(args.source)
