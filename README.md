<p align="center">
  <h1 align="center">🏥 TriageGeist</h1>
  <p align="center">
    <strong>AI-Powered Emergency Triage &amp; Hospital Intake Platform</strong>
  </p>
  <p align="center">
    <a href="#-features">Features</a> · <a href="#-benefits">Benefits</a> · <a href="#%EF%B8%8F-architecture">Architecture</a> · <a href="#-getting-started">Getting Started</a> · <a href="#-usage">Usage</a> · <a href="#-project-structure">Project Structure</a>
  </p>
</p>

---

## 📋 Overview

**TriageGeist** is a full-stack hospital intake and patient prioritization platform that leverages machine learning to classify patient urgency, streamline care workflows, and provide decision-makers with real-time operational insights.

The system combines a **CatBoost** gradient-boosted model with **BioBERT** text embeddings to predict ESI (Emergency Severity Index) triage acuity levels from structured patient data and free-text chief complaints. An LLM-powered conversational chatbot provides an alternative intake pathway, extracting clinical fields from natural patient dialogue.

---

## ✨ Features

| Module | Capability |
|---|---|
| **ML Pipeline** | CatBoost classifier with BioBERT (PubMedBERT) text embeddings and PCA dimensionality reduction |
| **Triage Form** | Structured patient intake form with real-time ML-powered acuity prediction |
| **AI Chatbot** | Conversational triage assistant powered by Llama 3.2 (Ollama / Groq fallback) with automatic clinical field extraction |
| **Doctor Portal** | Assigned patient queue, acuity tracking, on-duty toggle, and specialty-based routing |
| **Staff Portal** | Role-based nurse dashboard with task management and authenticated workflows |
| **Explainability** | SHAP-based model interpretability reports generated during training |

---

## 🎯 Benefits

### For Hospitals & Clinicians

- **⏱️ Faster Patient Routing** — ML-driven acuity predictions enable nurses to prioritize critical patients within seconds, reducing time-to-treatment in high-volume emergency departments.
- **📉 Reduced Wait Times** — Automated severity classification eliminates bottlenecks caused by manual triage scoring, keeping patient flow moving during peak hours.
- **🎯 Consistent Acuity Scoring** — The model removes subjective variability between individual triage nurses, producing standardized ESI-level predictions grounded in clinical data.
- **🗣️ Accessible Patient Intake** — The conversational AI chatbot allows patients to describe symptoms in plain language, lowering literacy and language barriers during registration.
- **📊 Data-Driven Decision Making** — Admin dashboards surface real-time department load, outcome trends, and staffing metrics, enabling evidence-based operational decisions.
- **🔍 Transparent Predictions** — SHAP explainability reports show *why* the model assigned a particular acuity level, building clinician trust and supporting auditability.

### For Developers & Researchers

- **🧩 Modular Architecture** — Training, inference, and API code are fully decoupled. Heavy GPU training never interferes with the lightweight production server.
- **📡 Offline-Ready Inference** — BioBERT embeddings load from local cache by default, allowing the system to run in air-gapped hospital networks with no internet dependency.
- **🔄 Versioned Model Pipeline** — Hyperparameters, model binaries, and PCA transformers are version-controlled via JSON configs, making experiment tracking and rollback trivial.
- **🤖 Dual LLM Fallback** — The chatbot tries a local Ollama model first, then automatically falls back to Groq's cloud API, ensuring availability regardless of GPU resources.
- **📈 Reproducible Experiments** — 5-fold cross-validation with fixed random seeds, Parquet-based intermediate datasets, and structured logging ensure fully reproducible results.
- **⚡ Production-Grade Stack** — FastAPI async backend, React SPA frontend, and MongoDB persistence provide a battle-tested foundation ready for real deployment.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React + Vite)              │
│  Landing · Triage Form · Chatbot · Doctor Portal · Staff Portal │
└────────────────────────────┬────────────────────────────────┘
                             │  REST API
┌────────────────────────────▼────────────────────────────────┐
│                    Backend (FastAPI + Uvicorn)               │
│  Routers: triage · patients · chatbot · nurses · doctors    │
│  Services: ML inference · LLM extraction · Session mgmt     │
└──────┬─────────────────────┬──────────────────────┬─────────┘
       │                     │                      │
  ┌────▼─────┐        ┌──────▼──────┐        ┌─────▼──────┐
  │ MongoDB  │        │  ML Engine  │        │ LLM Layer  │
  │ Database │        │  CatBoost   │        │ Ollama /   │
  │          │        │  BioBERT    │        │ Groq API   │
  └──────────┘        │  PCA        │        └────────────┘
                      └─────────────┘
```

### Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite 5, Tailwind CSS, React Router v7 |
| **Backend** | Python, FastAPI, Uvicorn, Pydantic |
| **ML / AI** | CatBoost, BioBERT (PubMedBERT), PyTorch, scikit-learn, SHAP |
| **LLM** | Ollama (Llama 3.2), Groq Cloud (fallback), LangGraph |
| **Database** | MongoDB (PyMongo) |
| **Data** | Pandas, NumPy, SciPy, Parquet |

---

## 🚀 Getting Started

### Prerequisites

- **Python** 3.10+
- **Node.js** 18+ and **npm**
- **MongoDB** (local instance or Atlas URI)
- **Ollama** *(optional — for local LLM chatbot; falls back to Groq cloud)*

### 1. Clone the Repository

```bash
git clone https://github.com/NavniMahendroo/ML-Project---TRIAGEGEIST.git
cd ML-Project---TRIAGEGEIST
```

### 2. Install Python Dependencies

Create and activate a virtual environment, then install:

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Configure Environment Variables

Copy the example `.env` files and fill in your credentials:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and configure:

| Variable | Description |
|---|---|
| `MONGO_URI` | MongoDB connection string (e.g. `mongodb://localhost:27017`) |
| `HF_TOKEN` | Hugging Face API token (create a free "Read" token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)) |
| `GROQ_API_KEY` | *(Optional)* Groq API key for cloud LLM fallback |

### 5. Seed the Database

Load the seed snapshot into MongoDB:

```bash
cd backend
python scripts/seed2.py
```

This populates the following collections from JSON snapshots in `backend/scripts/seed2_data/`:

| File | Collection | Contents |
|---|---|---|
| `patients.json` | `patients` | 15 patients (TG-0001 → TG-0015) |
| `visits.json` | `visits` | 6 visits (VT-0001 → VT-0006) |
| `patient_history.json` | `patient_history` | Medical history for 3 patients |
| `doctors.json` | `doctors` | 10 doctors (DOC-0001 → DOC-0010) across specialties |
| `nurses.json` | `nurses` | 10 nurses (NURSE-0001 → NURSE-0010) |
| `sites.json` | `sites` | 5 hospital sites (SITE-0001 → SITE-0005) |
| `_system_counters.json` | `_system_counters` | Auto-increment counters for ID generation |

**Default password for all seeded users: `12345678`**

> **`_system_counters` explained:** The backend generates IDs like `TG-0016`, `VT-0007`, `CS-0001` using an atomic counter in MongoDB. The seed file sets these counters to match the highest existing ID in each collection so new records never collide. Counters seeded: `patients` (15), `visits` (6), `chatbot_sessions` (0), `doctor_assignment:Emergency` (2).

### 6. Place Large Files

Due to GitHub's file size limits, large datasets and trained model binaries are **not** included in this repository. Obtain them from the team's shared drive and place them as follows:

| File(s) | Destination |
|---|---|
| `train.csv`, `test.csv`, `patient_history.csv`, `chief_complaints.csv`, `sample_submission.csv` | `ml/dataset/raw/` |
| `model_<version>.cbm`, `pca_<version>.pkl` | `ml/models/<version>/` |

---

## 💻 Usage

The project provides three distinct execution gateways depending on your goal:

### 🌐 Option A — Run the Full Application

Start both the backend API and the frontend dev server:

```bash
# Terminal 1: Backend
python backend/server.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

- **Backend API** → `http://127.0.0.1:8000`
- **Frontend UI** → `http://127.0.0.1:5173`

The backend automatically connects to MongoDB, runs index migrations, and loads the ML model into memory on startup.

**Access the platform:**

| Role | URL | Login |
|---|---|---|
| Patient (Triage Form) | `/patient/form` | No login required |
| Patient (Chatbot) | `/patient/chatbot` | No login required |
| Staff (Nurse) | `/signin` → Staff role | `NURSE-0001` / `12345678` |
| Doctor (Admin) | `/signin` → Admin role | `DOC-0001` / `12345678` |

### 📊 Option B — Generate a Kaggle Submission

Batch-predict across the full test set and produce a `submission.csv`:

```bash
python ml/run_kaggle.py
```

> Loads the trained model, runs inference on all rows in `test.csv`, and saves the formatted submission file.

### 🔬 Option C — Train a New Model from Scratch

> ⚠️ **Only use this when modifying datasets or hyperparameters.** Training is computationally expensive (~30 min on an RTX 4050 GPU).

```bash
python ml/run_train.py
```

This will:
1. Clean and merge raw datasets
2. Extract BioBERT text embeddings (~80k records)
3. Run 5-fold stratified cross-validation
4. Generate SHAP explainability reports in `ml/logs/`
5. Save the final model and PCA transformer to `ml/models/`

---

## 📁 Project Structure

```
ML-Project---TRIAGEGEIST/
│
├── backend/                    # FastAPI backend server
│   ├── server.py               # Application entry point & router registration
│   ├── database.py             # MongoDB connection & index management
│   ├── src/
│   │   ├── triage/             # ML inference, doctor routing & visit creation
│   │   ├── patients/           # Patient CRUD operations
│   │   ├── chatbot/            # LLM-powered conversational triage
│   │   ├── nurses/             # Staff authentication & management
│   │   ├── doctors/            # Doctor authentication, queue & duty management
│   │   ├── visits/             # Visit tracking
│   │   ├── patient_history/    # Patient history records
│   │   └── sites/              # Site / department configuration
│   ├── constants/
│   │   └── routing.py          # Specialty-to-keyword mapping for doctor routing
│   ├── scripts/
│   │   ├── seed2.py            # Restore DB from JSON snapshots (recommended)
│   │   ├── seed.py             # Generate fresh test data programmatically
│   │   └── seed2_data/         # JSON seed snapshots (patients, visits, doctors…)
│   └── .env.example            # Environment variable template
│
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx             # Root component & route definitions
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx         # Public landing page
│   │   │   ├── TriagePage.jsx          # Structured triage intake form
│   │   │   ├── SignInPage.jsx          # Staff / doctor authentication
│   │   │   ├── ChatbotPage/            # AI chatbot interface
│   │   │   ├── DoctorPage/             # Doctor portal (auth-protected)
│   │   │   │   ├── DoctorPatientsPage.jsx   # Assigned patient queue
│   │   │   │   ├── DoctorStaffPage.jsx      # Staff roster & on-duty status
│   │   │   │   ├── DoctorStatsPage.jsx      # Department statistics
│   │   │   │   ├── DoctorOutcomesPage.jsx   # Outcome tracking
│   │   │   │   ├── DoctorSettingsPage.jsx   # Doctor settings
│   │   │   │   └── DoctorDashboardPage.jsx  # Dashboard (unused route)
│   │   │   └── StaffPage/              # Staff portal (auth-protected)
│   │   │       ├── StaffDashboardPage.jsx   # Nurse shift dashboard
│   │   │       ├── StaffTasksPage.jsx       # Task management
│   │   │       ├── StaffSettingsPage.jsx    # Staff settings
│   │   │       └── StaffLogoutPage.jsx      # Logout handler
│   │   └── components/         # Reusable UI components
│   └── package.json
│
├── ml/                         # Machine Learning pipeline
│   ├── run_api.py              # API inference gateway
│   ├── run_kaggle.py           # Kaggle submission generator  (not in repo, see Usage)
│   ├── run_train.py            # Full training pipeline        (not in repo, see Usage)
│   ├── src/
│   │   ├── base_config.py      # Directory paths & dataset constants
│   │   ├── config.py           # Version-specific model parameters
│   │   └── predict_api.py      # Prediction engine (BioBERT + CatBoost)
│   ├── dataset/
│   │   ├── raw/                # Original CSV/DTA files (not tracked)
│   │   └── processed/          # Cleaned Parquet intermediates
│   ├── models/                 # Trained model binaries (not tracked)
│   ├── params/                 # Versioned hyperparameter JSON files
│   ├── logs/                   # Training logs & SHAP reports
│   ├── metrics/                # Cross-validation metrics
│   └── notebooks/              # Exploratory Jupyter notebooks
│
└── requirements.txt            # Python dependency manifest
```

---

## 🔧 Configuration

### Model Versioning

The ML pipeline uses a versioned parameter system. The active model version is controlled by `MODEL_VERSION` in [`ml/src/config.py`](ml/src/config.py). Each version has a corresponding JSON configuration in `ml/params/` that defines:

- BioBERT model name and tokenizer settings
- PCA component count
- CatBoost hyperparameters
- Cross-validation folds and random seed

### Offline Mode

By default, the system runs in **offline mode** (`TRANSFORMERS_OFFLINE=1`) to avoid network calls during inference. BioBERT weights are loaded from the local Hugging Face cache. To download models for the first time, temporarily set the environment variables to `0` or remove them.

---

## 🤝 Contributing

1. **Fork** the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a **Pull Request**

> Please ensure your code follows the existing project structure and conventions.

---

## 📄 License

This project was developed as part of an academic machine learning course. Please contact the repository maintainers for licensing and usage inquiries.

---

<p align="center">
  <sub>Built with ❤️ using CatBoost, BioBERT, FastAPI, and React</sub>
</p>
