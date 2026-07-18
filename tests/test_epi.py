import sys
import json
import urllib.request
import urllib.parse
import pandas as pd
import time
sys.path.append('src')
from scrapers.pubchem import get_cid, get_smiles

def fetch_epi_suite(smiles):
    url = f"https://episuite.dev/api/submit?smiles={urllib.parse.quote(smiles)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            bp = data.get('boilingPoint', {}).get('selectedValue', {}).get('value')
            return bp
    except Exception as e:
        print(f"Error fetching EPI for {smiles}: {e}")
        return None

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
        continue
    smiles = get_smiles(cid)
    if not smiles:
        continue
        
    epi_bp = fetch_epi_suite(smiles)
    if epi_bp is not None:
        error = abs(ref_bp - epi_bp)
        perc_error = (error / ref_bp) * 100
        results.append({
            'Drug': drug,
            'Ref_BP (C)': ref_bp,
            'EPI_BP (C)': round(epi_bp, 2),
            'Error (C)': round(error, 2),
            'Error (%)': round(perc_error, 2)
        })
    time.sleep(1)

df = pd.DataFrame(results)
print(df.to_string())
print(f"\nMean Absolute Error: {df['Error (C)'].mean():.2f} C")
print(f"Mean Percentage Error: {df['Error (%)'].mean():.2f} %")
