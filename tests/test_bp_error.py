import sys
import pandas as pd
sys.path.append('src')
from scrapers.pubchem import get_cid, get_smiles, calculate_theoretical_bp

# Reference data from the paper
reference_data = {
    'Apixaban': 770.5,
    'Aspirin': 321.4,
    'Atenolol': 508.0,
    'Candesartan': 754.8,
    'Captopril': 427.0,
    'Carvedilol': 655.2,
    'Dipyridamole': 806.5,
    'Quinapril': 662.0,
    'Ramipril': 616.2,
    'Rivaroxaban': 732.6,
    'Ticagrelor': 777.6,
    'Warfarin': 515.2
}

results = []
for drug, ref_bp in reference_data.items():
    cid = get_cid(drug)
    if not cid:
        print(f"Skipping {drug}, CID not found.")
        continue
    smiles = get_smiles(cid)
    if not smiles:
        print(f"Skipping {drug}, SMILES not found.")
        continue
        
    our_bp = calculate_theoretical_bp(smiles)
    if our_bp is not None:
        error = abs(ref_bp - our_bp)
        perc_error = (error / ref_bp) * 100
        results.append({
            'Drug': drug,
            'Ref_BP (C)': ref_bp,
            'Our_Calc_BP (C)': our_bp,
            'Error (C)': round(error, 2),
            'Error (%)': round(perc_error, 2)
        })

df = pd.DataFrame(results)
print(df.to_string())
print(f"\nMean Absolute Error: {df['Error (C)'].mean():.2f} C")
print(f"Mean Percentage Error: {df['Error (%)'].mean():.2f} %")
