# Business logic for Analysis lifecycle, QSPR regression, and plot generations
import os
import re
import logging
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from app.repositories.analysis import AnalysisRepository
from app.repositories.drug import DrugRepository
from app.models.analysis import Analysis, AnalysisItem, AnalysisStats
from app.core.exceptions import AppError
from app.core.config import settings

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self, analysis_repo: AnalysisRepository, drug_repo: DrugRepository):
        self.analysis_repo = analysis_repo
        self.drug_repo = drug_repo

    def get_analysis_folder_name(self, analysis: Analysis) -> str:
        sanitized = re.sub(r'[^a-zA-Z0-9_\-]', '_', analysis.name)
        sanitized = sanitized.strip('_').lower()
        if not sanitized:
            sanitized = "analysis"
        return f"{sanitized}_{analysis.id}"

    def get_analysis(self, id: int) -> Analysis:
        analysis = self.analysis_repo.get_by_id(id)
        if not analysis:
            raise AppError("Analysis not found", 404)
        return analysis

    def list_analyses(self, user_id: Optional[int] = None) -> List[Analysis]:
        return self.analysis_repo.list_all(user_id)

    def create_analysis(self, name: str, drug_ids: List[int], description: Optional[str] = None, user_id: Optional[int] = None) -> Analysis:
        analysis = Analysis(name=name, description=description, user_id=user_id, status="draft")
        self.analysis_repo.create(analysis)
        
        # Create snapshots for each drug
        for d_id in drug_ids:
            drug = self.drug_repo.get_by_id(d_id)
            if drug:
                item = AnalysisItem(
                    analysis_id=analysis.id,
                    drug_id=drug.id,
                    bp=drug.bp,
                    vp=drug.vp,
                    ev=drug.ev,
                    fp=drug.fp,
                    mr=drug.mr,
                    st=drug.st,
                    mv=drug.mv,
                    mw=drug.mw,
                    complexity=drug.complexity
                )
                self.analysis_repo.create_item(item)
                
        # Reload analysis with items
        return self.get_analysis(analysis.id)

    def update_analysis_item(self, id: int, item_id: int, data: Dict[str, Any]) -> AnalysisItem:
        item = self.analysis_repo.get_item(item_id, id)
        if not item:
            raise AppError("Analysis item not found", 404)
        
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, float(value) if value is not None else None)
        
        self.analysis_repo.db.commit()
        return item

    def run_analysis(self, id: int) -> Dict[str, Any]:
        analysis = self.get_analysis(id)
        folder_name = self.get_analysis_folder_name(analysis)
        
        try:
            from app.calculators.qspr import build_report
            from app.visualizers.report_plots import generate_structure_grid, generate_correlation_figures
            
            # 1. Run QSPR
            output_dir = str(settings.QSPR_RESULTS_DIR / folder_name)
            paths = build_report(self.analysis_repo.db, output_dir=output_dir, analysis_id=id)
            
            # 2. Save Stats to DB
            all_models_df = pd.read_csv(paths['all_models'])
            
            # Clear old stats
            self.analysis_repo.delete_stats(id)
            
            for _, row in all_models_df.iterrows():
                n_val = int(row.get('n', 0)) if pd.notnull(row.get('n')) else None
                adj_r2_val = float(row.get('adjusted_R2', np.nan)) if 'adjusted_R2' in row and pd.notnull(row['adjusted_R2']) else None
                
                r2_val = float(row['R2'])
                f_stat = None
                if n_val and n_val > 2 and r2_val < 1.0:
                    f_stat = (r2_val / (1.0 - r2_val)) * (n_val - 2)

                stat = AnalysisStats(
                    analysis_id=id,
                    property_name=row['property'],
                    index_name=row['index'],
                    r=row['r'],
                    r2=r2_val,
                    slope=row['slope'],
                    intercept=row['intercept'],
                    p_value=row['p_value'] if pd.notnull(row['p_value']) else None,
                    rmse=row['RMSE'] if pd.notnull(row['RMSE']) else None,
                    adj_r2=adj_r2_val,
                    n=n_val,
                    f_statistic=f_stat
                )
                self.analysis_repo.create_stat(stat)
            
            # 3. Generate Plots
            plot_dir = str(settings.PLOTS_DIR / folder_name)
            os.makedirs(plot_dir, exist_ok=True)
            
            drug_data = []
            for item in analysis.items:
                drug_data.append({'name': item.drug.name, 'smiles': item.drug.smiles})
            
            generate_structure_grid(pd.DataFrame(drug_data), os.path.join(plot_dir, "molecule_structures.png"))
            generate_correlation_figures(all_models_df, plot_dir)
            
            analysis.status = "completed"
            self.analysis_repo.save(analysis)
            
            return {"status": "completed", "report": str(paths['report'])}
        except Exception as e:
            self.analysis_repo.db.rollback()
            logger.error(f"Error running QSPR regression for analysis '{analysis.name}': {e}", exc_info=True)
            raise AppError(f"Error running QSPR engine: {str(e)}", 500)

    def get_analysis_report(self, id: int) -> str:
        analysis = self.get_analysis(id)
        folder_name = self.get_analysis_folder_name(analysis)
        report_path = settings.QSPR_RESULTS_DIR / folder_name / "qspr_report.md"
        if not report_path.exists():
            raise AppError("Report not generated yet", 404)
        return report_path.read_text(encoding="utf-8")

    def delete_analysis(self, id: int) -> None:
        analysis = self.get_analysis(id)
        folder_name = self.get_analysis_folder_name(analysis)
        
        # 1. Clean up generated directories on disk
        import shutil
        qspr_dir = settings.QSPR_RESULTS_DIR / folder_name
        plots_dir = settings.PLOTS_DIR / folder_name
        
        try:
            if qspr_dir.exists():
                shutil.rmtree(qspr_dir)
        except Exception as e:
            logger.error(f"Error removing QSPR directory for analysis {id}: {e}")
            
        try:
            if plots_dir.exists():
                shutil.rmtree(plots_dir)
        except Exception as e:
            logger.error(f"Error removing plots directory for analysis {id}: {e}")
            
        # 2. Delete database record (items and stats will cascade delete)
        self.analysis_repo.delete(analysis)
