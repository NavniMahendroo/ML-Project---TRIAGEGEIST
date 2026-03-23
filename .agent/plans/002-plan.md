# TriageGeist Machine Learning Pipeline: Advanced Upgrades Plan (002)

## Overview
This document outlines the advanced, production-grade improvements intended for the TriageGeist ML architecture. These upgrades are designed to be layered purely on top of the foundational, clean modular pipeline established in `001-plan.md`, ensuring we secure the base architecture first before adding complexity.

---

## 🚀 Phase 3: Architecture Enhancements

### 1. Experiment Registry & Model Tracking (Weights & Biases / MLFlow)
*   **What it does:** Automatically logs, tracks, and visually catalogs your machine learning training sessions without relying on basic `print()` metrics and manual version strings.
*   **Implementation Strategy:** Wrap a `wandb.init()` tracker block inside `ml/src/train.py`. Instead of manually renaming model files (e.g., `v1.0.0.cbm`), the system will automatically log the active config, cache the hyperparameter runs (like tree depth and iterations), plot real-time loss curves during CV, and auto-version the resulting models. These visual dashboards are highly effective for college project demonstrations.

### 2. Strict API Payload Validation (Pydantic / FastAPI)
*   **What it does:** Prevents frontend web applications from crashing the ML backend by transmitting corrupted, missing, or improperly typed data.
*   **Implementation Strategy:** Implement Pydantic `BaseModel` schemas within the `ml/src/predict_api.py` gateway. Before invoking the model, Pydantic will rigorously validate incoming JSON requests to guarantee fields (e.g., verifying `age` is a valid integer and `chief_complaint_raw` exists). If the data payload is structurally compromised, the gateway cleanly rejects the request returning a 400 Bad Request API error instead of crashing the Python process.

### 3. YAML Configuration Management
*   **What it does:** Migrates hardcoded variables from native Python code into a standardized, language-agnostic data serialization format.
*   **Implementation Strategy:** Extract parameters (like file paths, batch sizes, and CatBoost learning rates) previously written into `ml/src/config.py` into a clear `config.yaml` document. The `config.py` module will be refactored to solely parse and load the YAML dictionary globally, cleanly separating data-tuning processes from code-execution logic.
