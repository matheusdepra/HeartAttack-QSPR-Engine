import sys

from fastapi.testclient import TestClient


def _fresh_app(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "drugs.db"))
    monkeypatch.setenv("PLOTS_DIR", str(tmp_path / "plots"))
    monkeypatch.setenv("QSPR_RESULTS_DIR", str(tmp_path / "qspr_results"))
    monkeypatch.setenv("AUTO_SEED_DATABASE", "true")
    monkeypatch.setenv("SEED_BASELINE_DRUGS", "true")
    monkeypatch.setenv("SEED_DEFAULT_ADMIN", "true")
    monkeypatch.setenv("DEFAULT_ADMIN_USERNAME", "admin")
    monkeypatch.setenv("DEFAULT_ADMIN_PASSWORD", "admin123")

    for module_name in list(sys.modules):
        if module_name == "app" or module_name.startswith("app."):
            del sys.modules[module_name]

    from app.main import app

    return app


def test_health_endpoint(monkeypatch, tmp_path):
    app = _fresh_app(monkeypatch, tmp_path)

    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_fresh_clone_seeds_baseline_drugs(monkeypatch, tmp_path):
    app = _fresh_app(monkeypatch, tmp_path)

    with TestClient(app) as client:
        response = client.get("/api/drugs")

    assert response.status_code == 200
    drugs = response.json()
    assert len(drugs) >= 20
    assert any(drug["name"] == "Aspirin" for drug in drugs)


def test_default_local_admin_can_login(monkeypatch, tmp_path):
    app = _fresh_app(monkeypatch, tmp_path)

    with TestClient(app) as client:
        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"},
        )

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_predict_endpoint_calculates_indices(monkeypatch, tmp_path):
    app = _fresh_app(monkeypatch, tmp_path)

    with TestClient(app) as client:
        response = client.post("/api/predict", params={"smiles": "CCO"})

    assert response.status_code == 200
    assert response.json()["indices"]["M1"] > 0
