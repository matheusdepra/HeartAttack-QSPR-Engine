# Business logic for Drug management, Pubchem sync, and properties estimations
import logging
from typing import List, Optional, Dict, Any
from app.repositories.drug import DrugRepository
from app.models.drug import Drug
from app.core.exceptions import AppError

logger = logging.getLogger(__name__)

class DrugService:
    def __init__(self, drug_repo: DrugRepository):
        self.drug_repo = drug_repo

    def get_drug(self, id: int) -> Drug:
        drug = self.drug_repo.get_by_id(id)
        if not drug:
            raise AppError("Drug not found", 404)
        return drug

    def list_drugs(self) -> List[Drug]:
        return self.drug_repo.list_all()

    def sync_drug(self, name: str, smiles: Optional[str] = None) -> Drug:
        # Check if the drug already exists in the database
        existing = self.drug_repo.get_by_name(name)
        if existing:
            return existing

        data = {}
        # Local fallback for baseline research drugs
        try:
            from app.db.seeds import BASELINE_DRUGS
            baseline_match = next((d for d in BASELINE_DRUGS if d["name"].lower() == name.lower()), None)
        except ImportError:
            baseline_match = None
        
        if baseline_match:
            data = baseline_match.copy()
            if smiles:
                data["smiles"] = smiles
        else:
            try:
                from app.scrapers.pubchem import process_drug_pubchem
                data = process_drug_pubchem(name)
            except Exception as e:
                logger.warning(f"PubChem scraper failed for name '{name}': {e}")
                pass
            
        final_smiles = smiles or data.get("smiles")
        if smiles:
            data["smiles"] = smiles
            
        if final_smiles:
            # Estimate missing properties from SMILES
            from app.scrapers.pubchem import calculate_theoretical_bp, fetch_epi_suite_data
            try:
                from rdkit import Chem
                from rdkit.Chem import Descriptors, Crippen
                from rdkit.Chem.GraphDescriptors import BertzCT
                
                mol = Chem.MolFromSmiles(final_smiles)
                if mol:
                    if data.get("mw") is None:
                        data["mw"] = round(Descriptors.MolWt(mol), 2)
                        data["mw_source"] = "Calculated (RDKit)"
                    if data.get("complexity") is None:
                        data["complexity"] = round(BertzCT(mol), 2)
                        data["complexity_source"] = "Calculated (RDKit BertzCT Proxy)"
                    if data.get("bp") is None:
                        calc_bp = calculate_theoretical_bp(final_smiles)
                        if calc_bp:
                            data["bp"] = calc_bp
                            data["bp_source"] = "Calculated (RDKit Estimator)"
                    if data.get("vp") is None:
                        epi = fetch_epi_suite_data(final_smiles)
                        if epi.get("vp"):
                            data["vp"] = epi["vp"]
                            data["vp_source"] = "Calculated (EPI Suite)"
                    if data.get("ev") is None and data.get("bp") is not None:
                        bp_k = data["bp"] + 273.15
                        data["ev"] = round(88 * bp_k / 1000, 2)
                        data["ev_source"] = "Calculated (RDKit/Trouton Estimate)"
                    if data.get("fp") is None and data.get("bp") is not None:
                        data["fp"] = round(0.683 * data["bp"] - 73, 2)
                        data["fp_source"] = "Calculated (Sinnott Rule)"
                    if data.get("mr") is None:
                        data["mr"] = round(Crippen.MolMR(mol), 2)
                        data["mr_source"] = "Calculated (RDKit Estimator)"
                    if data.get("st") is None and data.get("mr") is not None:
                        data["st"] = round(0.05 * data["mr"] * 10, 2)
                        data["st_source"] = "Calculated (Macleod-Sugden Proxy)"
                    if data.get("mv") is None:
                        data["mv"] = round(Descriptors.MolWt(mol) / 1.0, 2)
                        data["mv_source"] = "Calculated (MW/density=1 Approximation)"
            except Exception as e:
                logger.warning(f"RDKit estimations failed during sync of '{name}': {e}")
                    
        ti = None
        if final_smiles:
            try:
                from app.calculators.topological import calculate_for_drug
                ti = calculate_for_drug(name, final_smiles)
            except Exception as e:
                logger.warning(f"Failed to calculate topological indices for '{name}': {e}")

        drug = Drug(
            name=name,
            **{k: v for k, v in data.items() if k not in ["name"]},
            ti_abc=ti["ABC"] if ti else None,
            ti_ga=ti["GA"] if ti else None,
            ti_ri=ti["RI"] if ti else None,
            ti_rr=ti["RR"] if ti else None,
            ti_h=ti["H"] if ti else None,
            ti_sci=ti["SCI"] if ti else None,
            ti_m1=ti["M1"] if ti else None,
            ti_m2=ti["M2"] if ti else None,
            ti_hm=ti["HM"] if ti else None,
            ti_rm2=ti["RM2"] if ti else None,
            ti_f=ti["F"] if ti else None,
            ti_hf=ti["HF"] if ti else None,
        )
        return self.drug_repo.create(drug)

    def update_drug(self, id: int, data: Dict[str, Any]) -> Drug:
        drug = self.get_drug(id)
        
        old_smiles = drug.smiles
        new_smiles = data.get("smiles")
        
        for key, value in data.items():
            if hasattr(drug, key):
                setattr(drug, key, value)
                
        if new_smiles and new_smiles != old_smiles:
            try:
                from app.calculators.topological import calculate_for_drug
                ti = calculate_for_drug(drug.name, new_smiles)
                if ti:
                    drug.ti_abc = ti.get("ABC")
                    drug.ti_ga = ti.get("GA")
                    drug.ti_ri = ti.get("RI")
                    drug.ti_rr = ti.get("RR")
                    drug.ti_h = ti.get("H")
                    drug.ti_sci = ti.get("SCI")
                    drug.ti_m1 = ti.get("M1")
                    drug.ti_m2 = ti.get("M2")
                    drug.ti_hm = ti.get("HM")
                    drug.ti_rm2 = ti.get("RM2")
                    drug.ti_f = ti.get("F")
                    drug.ti_hf = ti.get("HF")
            except Exception as e:
                logger.error(f"Failed to recalculate indices for drug '{drug.name}': {e}")
                
        return self.drug_repo.save(drug)

    def resync_drug(self, id: int) -> Drug:
        drug = self.get_drug(id)
        
        try:
            from app.scrapers.pubchem import process_drug_pubchem
            data = process_drug_pubchem(drug.name)
            
            # If name search failed but we have a SMILES, try finding properties by SMILES
            if (not data.get("pubchem_cid")) and drug.smiles:
                from app.scrapers.pubchem import get_cid_by_smiles, _get_json, PUBCHEM_VIEW, find_property_in_view
                cid = get_cid_by_smiles(drug.smiles)
                if cid:
                    data["pubchem_cid"] = cid
                    view_url = f"{PUBCHEM_VIEW}/data/compound/{cid}/JSON"
                    view_data = _get_json(view_url, delay=0.5)
                    bp, bp_src = find_property_in_view(view_data, ["Boiling Point"])
                    vp, vp_src = find_property_in_view(view_data, ["Vapor Pressure"])
                    data.update({"bp": bp, "bp_source": bp_src, "vp": vp, "vp_source": vp_src})

            # Priority logic for SMILES: Existing > PubChem
            final_smiles = drug.smiles or data.get("smiles")
            
            # Update chemical properties
            for key, value in data.items():
                if value is not None:
                    if key == "smiles" and drug.smiles:
                        continue
                    setattr(drug, key, value)
                
            if final_smiles:
                from app.calculators.topological import calculate_for_drug
                ti = calculate_for_drug(drug.name, final_smiles)
                if ti:
                    drug.ti_abc = ti.get("ABC")
                    drug.ti_ga = ti.get("GA")
                    drug.ti_ri = ti.get("RI")
                    drug.ti_rr = ti.get("RR")
                    drug.ti_h = ti.get("H")
                    drug.ti_sci = ti.get("SCI")
                    drug.ti_m1 = ti.get("M1")
                    drug.ti_m2 = ti.get("M2")
                    drug.ti_hm = ti.get("HM")
                    drug.ti_rm2 = ti.get("RM2")
                    drug.ti_f = ti.get("F")
                    drug.ti_hf = ti.get("HF")
            
            return self.drug_repo.save(drug)
        except Exception as e:
            logger.error(f"Error resyncing drug '{drug.name}': {e}", exc_info=True)
            raise AppError(f"Error resyncing drug: {str(e)}", 500)
