from fastapi.testclient import TestClient
from mock_api_server.main import app

client = TestClient(app)
def test_health():
    r=client.get("/health"); assert r.status_code==200 and r.json()["mock"] is True
def test_products():
    r=client.get("/mock-api/products",params={"keyword":"MagicBand"}); assert r.status_code==200 and r.json()["count"]>=1
def test_claim_status():
    r=client.get("/mock-api/reservations/RES-1001/claim-status"); assert r.status_code==200 and r.json()["status_summary"]["CLAIMED"]==2
def test_dining():
    r=client.post("/mock-api/dining/availability",json={"restaurant":"Cinderella's Royal Table","date":"2026-12-15","party_size":4}); assert r.status_code==200 and r.json()["available"] is True
