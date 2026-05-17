import os
import sys
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from db.models import get_engine, get_session, Drug

# Reference values from Rasheed et al. (2023) Table 2 (Approximate based on earlier benchmarking)
GOLDEN_SET = {
    "Aspirin": {"BP": 140.0, "VP": 0.0000001, "MR": 44.71},
    "Atenolol": {"BP": 508.0, "VP": 0.0},
    "Warfarin": {"BP": 494.37, "VP": 0.09, "MR": 87.73},
    "Metoprolol": {"BP": 394.0, "VP": 0.0003},
    "Propranolol": {"BP": 447.0, "VP": 0.0002},
    "Captopril": {"BP": 427.0, "VP": 0.0},
    "Lisinopril": {"BP": 666.0, "VP": 0.0},
}

def audit_library():
    print("🔬 CardioQSPR Data Integrity Audit\n" + "="*40)
    
    engine = get_engine()
    session = get_session(engine)
    
    try:
        db_drugs = session.query(Drug).all()
        if not db_drugs:
            print("❌ Library is empty. Please run 'Load Defaults' in the UI first.")
            return

        results = []
        for d in db_drugs:
            name = d.name.capitalize()
            if name in GOLDEN_SET:
                expected = GOLDEN_SET[name]
                results.append({
                    "Drug": name,
                    "BP_Obs": d.bp,
                    "BP_Exp": expected.get("BP"),
                    "VP_Obs": d.vp,
                    "VP_Exp": expected.get("VP"),
                    "MR_Obs": d.mr,
                    "MR_Exp": expected.get("MR")
                })

        df = pd.DataFrame(results)
        if df.empty:
            print("⚠️ None of the 13 hallmark drugs found in the library.")
            return

        print(df.to_string(index=False))
        
        # Calculate discrepancies
        print("\n🚩 Discrepancies (>10%):")
        for _, row in df.iterrows():
            if row['BP_Obs'] is not None and row['BP_Exp'] is not None:
                diff = abs(row['BP_Obs'] - row['BP_Exp']) / row['BP_Exp']
                if diff > 0.1:
                    print(f"  - {row['Drug']} BP: Diff {diff:.1%}")

    finally:
        session.close()

if __name__ == "__main__":
    audit_library()
