#!/usr/bin/env python3
"""Fetch SMILES strings from PubChem for drugs listed in a CSV file."""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen


PUBCHEM_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"


def get_json(url: str) -> dict:
    with urlopen(url, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def get_cid(drug_name: str) -> Optional[int]:
    encoded = quote(drug_name.strip())
    urls = [
        f"{PUBCHEM_BASE}/compound/name/{encoded}/cids/JSON",
        f"{PUBCHEM_BASE}/compound/name/{encoded}/cids/JSON?name_type=word",
        f"{PUBCHEM_BASE}/compound/name/{encoded}/cids/JSON?name_type=complete",
    ]
    for url in urls:
        try:
            data = get_json(url)
        except HTTPError as exc:
            if exc.code == 404:
                continue
            raise
        cids = data.get("IdentifierList", {}).get("CID", [])
        if cids:
            return int(cids[0])
    return None


def extract_cid_from_text(value: str) -> Optional[int]:
    token = value.strip()
    if token.isdigit():
        return int(token)
    match = re.search(r"pubchem\.ncbi\.nlm\.nih\.gov/compound/(\d+)", token, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def get_smiles_from_record(cid: int) -> tuple[Optional[str], Optional[str]]:
    url = f"{PUBCHEM_BASE}/compound/cid/{cid}/record/JSON"
    data = get_json(url)
    canonical = None
    isomeric = None
    for compound in data.get("PC_Compounds", []):
        for prop in compound.get("props", []):
            urn = prop.get("urn", {})
            label = (urn.get("label") or "").lower()
            name = (urn.get("name") or "").lower()
            if label != "smiles":
                continue
            sval = prop.get("value", {}).get("sval")
            if not sval:
                continue
            if name == "canonical":
                canonical = sval
            elif name == "isomeric":
                isomeric = sval
            elif canonical is None:
                canonical = sval
    return canonical, isomeric


def get_smiles(cid: int) -> tuple[Optional[str], Optional[str]]:
    url = (
        f"{PUBCHEM_BASE}/compound/cid/{cid}"
        "/property/CanonicalSMILES,IsomericSMILES/JSON"
    )
    canonical = None
    isomeric = None
    try:
        data = get_json(url)
        properties = data.get("PropertyTable", {}).get("Properties", [])
        if properties:
            row = properties[0]
            canonical = row.get("CanonicalSMILES")
            isomeric = row.get("IsomericSMILES")
    except HTTPError as exc:
        if exc.code != 404:
            raise

    if canonical or isomeric:
        return canonical, isomeric
    return get_smiles_from_record(cid)


def derive_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}_with_smiles.csv")


def process_csv(
    input_path: Path,
    output_path: Path,
    drug_column: str,
    smiles_column: str,
    cid_column: str,
    delay: float,
) -> None:
    with input_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header row.")
        if drug_column not in reader.fieldnames:
            raise ValueError(
                f"Drug column '{drug_column}' not found. Available columns: {reader.fieldnames}"
            )
        rows = list(reader)

    fieldnames = list(reader.fieldnames)
    if smiles_column not in fieldnames:
        fieldnames.append(smiles_column)
    if cid_column not in fieldnames:
        fieldnames.append(cid_column)

    total = len(rows)
    found = 0

    for index, row in enumerate(rows, start=1):
        drug = (row.get(drug_column) or "").strip()
        if not drug:
            print(f"[{index}/{total}] Empty drug name, skipped.")
            row[smiles_column] = ""
            row[cid_column] = ""
            continue

        try:
            cid = extract_cid_from_text(drug) or get_cid(drug)
            if cid is None:
                print(f"[{index}/{total}] {drug}: not found in PubChem.")
                row[smiles_column] = ""
                row[cid_column] = ""
            else:
                canonical_smiles, isomeric_smiles = get_smiles(cid)
                smiles = canonical_smiles or isomeric_smiles or ""
                row[smiles_column] = smiles
                row[cid_column] = str(cid)
                if smiles:
                    found += 1
                print(f"[{index}/{total}] {drug}: CID={cid}, SMILES={'yes' if smiles else 'no'}.")
        except (HTTPError, URLError, TimeoutError) as exc:
            print(f"[{index}/{total}] {drug}: request failed ({exc}).")
            row[smiles_column] = ""
            row[cid_column] = ""

        if delay > 0:
            time.sleep(delay)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. Found SMILES for {found}/{total} drugs.")
    print(f"Output: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape PubChem and add SMILES values to a CSV of drug names."
    )
    parser.add_argument(
        "input_csv",
        type=Path,
        help="Path to input CSV (must contain a drug column, default: Drug).",
    )
    parser.add_argument(
        "-o",
        "--output-csv",
        type=Path,
        default=None,
        help="Path to output CSV. Defaults to <input>_with_smiles.csv.",
    )
    parser.add_argument(
        "--drug-column",
        default="Drug",
        help="Column that contains drug names (default: Drug).",
    )
    parser.add_argument(
        "--smiles-column",
        default="SMILES",
        help="Column to store SMILES (default: SMILES).",
    )
    parser.add_argument(
        "--cid-column",
        default="PubChem_CID",
        help="Column to store PubChem CID (default: PubChem_CID).",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="Delay between PubChem requests in seconds (default: 0.2).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input_csv.resolve()
    output_path = args.output_csv.resolve() if args.output_csv else derive_output_path(input_path)
    process_csv(
        input_path=input_path,
        output_path=output_path,
        drug_column=args.drug_column,
        smiles_column=args.smiles_column,
        cid_column=args.cid_column,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()
