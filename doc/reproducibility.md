# Reproducibility Guide

This guide describes how to reproduce a local CardioQSPR run from a clean clone.

## 1. Prepare The Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd frontend
npm install
cd ..
```

Recommended versions:

- Python 3.11 or newer
- Node.js 20 or newer
- npm 10 or newer

## 2. Start From A Fresh Local Database

Remove any previous local runtime database:

```bash
rm -f data/drugs.db
```

Start the platform:

```bash
python run.py
```

On first startup, the backend creates:

- `data/drugs.db`
- baseline drug records from `src/app/db/seeds.py`
- local admin user `admin` / `admin123`

## 3. Verify The Clone

In a separate terminal:

```bash
source venv/bin/activate
python -m pytest -q
```

For the frontend:

```bash
cd frontend
npm run build
```

## 4. Manual Smoke Check

With the platform running:

```bash
curl http://localhost:5555/api/health
curl http://localhost:5555/api/drugs
```

The health endpoint should return `{"status":"ok"}`. The drug endpoint should return the seeded baseline library.

## 5. Generate A Reproducible Analysis

1. Open `http://localhost:5173`.
2. Log in with `admin` / `admin123`.
3. Open the molecular database and confirm the baseline compounds are present.
4. Create an analysis from a fixed compound subset.
5. Run the regression engine.
6. Record the generated analysis folder shown in the UI.

Generated outputs are written under:

- `data/qspr_results/<analysis_folder>/`
- `data/plots/<analysis_folder>/`

These generated files are intentionally ignored by Git. They should be regenerated from the code, seed data, and analysis choices.

## 6. Scientific Caveats

CardioQSPR uses a mixture of curated seed data, PubChem retrieval, EPI Suite-style fallbacks, and RDKit estimators. For publication-grade work, manually inspect:

- values marked as calculated or estimated
- vapor pressure values spanning very large orders of magnitude
- flash point values that may reflect unit or decomposition ambiguities
- outliers that strongly influence linear regressions

The project is intended for academic exploration and reproducible computational experiments, not regulatory or clinical decision-making.

## 7. Reference Article

Primary reference:

- Rasheed, M. W., Mahboob, A., & Hanif, I. (2023). An estimation of physicochemical properties of heart attack treatment medicines by using molecular descriptor's. South African Journal of Chemical Engineering, 45, 20-29. https://doi.org/10.1016/j.sajce.2023.04.003

Local PDF:

```text
data/raw/reference/1-s2.0-S1026918523000276-main.pdf
```
