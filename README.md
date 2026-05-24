# CardioQSPR

CardioQSPR is a full-stack QSPR platform for cardiovascular and heart attack drug analysis. It combines chemical graph theory, topological index calculation, web data acquisition, linear regression, report generation, and an interactive web UI for building and reviewing analyses.

## At A Glance

The platform is designed for workflows where a researcher wants to:

- ingest cardiovascular compounds into a curated local dataset
- fetch or estimate physicochemical properties
- calculate degree-based topological indices from SMILES
- build QSPR regressions between indices and properties
- review, override, and validate the analysis dataset before execution
- generate article-style statistical tables, plots, and Markdown reports

## Quick Start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd frontend
npm install
cd ..

python run.py
```

Then open:

- Frontend UI: `http://localhost:5173`
- Backend API docs: `http://localhost:5555/docs`

## Contents

- [What The Tool Does](#what-the-tool-does)
- [Scientific And Computational Basis](#scientific-and-computational-basis)
- [Topological Indices Used](#topological-indices-used)
- [Physicochemical Properties Used](#physicochemical-properties-used)
- [Fallback Estimation Logic](#fallback-estimation-logic)
- [Web Scraping And External Data Acquisition](#web-scraping-and-external-data-acquisition)
- [User Workflows](#user-workflows)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Installation](#installation)
- [Local Development And Deployment](#local-development-and-deployment)
- [Linux Service Deployment](#linux-service-deployment)
- [Data Persistence Model](#data-persistence-model)
- [Outputs Generated](#outputs-generated)
- [Web Scraping Caveats](#web-scraping-caveats)

## What The Tool Does

CardioQSPR is organized around four major capabilities.

### 1. Drug Library Management

The platform maintains a local SQLite database of compounds with:

- compound identity
- SMILES representation
- physicochemical properties
- source metadata for each property
- topological indices derived from the molecule graph

Users can:

- add compounds manually
- import a baseline cardiovascular dataset
- refresh compounds from PubChem
- edit the master record directly in the UI

### 2. Ingestion And Data Enrichment

When a drug is added or re-synced, CardioQSPR attempts to build the best possible record from a hierarchy of sources and estimators:

- baseline seeded dataset, when available
- PubChem PUG REST / PUG View data
- EPI Suite-compatible remote fallback for selected missing values
- RDKit-derived estimations when external experimental values are unavailable

The goal is to avoid sparse datasets that would make regression comparisons unusable.

### 3. QSPR Analysis Workspace

The Analysis Workspace lets the user:

- select a subset of compounds from the library
- create a snapshot analysis dataset
- override values for the selected run without changing the master record
- inspect missing values before execution
- execute the regression engine
- review the resulting report, statistics, and generated plots

This snapshot model is important: the analysis uses copied values from the library at the time of analysis creation, so later edits to the master record do not retroactively alter older analyses.

### 4. Reporting And Visualization

After execution, the platform produces:

- a Markdown report
- article-style statistical tables by topological index
- “best model per property” summaries
- prediction and residual tables
- molecular structure grids
- correlation plots by property
- global correlation comparison charts

The frontend exposes these outputs through the Analysis Viewer.

## Scientific And Computational Basis

CardioQSPR models each molecule as a graph:

- atoms are vertices
- bonds are edges
- vertex degree is the number of bonded neighbors for an atom

From this graph representation, the platform calculates degree-based topological indices and relates them to physicochemical properties using simple linear regression.

### Core QSPR Model

For each pair:

- one property `P`
- one topological index `TI`

the platform fits:

```text
P = a + b · TI
```

Where:

- `a` is the intercept
- `b` is the slope
- `TI` is the selected topological index

Each property is regressed independently against each available index.

### Statistical Outputs

For each fitted model, CardioQSPR computes:

- `r`: Pearson correlation coefficient
- `R²`: coefficient of determination
- `Adjusted R²`: variance explained corrected for sample size
- `p-value`: significance of the linear relationship
- `F-statistic`: overall model significance against a null model
- `RMSE`: root mean square error
- `MAE`: mean absolute error
- `MAPE`: mean absolute percentage error, when the target is non-zero

The platform then classifies model quality:

- `excellent` when `R² >= 0.90` and `p < 0.05`
- `good` when `R² >= 0.75` and `p < 0.05`
- `moderate` when `R² >= 0.50`
- `weak` otherwise

## Topological Indices Used

The backend computes 12 degree-based indices from SMILES using RDKit-generated molecular graphs.

### Connectivity Family

- `ABC`: Atom-Bond Connectivity Index
- `GA`: Geometric-Arithmetic Index
- `RI`: Randić Index
- `RR`: Reciprocal Randić Index
- `SCI`: Sum Connectivity Index
- `H`: Harmonic Index

These indices primarily describe branching, degree balance, and connectivity patterns across the molecular graph.

### Zagreb Family

- `M1`: First Zagreb Index
- `M2`: Second Zagreb Index
- `HM`: Hyper Zagreb Index
- `RM2`: Redefined Second Zagreb Index

These emphasize degree sums and products and are often used as coarse structural complexity descriptors.

### Forgotten Family

- `F`: Forgotten Index
- `HF`: Hyper Forgotten Index

These are more sensitive to degree magnitude and often correlate strongly with size- and complexity-driven properties.

## Physicochemical Properties Used

The current platform works with 9 target properties.

| Symbol | Property | Meaning |
|---|---|---|
| `BP` | Boiling Point | Temperature at which the compound transitions from liquid to vapor |
| `VP` | Vapor Pressure | Tendency of the compound to evaporate |
| `EV` | Enthalpy / Heat of Vaporization | Energy required to convert liquid into gas |
| `FP` | Flash Point | Lowest temperature at which vapors can ignite |
| `MR` | Molar Refractivity | Polarizability-related structural descriptor |
| `ST` | Surface Tension | Cohesive force at the liquid surface |
| `MV` | Molar Volume | Volume occupied per mole |
| `MW` | Molecular Weight | Sum of atomic masses |
| `Complexity` | Molecular Complexity | Graph-complexity proxy for branching and structure |

## Fallback Estimation Logic

If a property is unavailable from PubChem, CardioQSPR can estimate it using pragmatic fallbacks.

### Direct RDKit / Structural Estimators

- `MW`: RDKit molecular weight
- `MR`: RDKit Crippen molar refractivity
- `Complexity`: RDKit BertzCT as a complexity proxy
- topological indices: derived directly from the graph defined by SMILES

### Derived Or Empirical Fallbacks

- `BP`: theoretical boiling point estimator using RDKit descriptors
- `EV`: Trouton-style approximation from boiling point
- `FP`: Sinnott-style approximation from boiling point
- `ST`: Macleod-Sugden-like proxy from molar refractivity
- `MV`: molecular weight divided by density proxy, assuming density near `1 g/cm³`

These fallbacks are not a substitute for validated experimental chemistry data. They exist to keep the workflow operable when public sources are incomplete.

## Web Scraping And External Data Acquisition

CardioQSPR is not a generic crawler. It uses targeted structured data retrieval.

### Primary Sources

- `PubChem PUG REST`
- `PubChem PUG View`

These are used to retrieve:

- CIDs from drug names or SMILES
- SMILES strings
- structured physicochemical property sections
- source preference between experimental and computed values

### Secondary Fallback Source

- `episuite.dev` as a remote EPI Suite-style API fallback

This is used mainly for:

- boiling point fallback
- vapor pressure fallback

### Scraping Rules In Practice

The implementation includes:

- explicit request throttling via short delays
- a user-agent header
- preference for experimental values over computed values when both exist
- recovery logic when PubChem lookup by name fails but the compound already has a valid SMILES

### Important Operational Notes

- internet access is required for PubChem and EPI Suite fallbacks
- if external services are down or rate-limited, the platform may fall back to RDKit-based estimates
- analyses remain executable even when some values must be estimated manually or by proxy

## User Workflows

### Typical Research Flow

1. Ingest or sync compounds into the library.
2. Verify or edit physicochemical properties.
3. Use the Analysis Workspace to create a snapshot dataset.
4. Override missing or suspicious values in the snapshot.
5. Run the regression engine.
6. Review the report, statistics, and correlation plots.

### Library Workflow

Use the `Database & Library` section to:

- browse stored compounds
- add a new compound by name and optional SMILES
- load the seeded cardiovascular baseline dataset
- edit physicochemical properties manually
- re-sync a compound from PubChem

### In-Silico Predictor Workflow

Use `In-Silico Predictor` when you already have a valid SMILES string and want only the topological indices.

Input:

- one SMILES string

Output:

- all supported topological indices

This does not create a full analysis by itself. It is a descriptor calculator.

### Analysis Workspace Workflow

1. Select multiple compounds from the library.
2. Create a named analysis snapshot.
3. Review the copied dataset in the `Data Override` step.
4. Fix missing values or override suspicious values.
5. Run the regression engine.
6. Inspect the report, statistics, and correlation plots.

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pandas
- NumPy
- SciPy
- RDKit
- Matplotlib
- Seaborn
- Uvicorn

### Frontend

- React 19
- Vite
- React Markdown
- remark-gfm

### Data / Scientific Stack

- RDKit for molecular graph handling and descriptor calculation
- SciPy `linregress` for pairwise linear regression
- Pandas for tabular transformations and report table generation

### Deployment / Runtime

- local Python virtual environment
- Node.js + npm for frontend dev server and build
- optional `systemd` service installation via `setup_service.sh`

## Project Structure

```text
.
├── frontend/                 # React + Vite UI
├── src/
│   ├── api.py                # Backward-compatible FastAPI entrypoint
│   ├── app/
│   │   ├── api/              # FastAPI routes
│   │   ├── calculators/      # Topological indices and QSPR engine
│   │   ├── core/             # Config, DB, exceptions
│   │   ├── db/               # Seeds
│   │   ├── models/           # SQLAlchemy models
│   │   ├── repositories/     # Data access layer
│   │   ├── scrapers/         # PubChem and fallback acquisition
│   │   ├── services/         # Business logic
│   │   └── visualizers/      # Plot generation
│   ├── main.py               # Legacy acquisition pipeline
│   └── generate_qspr_report.py
├── data/
│   ├── raw/
│   ├── plots/
│   ├── qspr_results/
│   └── drugs.db
├── run.py                    # Convenience launcher for backend + frontend
├── setup_service.sh          # Linux service setup helper
└── requirements.txt
```

## Environment Variables

No environment variable is strictly required to boot the platform locally. Every setting below has a default value.

### Backend Configuration

| Variable | Default | Purpose |
|---|---|---|
| `PROJECT_NAME` | `CardioQSPR` | FastAPI application title and backend project label |
| `PROJECT_DESCRIPTION` | `CardioQSPR — QSPR Regression Engine for Cardiovascular Drugs` | FastAPI description string |
| `PROJECT_VERSION` | `2.0.0` | FastAPI version string |
| `BACKEND_HOST` | `0.0.0.0` | Backend bind host |
| `BACKEND_PORT` | `5555` | Backend bind port |
| `FRONTEND_PORT` | `5173` | Frontend dev server port used by the launcher documentation/runtime assumptions |
| `API_PREFIX` | `/api` | URL prefix for all API routes |
| `STATIC_PLOTS_ROUTE` | `/plots` | Static route that serves generated plot images |
| `CORS_ALLOW_ORIGINS` | `*` | Comma-separated CORS allowlist |
| `DATABASE_PATH` | `data/drugs.db` | SQLite database file path |
| `PLOTS_DIR` | `data/plots` | Directory for generated plot assets |
| `QSPR_RESULTS_DIR` | `data/qspr_results` | Directory for generated reports and CSV outputs |
| `PUBCHEM_REST_URL` | `https://pubchem.ncbi.nlm.nih.gov/rest/pug` | PubChem PUG REST base URL |
| `PUBCHEM_VIEW_URL` | `https://pubchem.ncbi.nlm.nih.gov/rest/pug_view` | PubChem PUG View base URL |
| `EPI_SUITE_API_URL` | `https://episuite.dev/api/submit` | Remote EPI Suite-style fallback endpoint |
| `PUBCHEM_USER_AGENT` | `Mozilla/5.0 Python PubChemScraper` | User-Agent header for external data acquisition |
| `SCRAPER_DELAY_SECONDS` | `0.2` | Delay between scraper requests |
| `PUBCHEM_TIMEOUT_SECONDS` | `20` | HTTP timeout for external data requests |

### Frontend Configuration

| Variable | Default | Purpose |
|---|---|---|
| `VITE_API_HOST` | unset | Explicit API host override. If set, it bypasses host auto-resolution |
| `VITE_API_PORT` | `5555` | Backend port used by the frontend |
| `VITE_API_PREFIX` | `/api` | API route prefix used by the frontend |
| `VITE_STATIC_PREFIX` | `/plots` | Static plots route used by the frontend |
| `VITE_LOCAL_API_HOST` | `http://localhost` | Base host used for local API calls |
| `VITE_STORAGE_USER_KEY` | `cardio_user` | Local storage key for persisted login state |
| `VITE_APP_NAME` | `CardioQSPR` | Full frontend branding label |
| `VITE_APP_SHORT_NAME` | `CQ` | Compact branding label used in collapsed sidebar mode |
| `VITE_APP_VERSION` | `v1.0` | Frontend version badge |
| `VITE_HOST` | `0.0.0.0` | Vite dev server bind host |
| `VITE_PORT` | `5173` | Vite dev server port |

### Example

```bash
export BACKEND_PORT=5555
export DATABASE_PATH=/absolute/path/to/drugs.db
export CORS_ALLOW_ORIGINS=http://localhost:5173,https://your-domain.example
export VITE_API_PORT=5555
export VITE_APP_NAME=CardioQSPR
```

### Runtime Notes

- `PYTHONPATH` may still need to include `src/` when launching the backend manually from the repository root
- internet access is required for PubChem and EPI Suite fallbacks
- if you change route-related defaults such as `API_PREFIX` or `STATIC_PLOTS_ROUTE`, the frontend must be configured with matching `VITE_*` values

## Installation

If you only want the fastest working local setup, use the Quick Start block at the top of this README. The full installation steps below are for clarity and manual control.

### 1. Create A Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Optional: Install Playwright Browser Runtime

This is only needed if you plan to use browser-based scraping utilities or related experimentation.

```bash
playwright install chromium
```

## Local Development And Deployment

### Option A: Start The Full Platform With One Command

```bash
python run.py
```

This starts:

- backend API on `http://localhost:5555`
- frontend UI on `http://localhost:5173`

The backend OpenAPI docs are exposed at:

```text
http://localhost:5555/docs
```

### Option B: Start Backend And Frontend Separately

#### Backend

From the repository root:

```bash
export PYTHONPATH=$(pwd)/src
uvicorn api:app --reload --host 0.0.0.0 --port 5555
```

Alternative canonical entrypoint:

```bash
export PYTHONPATH=$(pwd)/src
uvicorn app.main:app --reload --host 0.0.0.0 --port 5555
```

#### Frontend

```bash
cd frontend
npm run dev
```

### Option C: Production-Style Frontend Build

```bash
cd frontend
npm run build
```

The compiled assets are generated under:

```text
frontend/dist/
```

## Linux Service Deployment

The repository includes `setup_service.sh` for Linux environments that use `systemd`.

It performs these steps:

- installs required system graphics libraries for RDKit image generation
- stops loose existing `run.py`, `uvicorn`, and `vite` processes
- creates a `cardio.service` systemd unit
- configures it to run `run.py` from the project virtual environment
- enables and starts the service

Usage:

```bash
sudo bash setup_service.sh
```

After installation:

- service status: `sudo systemctl status cardio`
- logs: `journalctl -u cardio -f`
- restart: `sudo systemctl restart cardio`
- stop: `sudo systemctl stop cardio`

## API And Frontend Behavior

The frontend dynamically resolves the API base URL:

- `localhost` / `127.0.0.1` -> backend at `http://localhost:5555`
- remote host with a dev port -> same host on port `5555`
- reverse-proxy deployment -> same protocol/host without forcing port in the URL

This logic lives in `frontend/src/config.js`.

## Data Persistence Model

CardioQSPR uses two kinds of persistence.

### 1. Master Drug Records

Stored in SQLite, these represent the canonical compound library.

### 2. Analysis Snapshots

When an analysis is created, the platform copies current property values into `AnalysisItem` rows. Those values can then be overridden safely for that single analysis without mutating the master library.

This is the core reason the workspace is useful for research: it supports controlled experimental what-if analyses.

## Outputs Generated

Each completed analysis can generate:

- `qspr_report.md`
- `all_models.csv`
- `best_models.csv`
- `top_models.csv`
- `predictions.csv`
- `equations.csv`
- `article_tables.csv`
- `r2_matrix.csv`
- `pvalue_matrix.csv`
- correlation plots for each property
- a molecular structure grid
- a global correlation comparison chart

Files are stored under:

- `data/qspr_results/<analysis_folder>/`
- `data/plots/<analysis_folder>/`

## Web Scraping Caveats

You should treat the ingestion layer as best-effort scientific automation, not as a regulatory-grade source of truth.

Known caveats:

- PubChem entries can mix experimental and computed values
- units and contextual meaning can vary across compounds
- some values may be decomposition points or derived values rather than directly measured targets
- fallback estimators are heuristic, not experimentally validated replacements

For high-stakes or publication-grade work, manually review:

- extreme outliers
- values inconsistent with known chemistry
- compounds with many estimated rather than experimental fields

## Current Configuration Summary

- backend port: `5555`
- frontend dev port: `5173`
- static plots served from `/plots`
- API mounted under `/api`
- database default path: `data/drugs.db`

## License

This project is intended for research, experimentation, and academic use.
