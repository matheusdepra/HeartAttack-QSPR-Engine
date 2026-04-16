import urllib.request
import urllib.parse
import json
import logging
import time
from typing import Optional, Dict, Tuple, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PUBCHEM_REST = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
PUBCHEM_VIEW = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view"

def _get_json(url: str, delay: float = 0.2) -> dict:
    time.sleep(delay)  # polite rate limiting
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 Python PubChemScraper'})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {}
        logger.error(f"HTTP Error {e.code} for URL: {url}")
        return {}
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return {}

def get_cid(drug_name: str) -> Optional[str]:
    """Fetch CID for a given drug name"""
    encoded = urllib.parse.quote(drug_name.strip())
    url = f"{PUBCHEM_REST}/compound/name/{encoded}/cids/JSON"
    data = _get_json(url)
    cids = data.get("IdentifierList", {}).get("CID", [])
    if cids:
        return str(cids[0])
    return None

def _get_smiles_from_record(cid: str) -> Optional[str]:
    url = f"{PUBCHEM_REST}/compound/cid/{cid}/record/JSON"
    data = _get_json(url)
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
    return canonical or isomeric

def get_smiles(cid: str) -> Optional[str]:
    """Fetch Canonical or Isomeric SMILES for CID"""
    url = f"{PUBCHEM_REST}/compound/cid/{cid}/property/CanonicalSMILES,IsomericSMILES/JSON"
    data = _get_json(url)
    props = data.get("PropertyTable", {}).get("Properties", [])
    if props:
        row = props[0]
        smiles = row.get("CanonicalSMILES") or row.get("IsomericSMILES")
        if smiles:
            return smiles
            
    # Fallback to record endpoint if property endpoint fails or returns nothing
    return _get_smiles_from_record(cid)

def find_property_in_view(data: Any, target_headings: list[str], parent_context: str = "") -> Tuple[Optional[float], Optional[str]]:
    """
    Recursively search the PUG VIEW JSON for target headings (e.g., ['Boiling Point'])
    Returns (value (float), source (str)) -> source is either 'Experimental' or 'Computed'
    """
    found_values = []
    
    def _search(node, context):
        if isinstance(node, dict):
            heading = node.get("TOCHeading", "")
            current_context = context
            if heading in ["Experimental Properties", "Computed Properties"]:
                current_context = "Experimental" if "Experimental" in heading else "Computed"
                
            if heading in target_headings:
                infos = node.get("Information", [])
                for info in infos:
                    val = None
                    if "Value" in info and "Number" in info["Value"]:
                        val = info["Value"]["Number"][0]
                    elif "Value" in info and "StringWithMarkup" in info["Value"]:
                        try:
                            # Extract numbers from string like "770.5 deg C"
                            s = info["Value"]["StringWithMarkup"][0]["String"]
                            nums = [float(s) for s in s.split() if s.replace('.','',1).replace('-','',1).isdigit()]
                            if nums:
                                val = nums[0]
                        except Exception:
                            pass
                    
                    if val is not None:
                        found_values.append((val, current_context or "General"))
                        
            for k, v in node.items():
                _search(v, current_context)
        elif isinstance(node, list):
            for item in node:
                _search(item, context)

    _search(data, parent_context)
    
    if not found_values:
        return None, None
        
    # Prefer Experimental over Computed
    experimental = [v for v in found_values if v[1] == "Experimental"]
    if experimental:
        return experimental[0][0], "Experimental"
        
    computed = [v for v in found_values if v[1] == "Computed"]
    if computed:
        return computed[0][0], "Computed"
        
    return found_values[0][0], found_values[0][1]

def calculate_theoretical_bp(smiles: str) -> Optional[float]:
    """
    Dummy QSPR model to estimate Boiling Point (Celsius) from SMILES using RDKit structural descriptors.
    This acts as a fallback when experimental data in PubChem is missing for complex APIs.
    """
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            return None
            
        mw = Descriptors.MolWt(mol)
        tpsa = Descriptors.TPSA(mol)
        hba = Descriptors.NumHAcceptors(mol)
        hbd = Descriptors.NumHDonors(mol)
        
        # Simplified empirical estimation (result in Kelvin, converted to Celsius)
        bp_kelvin = 250 + (mw * 0.8) + (tpsa * 0.5) + (hba * 10) + (hbd * 20)
        return round(bp_kelvin - 273.15, 2)
    except ImportError:
        logger.warning("RDKit not installed. Cannot calculate theoretical BP.")
        return None
    except Exception as e:
        logger.error(f"Error calculating theoretical BP: {e}")
        return None

def fetch_epi_suite_data(smiles: str) -> dict:
    """
    Fetch calculated properties from EPA's EPI Suite via episuite.dev.
    Returns a dict with keys: bp, vp, ev, fp, st, mv (all in base SI/Celsius units).
    """
    url = f"https://episuite.dev/api/submit?smiles={urllib.parse.quote(smiles)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 Python PubChemScraper'})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode())

            def _sel(key):
                return data.get(key, {}).get('selectedValue', {}).get('value')

            result = {
                'bp': _sel('boilingPoint'),                           # Celsius
                'vp': _sel('vaporPressure'),                          # mmHg
                # EPI Suite does not compute EV/ST/MV directly;
                # use Henry's Law as a proxy for EV when missing
                'ev': None,
                'fp': None,
                'st': None,
                'mv': None,
            }
            logger.info(f"EPI Suite returned: bp={result['bp']}, vp={result['vp']}")
            return result
    except Exception as e:
        logger.warning(f"Failed to fetch EPI Suite data: {e}")
        return {}

def process_drug_pubchem(drug_name: str) -> Dict[str, Any]:
    """
    Given a drug name, fetch all required data from PubChem.
    Returns dictionary with properties.
    """
    logger.info(f"Processing PubChem for {drug_name}")
    cid = get_cid(drug_name)
    if not cid:
        logger.warning(f"Could not find CID for {drug_name}")
        return {"pubchem_cid": None, "smiles": None}
        
    smiles = get_smiles(cid)
    
    # Fetch PUG VIEW JSON
    view_url = f"{PUBCHEM_VIEW}/data/compound/{cid}/JSON"
    view_data = _get_json(view_url, delay=0.5)
    
    epi_data = {}
    
    # Extract properties
    bp, bp_src = find_property_in_view(view_data, ["Boiling Point"])
    if bp is None and smiles:
        if not epi_data: epi_data = fetch_epi_suite_data(smiles)
        if epi_data.get('bp') is not None:
            bp = epi_data['bp']
            bp_src = "Calculated (EPI Suite)"
        else:
            calc_bp = calculate_theoretical_bp(smiles)
            if calc_bp is not None:
                bp = calc_bp
                bp_src = "Calculated (RDKit Estimator)"
            
    vp, vp_src = find_property_in_view(view_data, ["Vapor Pressure"])
    if vp is None and smiles:
        if not epi_data: epi_data = fetch_epi_suite_data(smiles)
        if epi_data.get('vp') is not None:
            vp = epi_data['vp']
            vp_src = "Calculated (EPI Suite)"
            
    ev, ev_src = find_property_in_view(view_data, ["Enthalpy of Vaporization", "Heat of Vaporization"])
    # EPI Suite doesn't provide EV directly — RDKit fallback only
    if ev is None and smiles:
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                # Enthalpy of vaporization rough estimate (kJ/mol) via Trouton's rule: dHvap ~ 88 * Tb(K)
                bp_k = (bp + 273.15) if bp is not None else None
                if bp_k:
                    ev = round(88 * bp_k / 1000, 2)   # convert J/mol -> kJ/mol
                    ev_src = "Calculated (RDKit/Trouton Estimate)"
        except Exception:
            pass

    fp, fp_src = find_property_in_view(view_data, ["Flash Point"])
    # Flash point estimated via Sinnott rule: FP(C) ≈ 0.683 * BP(C) - 73  (valid for organic liquids)
    if fp is None and bp is not None:
        fp = round(0.683 * bp - 73, 2)
        fp_src = "Calculated (Sinnott Rule)"

    mr, mr_src = find_property_in_view(view_data, ["Refractivity", "Molar Refractivity"])
    if mr is None and smiles:
        try:
            from rdkit import Chem
            from rdkit.Chem import Crippen
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                mr = round(Crippen.MolMR(mol), 2)
                mr_src = "Calculated (RDKit Estimator)"
        except Exception:
            pass

    st, st_src = find_property_in_view(view_data, ["Surface Tension"])
    # Surface tension estimate (mN/m) via Macleod-Sugden correlation proxy: ST ~ 0.05 * MR
    if st is None and mr is not None:
        st = round(0.05 * mr * 10, 2)   # rough proxy
        st_src = "Calculated (Macleod-Sugden Proxy)"

    mv, mv_src = find_property_in_view(view_data, ["Molar Volume", "Volume"])
    # Molar volume estimate (cm3/mol): MV = MW / density; density ~ 1.0 g/cm3 approximation
    if mv is None and smiles:
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors
            mol = Chem.MolFromSmiles(smiles)
            if mol:
                mw = Descriptors.MolWt(mol)
                mv = round(mw / 1.0, 2)   # assumes density ~ 1 g/cm3
                mv_src = "Calculated (MW/density=1 Approximation)"
        except Exception:
            pass
    
    return {
        "pubchem_cid": cid,
        "smiles": smiles,
        "bp": bp, "bp_source": bp_src,
        "vp": vp, "vp_source": vp_src,
        "ev": ev, "ev_source": ev_src,
        "fp": fp, "fp_source": fp_src,
        "mr": mr, "mr_source": mr_src,
        "st": st, "st_source": st_src,
        "mv": mv, "mv_source": mv_src,
    }
