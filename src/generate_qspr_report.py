import sys
import os
import logging
from db.models import get_engine, get_session
from calculators.qspr import build_report

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting QSPR report generation...")
    
    # Get database session
    engine = get_engine()
    session = get_session(engine)
    
    try:
        # Generate the report
        output_dir = "data/qspr_results"
        paths = build_report(session, output_dir=output_dir)
        
        # 1. Visualization: Generate Molecular Grid
        from db.models import Drug
        import pandas as pd
        drugs = session.query(Drug).all()
        drugs_df = pd.DataFrame([{
            'name': d.name, 
            'smiles': d.smiles
        } for d in drugs])
        
        plot_dir = "data/plots"
        os.makedirs(plot_dir, exist_ok=True)
        
        from visualizers.report_plots import generate_structure_grid, generate_correlation_figures
        generate_structure_grid(drugs_df, os.path.join(plot_dir, "molecule_structures.png"))
        
        # 2. Visualization: Correlation Plots
        all_models_df = pd.read_csv(paths['all_models'])
        generate_correlation_figures(all_models_df, plot_dir)
        
        logger.info(f"QSPR analysis and visualization completed successfully.")
        logger.info(f"Report location: {paths['report']}")
        logger.info(f"Plots location: {plot_dir}")
        
        # Display the report location
        print(f"\nReport generated: {paths['report']}")
        print(f"Figures generated in: {plot_dir}")
        
    except Exception as e:
        logger.error(f"Error generating QSPR report: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()
