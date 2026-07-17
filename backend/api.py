from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os

from fl_server import metrics_history

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_FILE = "logs.json"
# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def read_logs():
    if not os.path.exists(LOG_FILE):
        return {"alerts": [], "trust": {}, "metrics": []}

    with open(LOG_FILE, "r") as f:
        return json.load(f)

# -------------------------------
# ROUTES
# -------------------------------

@app.get("/")
def root():
    return {"message": "Secure FL API Running"}

@app.get("/alerts")
def get_alerts():
    return read_logs().get("alerts", [])

@app.get("/trust")
def get_trust():
    return read_logs().get("trust", {})

@app.get("/metrics")
def get_metrics():
    return metrics_history