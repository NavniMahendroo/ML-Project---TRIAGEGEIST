# College ML Project: Triagegeist

## Project Overview

This project is built around the Kaggle competition **Triagegeist**. The goal is to predict emergency severity (`triage_acuity`) and optimize triage decisions using clinical data.

We are developing this machine learning model for a college project presentation. The final product will serve a dual purpose: 
1. A submission to the global Kaggle competition.
2. An interactive project (e.g., deployed in a web app or interactive notebook) to present to the class.

## Objectives

1. **Develop an ML Model**: Train a robust model to predict the triage acuity of incoming patients in an emergency department.
2. **Kaggle Submission**: Generate predictions for the `test.csv` dataset and submit the formatted `sample_submission.csv` to Kaggle.
3. **College Presentation**: Deploy the model to "some place" (a web interface or local app) to showcase the functionality live during the presentation.

## Dataset Details

The dataset consists of several tabular files providing detailed patient histories, chief complaints, and triage information.
- **train.csv**: Contains 40 columns including patient demographics, vitals, pain scores, and target variables like `triage_acuity`, `disposition`, and `ed_los_hours`.
- **test.csv**: Contains 37 columns. We need to predict `triage_acuity` for these records.
- **patient_history.csv**: Contains 26 columns detailing pre-existing medical conditions (e.g., hypertension, diabetes, asthma).
- **chief_complaints.csv**: Contains raw and categorized chief complaints of the patients.
- **sample_submission.csv**: Defines the submission format (`patient_id`, `triage_acuity`).

### Key Features Observed

- **Demographics**: `age`, `age_group`, `sex`, `language`, `insurance_type`
- **Visit Context**: `arrival_mode`, `arrival_hour`, `arrival_day`, `shift`, `transport_origin`
- **Clinical Vitals**: `systolic_bp`, `diastolic_bp`, `heart_rate`, `respiratory_rate`, `temperature_c`, `spo2`, `pain_score`
- **Medical Scores**: `gcs_total`, `shock_index`, `news2_score`
- **Target Variable**: `triage_acuity` (Integer scale)

## Action Plan

1. **Data Preprocessing**: Merge the datasets (`train.csv`, `patient_history.csv`, `chief_complaints.csv`) based on `patient_id`. Handle any missing values and encode categorical variables.
2. **Exploratory Data Analysis (EDA)**: Understand feature distributions, identifying outliers, and reviewing correlations with `triage_acuity`.
3. **Model Training**: Train baseline and advanced tree-based models (e.g., XGBoost, LightGBM, Random Forest) suitable for tabular dataset prediction.
4. **Evaluation**: Validate the model locally, generate test predictions, and format the Kaggle submission.
5. **Deployment / Presentation Prep**: Wrap the model in a simple frontend interface (e.g., Streamlit, Flask, or a React app) so it can be demonstrated to the class tomorrow.
