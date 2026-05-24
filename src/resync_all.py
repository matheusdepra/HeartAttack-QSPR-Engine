"""
CLI: Re-sync all drugs in the database against PubChem and recalculate indices.

Usage (from project root):
    ./venv/bin/python -m src.resync_all
"""
import logging
from app.core.database import SessionLocal
from app.models.drug import Drug
from app.scrapers.pubchem import process_drug_pubchem
from app.calculators.topological import calculate_for_drug

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def resync_all() -> None:
    db = SessionLocal()
    try:
        drugs = db.query(Drug).all()
        logger.info(f"Re-syncing {len(drugs)} drugs...")

        for drug in drugs:
            logger.info(f"[SYNC] {drug.name}")
            try:
                data = process_drug_pubchem(drug.name)
                if data:
                    drug.mw = data.get("mw") or drug.mw
                    drug.mw_source = data.get("mw_source") or drug.mw_source
                    drug.complexity = data.get("complexity") or drug.complexity
                    drug.complexity_source = data.get("complexity_source") or drug.complexity_source

                final_smiles = drug.smiles or data.get("smiles")
                if final_smiles:
                    ti = calculate_for_drug(drug.name, final_smiles)
                    if ti:
                        drug.ti_abc = ti.get("ABC")
                        drug.ti_ga = ti.get("GA")
                        drug.ti_ri = ti.get("RI")
                        drug.ti_rr = ti.get("RR")
                        drug.ti_h = ti.get("H")
                        drug.ti_sci = ti.get("SCI")
                        drug.ti_m1 = ti.get("M1")
                        drug.ti_m2 = ti.get("M2")
                        drug.ti_hm = ti.get("HM")
                        drug.ti_rm2 = ti.get("RM2")
                        drug.ti_f = ti.get("F")
                        drug.ti_hf = ti.get("HF")
            except Exception as e:
                logger.error(f"[FAIL] {drug.name}: {e}")

        db.commit()
        logger.info("Re-sync complete.")
    finally:
        db.close()


if __name__ == "__main__":
    resync_all()
