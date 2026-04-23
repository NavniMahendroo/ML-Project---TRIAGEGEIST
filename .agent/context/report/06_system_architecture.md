# V. System Architecture

TriageGeist is structured as a three-tier web application. The React single-page application communicates exclusively through a versioned REST API exposed by the FastAPI backend. Persistence is handled by MongoDB, with collections indexed at application startup to guarantee query performance under concurrent ED load.

## A. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite 5, Tailwind CSS, React Router v7 |
| Backend | Python 3.11, FastAPI, Uvicorn, Pydantic v2, PyJWT |
| ML / AI | CatBoost, BioBERT (dmis-lab/biobert-v1.1), PyTorch, scikit-learn, SHAP |
| Voice Chatbot | Vapi (cloud voice platform), Vapi Web SDK |
| Database | MongoDB with PyMongo; compound-indexed collections |
| Data Tools | Pandas, NumPy, SciPy, Parquet (PyArrow) |

TABLE III. TECHNOLOGY STACK BY LAYER

## B. Backend Router Structure
The FastAPI application registers seven routers at startup:
- **/triage** — ML inference and form options
- **/patients** — patient CRUD and fuzzy lookup
- **/chatbot** — session management, voice submit
- **/nurses** — staff authentication and management
- **/doctors** — doctor authentication, queue, duty toggle
- **/visits** — ED visit tracking
- **/superadmin** — cross-role administration and system oversight

All environment-specific configuration—MongoDB URI, Hugging Face token, Groq API key, Vapi keys, JWT secret, model version string—is supplied through a .env file loaded at startup. This 12-factor design enables the same codebase to run identically in local development, staging, and cloud production environments without code changes.

## C. ML Engine Lifecycle
All three CatBoost models (v1.0.2, v1.0.2-b, v1.0.2-c) are loaded into memory at server startup via a single load_all_models() call. BioBERT weights are loaded once and shared between v1.0.2 and v1.0.2-b. The /health endpoint reports which model versions are currently loaded and whether the BERT encoder is active, enabling operational monitoring:

```json
{
  "status": "ok",
  "engine": "ml_pipeline",
  "ml_model_loaded": true,
  "loaded_versions": ["v1.0.2", "v1.0.2-b", "v1.0.2-c"],
  "bert_loaded": true,
  "database_connected": true
}
```

## D. Authentication Model
TriageGeist uses JWT-based role authentication. Staff submit their credentials (nurse ID / doctor ID) and password to the appropriate login endpoint; the backend returns a signed JWT that the frontend stores and attaches to subsequent requests. The backend determines role automatically from the staff ID prefix (NURSE-XXXX vs DOC-XXXX), eliminating a role-selector UI element. Patient intake (triage form and chatbot) requires no authentication.

## E. Database Collections

| Collection | Contents |
|---|---|
| patients | Demographics, anthropometrics, visit counters, medical history |
| visits | One document per ED encounter; embeds triage prediction, doctor assignment, engine version |
| nurses | Staff credentials, department, shift |
| doctors | Doctor credentials, specialty, duty status, patient queue |
| chatbot_sessions | Full conversation transcript, collected fields, missing fields, session ID |
| sites | Hospital site configuration |
| _system_counters | Auto-increment counters for TG-, VT-, CS- ID generation |
