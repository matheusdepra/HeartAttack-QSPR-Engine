"""
Agnostic Figure Generation Module
=================================
Generates article-style visualizations matching Rasheed et al. (2023)
style, but dynamically adjusting to the number of drugs provided.
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Force non-interactive backend for server environments
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from rdkit import Chem
from rdkit.Chem import Draw

from calculators.topological import INDEX_NAMES

def generate_structure_grid(df: pd.DataFrame, output_path: str | Path, mols_per_row: int = 4):
    """
    Generates a 2D grid image of molecular structures.
    Agnostic to the number of drugs.
    """
    df_valid = df.dropna(subset=['smiles'])
    if df_valid.empty:
        return
    
    mols = []
    legends = []
    for _, row in df_valid.iterrows():
        mol = Chem.MolFromSmiles(row['smiles'])
        if mol:
            mols.append(mol)
            legends.append(row['name'])
    
    if not mols:
        return

    n_mols = len(mols)
    n_rows = math.ceil(n_mols / mols_per_row)
    
    # RDKit drawing
    img = Draw.MolsToGridImage(
        mols, 
        molsPerRow=mols_per_row, 
        subImgSize=(300, 300), 
        legends=legends
    )
    
    img.save(str(output_path))
    print(f"Structure grid saved to {output_path}")

def generate_correlation_figures(qspr_df: pd.DataFrame, output_dir: str | Path):
    """
    Generates line plots of correlation coefficient (r) vs Topological Indices.
    - Replicates Figure 2 (Individual Property subplots)
    - Replicates Figure 3 (Global comparison)
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if qspr_df.empty:
        return

    # 1. Individual Property Plots (Figure 2 style)
    properties = qspr_df['property'].unique()
    
    sns.set_theme(style="whitegrid")
    
    for prop in properties:
        sub = qspr_df[qspr_df['property'] == prop].copy()
        # Sort by INDEX_NAMES order
        sub['index'] = pd.Categorical(sub['index'], categories=INDEX_NAMES, ordered=True)
        sub = sub.sort_values('index')
        
        plt.figure(figsize=(10, 6))
        plt.plot(sub['index'], abs(sub['r']), marker='o', linestyle='-', linewidth=2, color='#1f77b4')
        plt.title(f"Correlation of {prop} vs Topological Indices", fontsize=14, fontweight='bold')
        plt.xlabel("Topological Indices", fontsize=12)
        plt.ylabel("Correlation Coefficient |r|", fontsize=12)
        plt.ylim(0, 1.05)
        plt.tight_layout()
        plt.savefig(out_dir / f"correlation_{prop.lower()}.png", dpi=150)
        plt.close()

    # 2. Global Comparison Plot (Figure 3 style)
    plt.figure(figsize=(12, 7))
    
    # Qualitative color palette
    palette = sns.color_palette("bright", n_colors=len(properties))
    
    for i, prop in enumerate(properties):
        sub = qspr_df[qspr_df['property'] == prop].copy()
        sub['index'] = pd.Categorical(sub['index'], categories=INDEX_NAMES, ordered=True)
        sub = sub.sort_values('index')
        
        plt.plot(sub['index'], abs(sub['r']), marker='s', markersize=6, label=prop, color=palette[i], alpha=0.8)

    plt.title("Comparison of Correlation Coefficients (|r|)", fontsize=16, fontweight='bold')
    plt.xlabel("Topological Indices", fontsize=14)
    plt.ylabel("Correlation Coefficient |r|", fontsize=14)
    plt.ylim(0, 1.05)
    plt.legend(title="Physicochemical Properties", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(out_dir / "comparison_all_correlations.png", dpi=300)
    plt.close()
    
    print(f"Correlation figures saved to {out_dir}")
