import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.models import get_session, get_engine, Drug
from calculators.topological import calculate_for_drug
from scrapers.pubchem import process_drug_pubchem

engine = get_engine("../data/drugs.db")
db = get_session(engine)
drugs = db.query(Drug).all()
for drug in drugs:
    print(f"Syncing {drug.name}...")
    try:
        data = process_drug_pubchem(drug.name)
        if data:
            drug.mw = data.get("mw")
            drug.mw_source = data.get("mw_source")
            drug.complexity = data.get("complexity")
            drug.complexity_source = data.get("complexity_source")
            
            final_smiles = drug.smiles or data.get("smiles")
            if final_smiles:
                ti = calculate_for_drug(drug.name, final_smiles)
                if ti:
                    drug.ti_abc = ti.get("ABC")
                    drug.ti_ga = ti.get("GA")
    except Exception as e:
        print(f"Failed {drug.name}: {e}")
        
db.commit()
print("Done!")
