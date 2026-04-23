# III. Dataset

## A. Source and Competition Context
The dataset was provided by the Triagegeist Kaggle competition and originates from a real emergency department information system operated by the Laitinen-Fredriksson Foundation. It comprises four relational CSV files linked by a common patient_id key.

## B. File Structure
- **train.csv** — ~80,000 patient visits, 40 columns including the primary target triage_acuity (ESI 1–5) and secondary targets disposition and ed_los_hours.
- **test.csv** — same 37 structural columns without target labels; used for Kaggle submission generation.
- **patient_history.csv** — 26 binary comorbidity flags per patient (hx_* fields: hypertension, diabetes type 1 & 2, asthma, COPD, heart failure, atrial fibrillation, CKD, liver disease, malignancy, obesity, depression, anxiety, dementia, epilepsy, hypothyroidism, hyperthyroidism, HIV, coagulopathy, immunosuppressed, pregnant, substance use disorder, coronary artery disease, prior stroke, peripheral vascular disease).
- **chief_complaints.csv** — raw and categorized free-text chief complaints with 14 body-system class labels.

## C. Feature Summary

| Category | Key Variables |
|---|---|
| Demographics | age, age_group, sex, language, insurance_type |
| Arrival | arrival_mode, arrival_hour, arrival_day, shift, transport_origin |
| Vitals | systolic_bp, diastolic_bp, heart_rate, respiratory_rate, temperature_c, spo2, pain_score |
| Derived Scores | gcs_total, shock_index, news2_score, mean_arterial_pressure, pulse_pressure, bmi |
| Comorbidities | 25 binary hx_* flags (hypertension, diabetes type 1 & 2, COPD, heart_failure, CKD, malignancy, etc.) |
| NLP | 10 BioBERT PCA principal components from chief_complaint_raw |

TABLE I. DATASET FEATURE CATEGORIES

## D. Class Distribution
ESI Level 1 (Resuscitation) represents fewer than 2% of all ED visits, creating significant class imbalance. Levels 3 (Urgent) and 4 (Less Urgent) together account for the majority of encounters, reflecting the typical ED patient mix. Stratified cross-validation and CatBoost class weighting are used to address this imbalance.
