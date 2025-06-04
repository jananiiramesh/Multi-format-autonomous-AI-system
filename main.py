from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class GenericPayload(BaseModel):
    source: Optional[str] = None
    issue_id: Optional[int] = None
    message: str
    details: Optional[str] = None

@app.post("/escalate")
async def escalate(payload: GenericPayload):
    print("Escalation received")
    print(payload)
    return {"status": "escalated", "received": payload}

@app.post("/risk_alert")
async def risk_alert(payload: GenericPayload):
    print("Risk alert received")
    print(payload)
    return {"status": "risk_alert_sent", "received": payload}
