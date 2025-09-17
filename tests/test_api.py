from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_predict_endpoint():
    payload = {
        "superficie": "80m2",
        "habitaciones": "tres",
        "antiguedad": "nueva",
        "ubicacion": "urbano",
    }
    resp = client.post("/predict", json=payload)
    assert resp.status_code in (200, 400)
    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data["precio_estimado"], (int, float))
        assert data["precio_estimado"] >= 0


