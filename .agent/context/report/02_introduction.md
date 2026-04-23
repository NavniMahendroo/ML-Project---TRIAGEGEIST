# I. Introduction

Emergency departments around the world face a convergence of pressures: rising patient volumes, chronic nursing shortages, and the cognitive burden placed on triage clinicians who must assign acuity scores rapidly and accurately under adverse conditions. Errors in triage severity scoring are not abstractions—they manifest as delayed treatment, adverse outcomes, and preventable deaths.

Established protocols such as the Emergency Severity Index (ESI) and the Manchester Triage System (MTS) were designed several decades ago and rely almost entirely on unaided clinical judgment. Inter-rater variability among triage nurses is well-documented in the literature, and systematic undertriage of certain demographic groups remains an active patient safety concern [1].

Artificial intelligence offers a complementary pathway: a model that ingests the same structured observations a nurse records—vitals, demographics, chief complaint—and produces a calibrated acuity recommendation that can serve as a second opinion, an audit trail, or a workload-prioritization signal for overwhelmed staff.

This paper presents TriageGeist, developed for the Triagegeist Kaggle competition organized by the Laitinen-Fredriksson Foundation, a Finnish medical research foundation dedicated to advancing clinical decision support in acute and emergency medicine. The system makes four primary contributions:

(i) A multi-model ML pipeline comprising three specialized CatBoost classifiers: a primary acuity predictor that fuses 47 structured clinical features with 10 BioBERT PCA components; a text-only chief complaint system classifier that infers body-system category from free-text; and a history-free fallback acuity predictor for patients without prior medical records. A runtime routing layer selects the appropriate model combination automatically based on data availability.

(ii) A Vapi-managed voice chatbot that captures spoken patient symptoms, extracts structured clinical fields via an LLM assistant, and feeds the result through the same unified triage inference pipeline—requiring no manual form entry.

(iii) A production-grade full-stack deployment: React frontend with role-specific portals (patient, nurse, doctor, superadmin), FastAPI backend with JWT authentication, MongoDB persistence, and SHAP-based model explainability reports.

(iv) Robustness features including patient ID normalization, fuzzy phonetic name matching with RapidFuzz, offline BioBERT inference, and session-level audit trails for every chatbot interaction.
