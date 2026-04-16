import os
import logging
from db.models import get_engine, init_db, get_session, Drug
from scrapers.pubchem import process_drug_pubchem
from calculators.topological import calculate_for_drug

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_pipeline(source_url: str = 'data/raw/drogas_iniciais.txt'):
    logger.info("Initializing database...")
    engine = get_engine()
    init_db(engine)
    session = get_session(engine)
    
    logger.info(f"Fetching drug list from {source_url}...")
    drug_names = []
    try:
        with open(source_url, 'r') as f:
            drug_names = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Failed to read txt file: {e}")

    logger.info(f"Retrieved {len(drug_names)} drugs to process.")
    
    for name in drug_names:
        # Check if already exists in DB
        existing = session.query(Drug).filter_by(name=name).first()
        if existing:
            logger.info(f"Drug {name} already in Database. Skipping API call.")
            continue
            
        logger.info(f"Fetching PubChem data for {name}...")
        pubchem_data = process_drug_pubchem(name)

        # Calculate topological indices from SMILES
        smiles = pubchem_data.get("smiles")
        ti = calculate_for_drug(name, smiles) if smiles else None
        if ti:
            logger.info(f"Topological indices calculated for {name}: RI={ti['RI']:.4f}, M1={ti['M1']:.4f}")
        else:
            logger.warning(f"Could not calculate topological indices for {name}.")
        
        drug = Drug(
            name=name,
            source_url=source_url,
            **pubchem_data,
            ti_ri=ti["RI"]  if ti else None,
            ti_rr=ti["RR"]  if ti else None,
            ti_h=ti["H"]    if ti else None,
            ti_sci=ti["SCI"] if ti else None,
            ti_m1=ti["M1"]  if ti else None,
            ti_m2=ti["M2"]  if ti else None,
            ti_hm=ti["HM"]  if ti else None,
            ti_rm2=ti["RM2"] if ti else None,
            ti_f=ti["F"]    if ti else None,
            ti_hf=ti["HF"]  if ti else None,
        )
        session.add(drug)
        session.commit()
        logger.info(f"Saved {name} to Database.")
        
    logger.info("Pipeline completed successfully.")

if __name__ == '__main__':
    run_pipeline()
