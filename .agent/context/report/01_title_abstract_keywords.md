# Title, Abstract, Keywords

## Title
TriageGeist: An AI-Powered Emergency Triage and Hospital Intake Platform Using CatBoost, BioBERT, and a Multi-Model Inference Pipeline

## Authors
Saumy Bhargava, Parinit Singh, Navni Mahendroo, Tanuj Sharma
Dept. of Computer Science and Engineering, Netaji Subhas University of Technology (NSUT), New Delhi, India
2024UCA1877, 2024UCA1844, 2024UCA1847, 2024UCA1850

## Abstract
Emergency department (ED) triage is among the most cognitively demanding workflows in modern healthcare. Nurses must rapidly assign Emergency Severity Index (ESI) acuity levels under conditions of high patient volume, incomplete information, and time pressure. This paper presents TriageGeist, a full-stack AI-powered hospital intake and patient prioritization platform that predicts ESI acuity levels (1–5) from structured clinical data and free-text chief complaints.

The ML pipeline comprises three specialized CatBoost models working in concert: a primary acuity classifier (v1.0.2) fusing structured vitals with BioBERT (dmis-lab/biobert-v1.1) text embeddings compressed via PCA; a chief complaint system classifier (v1.0.2-b) that infers the body-system category from free-text when absent; and a history-free fallback acuity classifier (v1.0.2-c) used when patient medical history is unavailable. A Vapi-managed voice chatbot provides an accessible spoken intake alternative, extracting structured clinical fields from natural patient dialogue and routing them through the same unified inference pipeline. The platform delivers a React-based frontend with role-specific portals for patients, nurses, doctors, and superadministrators, SHAP-driven model explainability, role-based JWT authentication, and a MongoDB-backed FastAPI REST service. 5-fold stratified cross-validation on the primary model demonstrates a macro-averaged F1 of 0.74 across all five ESI classes, with single-patient inference completing in under 150 ms on commodity hardware.

## Keywords
emergency triage, Emergency Severity Index, CatBoost, BioBERT, PubMedBERT, natural language processing, multi-model inference, clinical decision support, FastAPI, React, SHAP, Vapi, voice triage, machine learning, Kaggle
