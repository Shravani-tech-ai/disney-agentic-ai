"""Local simulated Disney provider API. All records are fictional test data."""
from pathlib import Path
from typing import Any
from difflib import SequenceMatcher
import json
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parent / "data"
def load(name: str) -> list[dict[str, Any]]:
    with (BASE / name).open(encoding="utf-8") as f: return json.load(f)
def norm(value: str) -> str: return " ".join(value.casefold().split())
def similarity(a: str,b: str) -> float: return SequenceMatcher(None,norm(a),norm(b)).ratio()
app = FastAPI(title="Disney Mock Provider APIs", version="1.0.0", description="Local simulation only. Not affiliated with or connected to Disney.")

class DuplicateRequest(BaseModel):
    guest_id: str = Field(min_length=1)
    name: str | None = None
    email: str | None = None
class DiningRequest(BaseModel):
    restaurant: str = Field(min_length=2)
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    party_size: int = Field(ge=1, le=20)
    preferred_time: str | None = None
class LightningLaneRequest(BaseModel):
    park: str = Field(min_length=2)
    attraction: str = Field(min_length=2)
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    preferred_time: str | None = None

@app.get("/health")
def health(): return {"status":"ok","service":"disney-mock-provider-api","mock":True}
@app.get("/mock-api/products")
def products(keyword: str = Query(default="", max_length=100)):
    rows=load("products.json")
    if keyword: rows=[p for p in rows if norm(keyword) in norm(p["name"]+" "+p["category"]+" "+p["description"]+" "+" ".join(p["tags"]))]
    return {"success":True,"mock":True,"count":len(rows),"products":rows}
@app.get("/mock-api/knowledge/search")
def knowledge(query: str = Query(min_length=1,max_length=200)):
    rows=load("knowledge.json"); scored=[]
    for row in rows:
        text=" ".join([row["title"],row["content"],*row["keywords"]]); score=max([similarity(query,k) for k in row["keywords"]]+[similarity(query,row["title"])])
        if norm(query) in norm(text) or score >= .25: scored.append({**row,"score":round(score,3)})
    scored.sort(key=lambda x:x["score"],reverse=True)
    return {"success":True,"mock":True,"query":query,"results":scored[:5]}
@app.post("/mock-api/friends-family/check-duplicates")
def duplicates(req: DuplicateRequest):
    guest=next((g for g in load("guests.json") if norm(g["guest_id"])==norm(req.guest_id)),None)
    if not guest: raise HTTPException(404,detail=f"Guest {req.guest_id} not found in mock data")
    profiles=guest["friends_family"]; exact=[]; possible=[]
    for i,a in enumerate(profiles):
        for b in profiles[i+1:]:
            email_match=bool(a.get("email") and norm(a["email"])==norm(b.get("email","")))
            name_score=similarity(a["name"],b["name"])
            if email_match: exact.append({"type":"EXACT_EMAIL_MATCH","profiles":[a,b],"confidence":"HIGH"})
            elif name_score>=.88: possible.append({"type":"POSSIBLE_NAME_MATCH","profiles":[a,b],"name_similarity":round(name_score,2),"confidence":"REVIEW_REQUIRED"})
    return {"success":True,"mock":True,"guest_id":guest["guest_id"],"guest_name":guest["name"],"profile_count":len(profiles),"exact_duplicates":exact,"possible_duplicates":possible,"note":"Detection only. No profile was changed."}
@app.get("/mock-api/reservations/{reservation_id}/claim-status")
def claim_status(reservation_id: str):
    row=next((r for r in load("reservations.json") if norm(r["reservation_id"])==norm(reservation_id)),None)
    if not row: raise HTTPException(404,detail=f"Reservation {reservation_id} not found in mock data")
    counts={}
    for g in row["guests"]: counts[g["claim_status"]]=counts.get(g["claim_status"],0)+1
    return {"success":True,"mock":True,**row,"guest_count":len(row["guests"]),"status_summary":counts,"note":"Simulated claim status. No reservation was changed."}
@app.post("/mock-api/dining/availability")
def dining(req: DiningRequest):
    rows=[s for s in load("dining.json") if norm(s["restaurant"])==norm(req.restaurant) and s["date"]==req.date and s["party_size_min"]<=req.party_size<=s["party_size_max"] and s["status"]=="AVAILABLE"]
    if req.preferred_time: rows.sort(key=lambda s:abs(int(s["time"][:2])*60+int(s["time"][3:])-int(req.preferred_time[:2])*60-int(req.preferred_time[3:])))
    return {"success":True,"mock":True,"restaurant":req.restaurant,"date":req.date,"party_size":req.party_size,"available":bool(rows),"available_slots":rows,"note":"Simulated availability only. No table is booked or held."}
@app.post("/mock-api/lightning-lane/availability")
def lightning_lane(req: LightningLaneRequest):
    rows=[s for s in load("lightning_lane.json") if norm(s["park"])==norm(req.park) and norm(s["attraction"])==norm(req.attraction) and s["date"]==req.date and s["status"]=="AVAILABLE"]
    return {"success":True,"mock":True,"park":req.park,"attraction":req.attraction,"date":req.date,"available":bool(rows),"available_slots":rows,"note":"Simulated availability only. No pass is selected, purchased or held."}
