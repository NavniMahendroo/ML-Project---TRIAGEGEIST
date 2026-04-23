# IX. Results and Discussion

## A. Cross-Validation Performance (v1.0.2 — Primary Model)
Five-fold stratified cross-validation on the training set yields consistent macro-averaged F1 across all folds, demonstrating that the model generalizes robustly rather than memorizing training examples. Per-fold variance in macro F1 remains below 0.02, indicating stable learning across different patient subsets.

| Metric | Mean (5-Fold CV) | Std. Dev. |
|---|---|---|
| Macro-avg F1 | 0.74 | 0.018 |
| Weighted-avg F1 | 0.81 | 0.012 |
| Accuracy | 0.82 | 0.011 |
| Acuity 1 Recall | 0.71 | 0.031 |
| Acuity 2 Recall | [ADD VALUE] | [ADD VALUE] |
| Acuity 3 Recall | 0.83 | 0.014 |
| Acuity 4 Recall | [ADD VALUE] | [ADD VALUE] |
| Acuity 5 Recall | [ADD VALUE] | [ADD VALUE] |
| Inference Latency | <150 ms | — |

TABLE IV. CROSS-VALIDATION PERFORMANCE METRICS (v1.0.2)

NOTE: Fill in Acuity 2, 4, 5 recall values from ml/logs/ before finalizing.

## B. Feature Importance Analysis
SHAP TreeExplainer analysis reveals that the five most impactful features are: news2_score, gcs_total, spo2, shock_index, and pain_score. The first BioBERT PCA component (biobert_pca_1) ranks seventh overall, confirming that free-text chief complaints carry independent predictive signal beyond what structured vitals alone capture. Complaints in the neurological and cardiovascular chief_complaint_system categories show the strongest NLP contribution to acuity elevation.

## C. Class Imbalance Handling
ESI Level 1 (Resuscitation) represents fewer than 2% of all ED visits in the dataset. Stratified cross-validation ensures every fold contains at least one example from this minority class. CatBoost's built-in class weight parameter is tuned to improve Level 1 recall, accepting a modest reduction in overall accuracy in exchange for reduced miss-rate on the most critical presentations.

## D. Ablation Study — Incremental Model Contributions

| Model Configuration | Macro-avg F1 |
|---|---|
| Logistic Regression (structured features only) | 0.61 |
| Logistic Regression + BioBERT PCA | 0.69 |
| CatBoost (structured features only) | ~0.70 |
| CatBoost + BioBERT PCA (v1.0.2) | 0.74 |

TABLE V. ABLATION STUDY RESULTS

The incremental contribution of both the domain-adapted language model (+8 points over structured-only logistic regression) and the gradient-boosted classifier (+5 points over logistic regression with NLP) is empirically validated.

## E. Multi-Model Routing Effectiveness
The three-model routing system provides two key quality improvements over a single-model approach:

1. **v1.0.2-b complaint inference** — when chief_complaint_system is absent (common in chatbot intake), v1.0.2-b infers it from free text before the acuity model runs, providing a meaningful categorical signal rather than forcing the primary model to treat it as Unknown. This is particularly impactful for acuity 1–2 cases where complaint system strongly correlates with severity.

2. **v1.0.2-c history-free fallback** — passing 25 NaN hx_* values into v1.0.2 degrades prediction quality because the model's internal weights were calibrated on a mix of present and absent history values. v1.0.2-c, trained without these columns, produces better-calibrated predictions for new or walk-in patients with no prior records.

NOTE: Add quantitative comparison of v1.0.2 vs v1.0.2-c accuracy on no-history patients if metrics are available from training logs.

## F. Chatbot Field Collection
In controlled simulation testing across 50 scripted patient dialogues covering all 14 chief_complaint_system categories, the chatbot successfully extracted all required triage fields in 94% of sessions. The 6% failure rate was primarily attributable to highly ambiguous chief complaints lacking a recognizable anatomical or symptomatic anchor (e.g., 'I don't feel right'). In these cases the bot correctly escalates to an explicit follow-up question rather than producing a hallucinated field value.

Patient ID resolution via fuzzy name + age matching correctly resolved all tested name variations with Levenshtein edit distance ≤ 2. The patient ID normalization (TG-002 → TG-0002) eliminates a common class of submit failures observed during testing.
