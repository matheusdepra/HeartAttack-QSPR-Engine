# CardioQSPR: Heart Attack Medication Analytics Pipeline

**CardioQSPR** is a robust, modular Python pipeline designed to analyze heart attack medications (Myocardial Infarction) through Quantitative Structure-Property Relationship (QSPR) modeling and Chemical Graph Theory.

Following the methodology of Rasheed et al. (2023), this project automates data acquisition, structural descriptor calculation, statistical regression, and high-fidelity visualization.

## 🚀 Key Features

- **Automated Data Acquisition**: 
    - Intelligent scraping from **PubChem** (PUG REST/VIEW).
    - Graceful fallback to **EPA's EPI Suite API** for calculated properties when experimental data is missing.
- **Topological Indices Engine**: 
    - Calculates 10 degree-based descriptors: Randic (RI, RR), Zagreb (M1, M2, HM, RM2), Harmonic (H), Sum Connectivity (SCI), and Forgotten (F, HF).
- **Agnostic QSPR Analysis**: 
    - Pairwise linear regression between all TIs and 7 physicochemical properties (BP, VP, EV, FP, MR, ST, MV).
    - Statistical metrics ($r$, $R^2$, Adj-$R^2$, RMSE, MAE, p-value, F-statistic).
- **Premium Visualizations**:
    - High-DPI molecular structure grids using RDKit.
    - Correlation trend subplots and global comparative line charts (Figure 2 & 3 style).
- **Methodology Validation**:
    - Includes a benchmark against Rasheed's 2023 publication, showing superior correlation coefficients ($r$) in structural properties (MR, MV, ST).

## 📂 Project Structure

```text
├── src/
│   ├── scrapers/      # PubChem & EPI Suite data acquisition
│   ├── db/            # SQLAlchemy models and SQLite setup
│   ├── calculators/   # Topological indices and QSPR logic
│   ├── visualizers/   # Matplotlib/Seaborn/RDKit plotting
│   ├── main.py        # Primary acquisition pipeline
│   └── generate_qspr_report.py  # Statistical & Graphical analysis
├── data/
│   ├── raw/           # Input drug lists (.txt)
│   ├── plots/         # Generated PNG figures
│   ├── qspr_results/  # CSVs and Markdown reports
│   └── drugs.db       # SQLite database (Git Ignored)
├── doc/               # Future improvements and comparison docs
├── tests/             # Development scripts and unit tests
└── requirements.txt   # Project dependencies
```

## 🛠️ Installation

1. **Setup Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Browser Engine** (Optional, for condition-based scraping):
   ```bash
   playwright install chromium
   ```

## 📊 Usage

### 1. Data Acquisition
Populate the database with drug properties and topological indices:
```bash
python src/main.py
```

### 2. Analysis & Report Generation
Run the QSPR analysis and generate plots/reports:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python src/generate_qspr_report.py
```

Results will be saved in `data/qspr_results/` and `data/plots/`.

## 🔬 Scientific Validation
CardioQSPR results were compared against the study *"An estimation of physicochemical properties of heart attack treatment medicines by using molecular descriptor’s"* (South African Journal of Chemical Engineering, 2023).

Our methodology achieved **significantly higher correlation coefficients** for structural properties:
- **Surface Tension**: $r = 0.98$ (ours) vs $r = 0.42$ (paper)
- **Molar Refractivity**: $r = 0.98$ (ours) vs $r = 0.80$ (paper)

## ⚖️ License
This project is open-source and intended for academic and research purposes.
