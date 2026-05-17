"""
Topological Index Calculator
============================
Ported from legacy/qspr_pipeline.py.
Calculates 10 degree-based topological indices from a SMILES string:
  RI, RR, H, SCI, M1, M2, HM, RM2, F, HF

These are the same indices used in the QSPR analysis of the reference article
(Rasheed et al.) for heart attack drug physicochemical property prediction.
"""
from __future__ import annotations

from collections import Counter
from typing import Optional

import numpy as np
from rdkit import Chem

INDEX_NAMES = ["ABC", "GA", "RI", "RR", "H", "SCI", "M1", "M2", "HM", "RM2", "F", "HF"]

INDEX_TITLES = {
    "ABC": "Atom-Bond Connectivity Index ABC(G)",
    "GA":  "Geometric-Arithmetic Index GA(G)",
    "RI":  "Randic Index R(G)",
    "RR":  "Reciprocal Randic Index RR(G)",
    "H":   "Harmonic Index H(G)",
    "SCI": "Sum Connectivity Index SC(G)",
    "M1":  "First Zagreb Index M1(G)",
    "M2":  "Second Zagreb Index M2(G)",
    "HM":  "Hyper Zagreb Index HM(G)",
    "RM2": "Redefined Second Zagreb Index RM2(G)",
    "F":   "Forgotten Index F(G)",
    "HF":  "Hyper Forgotten Index HF(G)",
}

INDEX_SYMBOLS = {
    "ABC": "ABC(G)",
    "GA":  "GA(G)",
    "RI":  "R(G)",
    "RR":  "RR(G)",
    "H":   "H(G)",
    "SCI": "SC(G)",
    "M1":  "M1(G)",
    "M2":  "M2(G)",
    "HM":  "HM(G)",
    "RM2": "RM2(G)",
    "F":   "F(G)",
    "HF":  "HF(G)",
}


def edge_partition_from_mol(mol: Chem.Mol) -> Counter:
    """Build edge partition: maps (du, dv) -> count of bonds with those endpoint degrees."""
    degrees = {atom.GetIdx(): atom.GetDegree() for atom in mol.GetAtoms()}
    part: Counter = Counter()
    for bond in mol.GetBonds():
        a = bond.GetBeginAtomIdx()
        b = bond.GetEndAtomIdx()
        key = tuple(sorted((degrees[a], degrees[b])))
        part[key] += 1
    return part


def calc_indices_from_partition(part: Counter) -> dict[str, float]:
    """Calculate all 12 topological indices from an edge partition."""
    values = {k: 0.0 for k in INDEX_NAMES}
    for (du, dv), freq in part.items():
        if du * dv > 0:
            values["ABC"] += freq * np.sqrt((du + dv - 2) / (du * dv))
            values["GA"]  += freq * ((2.0 * np.sqrt(du * dv)) / (du + dv))
        values["RI"]  += freq * (1.0 / np.sqrt(du * dv))
        values["RR"]  += freq * np.sqrt(du * dv)
        values["H"]   += freq * (2.0 / (du + dv))
        values["SCI"] += freq * (1.0 / np.sqrt(du + dv))
        values["M1"]  += freq * (du + dv)
        values["M2"]  += freq * (du * dv)
        values["HM"]  += freq * ((du + dv) ** 2)
        values["RM2"] += freq * ((du - 1) * (dv - 1))
        values["F"]   += freq * (du ** 2 + dv ** 2)
        values["HF"]  += freq * ((du ** 2 + dv ** 2) ** 2)
    return values


def smiles_to_indices(smiles: str) -> tuple[Counter, dict[str, float]]:
    """
    Given a SMILES string, return (edge_partition, index_dict).
    Raises ValueError on invalid/empty SMILES.
    """
    smiles_clean = (smiles or "").strip()
    if not smiles_clean:
        raise ValueError("SMILES vazio.")
    mol = Chem.MolFromSmiles(smiles_clean)
    if mol is None:
        raise ValueError(f"SMILES invalido: {smiles_clean}")
    mol = Chem.RemoveHs(mol)
    if mol.GetNumAtoms() == 0:
        raise ValueError(f"Molecula vazia apos remover H: {smiles_clean}")
    part = edge_partition_from_mol(mol)
    return part, calc_indices_from_partition(part)


def calculate_for_drug(name: str, smiles: str) -> Optional[dict[str, float]]:
    """
    Convenience wrapper for a single drug.
    Returns dict with index values, or None if SMILES is invalid.
    """
    if not smiles:
        return None
    try:
        _, indices = smiles_to_indices(smiles)
        return indices
    except ValueError:
        return None
