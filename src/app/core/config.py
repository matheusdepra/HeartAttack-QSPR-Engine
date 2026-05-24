import os
from pathlib import Path
from typing import List

# Base directories
APP_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = APP_DIR.parent
ROOT_DIR = SRC_DIR.parent

def _env_list(name: str, default: str) -> List[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "CardioQSPR")
    PROJECT_DESCRIPTION: str = os.getenv(
        "PROJECT_DESCRIPTION",
        "CardioQSPR — QSPR Regression Engine for Cardiovascular Drugs",
    )
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "2.0.0")

    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "5555"))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "5173"))

    API_PREFIX: str = os.getenv("API_PREFIX", "/api")
    STATIC_PLOTS_ROUTE: str = os.getenv("STATIC_PLOTS_ROUTE", "/plots")
    CORS_ALLOW_ORIGINS: List[str] = _env_list("CORS_ALLOW_ORIGINS", "*")

    DATABASE_PATH: str = os.getenv("DATABASE_PATH", str(ROOT_DIR / "data" / "drugs.db"))
    PLOTS_DIR: Path = Path(os.getenv("PLOTS_DIR", str(ROOT_DIR / "data" / "plots")))
    QSPR_RESULTS_DIR: Path = Path(os.getenv("QSPR_RESULTS_DIR", str(ROOT_DIR / "data" / "qspr_results")))

    PUBCHEM_REST_URL: str = os.getenv("PUBCHEM_REST_URL", "https://pubchem.ncbi.nlm.nih.gov/rest/pug")
    PUBCHEM_VIEW_URL: str = os.getenv("PUBCHEM_VIEW_URL", "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view")
    EPI_SUITE_API_URL: str = os.getenv("EPI_SUITE_API_URL", "https://episuite.dev/api/submit")
    PUBCHEM_USER_AGENT: str = os.getenv("PUBCHEM_USER_AGENT", "Mozilla/5.0 Python PubChemScraper")
    SCRAPER_DELAY_SECONDS: float = float(os.getenv("SCRAPER_DELAY_SECONDS", "0.2"))
    PUBCHEM_TIMEOUT_SECONDS: int = int(os.getenv("PUBCHEM_TIMEOUT_SECONDS", "20"))

    def __init__(self):
        self.PLOTS_DIR.mkdir(parents=True, exist_ok=True)
        self.QSPR_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
