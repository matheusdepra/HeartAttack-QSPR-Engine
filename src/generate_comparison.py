import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import linregress

# Drug list from paper
PAPER_DRUGS = [
    'apixaban', 'aspirin', 'atenolol', 'candesartan', 'captopril', 'carvedilol',
    'dipyridamole', 'edoxaban', 'quinapril', 'ramipril', 'rivaroxaban',
    'ticagrelor', 'warfarin'
]

# Paper's r values from Table 13
PAPER_R = {
    'RI':  {'BP': 0.944,  'VP': 0.7691, 'EV': 0.9392, 'FP': 0.9097, 'MR': 0.8084, 'ST': 0.4247, 'MV': 0.7539},
    'RR':  {'BP': 0.9664, 'VP': 0.8102, 'EV': 0.966,  'FP': 0.9253, 'MR': 0.9784, 'ST': 0.6556, 'MV': 0.9027},
    'H':   {'BP': 0.9263, 'VP': 0.788,  'EV': 0.929,  'FP': 0.8858, 'MR': 0.9182, 'ST': 0.6906, 'MV': 0.8653},
    'SCI': {'BP': 0.9657, 'VP': 0.8018, 'EV': 0.9677, 'FP': 0.9297, 'MR': 0.9898, 'ST': 0.6535, 'MV': 0.9273},
    'M1':  {'BP': 0.9446, 'VP': 0.8035, 'EV': 0.9446, 'FP': 0.9014, 'MR': 0.9332, 'ST': 0.6803, 'MV': 0.8637},
}

DB_PROP_MAP = {
    'BP': 'bp', 'VP': 'vp', 'EV': 'ev', 'FP': 'fp', 'MR': 'mr', 'ST': 'st', 'MV': 'mv'
}
DB_INDEX_MAP = {
    'RI': 'ti_ri', 'RR': 'ti_rr', 'H': 'ti_h', 'SCI': 'ti_sci', 'M1': 'ti_m1'
}

def compare():
    conn = sqlite3.connect('data/drugs.db')
    # Filter for the exact 13 drugs using case-insensitive set
    all_drugs = pd.read_sql("SELECT * FROM drugs", conn)
    conn.close()
    
    # Normalize names to lowercase for matching
    all_drugs['name_lower'] = all_drugs['name'].str.lower()
    paper_drugs_lower = [d.lower() for d in PAPER_DRUGS]
    
    # Filter to get exactly one record per paper drug (the one with most TIs)
    df = all_drugs[all_drugs['name_lower'].isin(paper_drugs_lower)].copy()
    df = df.sort_values('ti_ri', ascending=False).drop_duplicates('name_lower')

    print(f"Drugs found and matched: {len(df)}")
    if len(df) < 13:
         missing = set(paper_drugs_lower) - set(df['name_lower'])
         print(f"Missing drugs: {missing}")
    
    # Calculate our r values
    results = []
    indices = sorted(PAPER_R.keys())
    props = sorted(next(iter(PAPER_R.values())).keys())

    for idx_label in indices:
        db_idx = DB_INDEX_MAP[idx_label]
        for prop_label in props:
            db_prop = DB_PROP_MAP[prop_label]
            
            valid = df[[db_idx, db_prop]].dropna()
            if len(valid) < 3:
                continue
                
            slope, intercept, r_val, p_val, std_err = linregress(valid[db_idx], valid[db_prop])
            paper_r_val = PAPER_R[idx_label][prop_label]
            
            results.append({
                'Index': idx_label,
                'Property': prop_label,
                'Paper_r': round(paper_r_val, 4),
                'Our_r': round(abs(r_val), 4),
                'Diff': round(abs(r_val) - paper_r_val, 4),
                'Our_R2': round(r_val**2, 4),
                'Paper_R2': round(paper_r_val**2, 4)
            })

    res_df = pd.DataFrame(results)
    
    # Summary of best improvements
    print("\n=== Side-by-Side Comparison (R2) ===")
    pivoted = res_df.pivot(index='Property', columns='Index', values='Diff')
    print(pivoted)
    
    # Generate Markdown Table for Article Comparison
    md = "# Side-by-Side Methodology Comparison\n\n"
    md += "Comparison of Correlation Coefficients ($r$) for the same 13 drugs used in the paper.\n\n"
    md += "| Index | Property | Paper $r$ | Our $r$ | Diff | Result |\n"
    md += "|---|---|---|---|---|---|\n"
    
    for _, row in res_df.iterrows():
        status = "✨ Better" if row['Diff'] > 0.05 else ("✅ Matches" if abs(row['Diff']) <= 0.05 else "❌ Lower")
        md += f"| {row['Index']} | {row['Property']} | {row['Paper_r']} | {row['Our_r']} | {row['Diff']:+.4f} | {status} |\n"
    
    with open('data/qspr_results/methodology_comparison.md', 'w') as f:
        f.write(md)
    
    print("\nMarkdown report generated at data/qspr_results/methodology_comparison.md")

if __name__ == '__main__':
    compare()
