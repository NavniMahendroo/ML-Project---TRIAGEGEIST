import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from database import HOST, PORT
from triage.service import load_ml_model, get_engine_status
from triage.router import router as triage_router
from patients.router import router as patients_router
from users.router import router as users_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

app = FastAPI(title="Triagegeist API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(triage_router)
app.include_router(patients_router)
app.include_router(users_router)

@app.on_event("startup")
def startup_event():
    log.info("Starting TriageGeist API Server...")
    load_ml_model()

@app.get("/health")
def health_check():
    status = get_engine_status()
    return {
        "status": "ok",
        "engine": status["engine"],
        "ml_model_loaded": status["ml_model_loaded"],
    }

if __name__ == "__main__":
    uvicorn.run("server:app", host=HOST, port=PORT, reload=True)
