"""
compute_v102_oof_metrics.py
============================
Computes proper OOF metrics for v1.0.2 (the full model — 61 features).

Steps:
  1. Rebuild train feature matrix (structured + hx_* + BioBERT PCA)
  2. Run OOF predictions using all 5 saved fold models
  3. Report QWK, macro-F1, per-class metrics, under/over-triage rates
  4. Save embeddings as CSVs for Kaggle upload

Run from kaggle_submission/ directory:
  cd /home/saumy/Documents/ML-Project---TRIAGEGEIST/kaggle_submission
  python compute_v102_oof_metrics.py
"""

import pandas as pd
import numpy as np
import joblib
import torch
import json
from pathlib import Path
from transformers import AutoTokenizer, AutoModel
from catboost import CatBoostClassifier, Pool
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    cohen_kappa_score, f1_score, classification_report, accuracy_score
)
from tqdm.auto import tqdm

ML = Path("../ml")

BERT_MODEL  = "dmis-lab/biobert-v1.1"
BATCH_SIZE  = 64
MAX_LEN     = 64
N_FOLDS     = 5
SEED        = 42

# ── Step 1: Rebuild train feature matrix ─────────────────────────────────────
print("=" * 60)
print("STEP 1 — Rebuilding train feature matrix")
print("=" * 60)

master_df = pd.read_parquet(ML / "dataset/processed/master_dataset.parquet")

drop_cols = [
    'patient_id', 'site_id', 'triage_nurse_id',
    'arrival_hour', 'arrival_day', 'arrival_month', 'arrival_season', 'shift',
    'language', 'transport_origin', 'insurance_type',
    'disposition', 'ed_los_hours'
]
clean_df = master_df.drop(columns=drop_cols)
clean_df['chief_complaint_raw'] = clean_df['chief_complaint_raw'].fillna("No Data")
cat_cols = clean_df.select_dtypes(include=['object', 'string']).columns
clean_df[cat_cols] = clean_df[cat_cols].fillna("Unknown")

print(f"Train shape: {clean_df.shape}")

# ── Step 2: BioBERT on train texts (skipped if CSV already exists) ────────────
print("\n" + "=" * 60)
print("STEP 2 — BioBERT embedding extraction (train)")
print("=" * 60)

embed_csv = Path("train_biobert_pca.csv")

if embed_csv.exists():
    print(f"train_biobert_pca.csv already exists — loading from disk, skipping BioBERT.")
    pca_df = pd.read_csv(embed_csv)
    pca_df.index = clean_df.index
    print(f"Loaded: {pca_df.shape}")
else:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")

    tokenizer  = AutoTokenizer.from_pretrained(BERT_MODEL)
    bert_model = AutoModel.from_pretrained(BERT_MODEL).to(device)
    bert_model.eval()

    texts = clean_df['chief_complaint_raw'].tolist()
    all_embeddings = []

    print(f"Embedding {len(texts):,} train complaints...")
    with torch.no_grad():
        for i in tqdm(range(0, len(texts), BATCH_SIZE)):
            batch = texts[i : i + BATCH_SIZE]
            encoded = tokenizer(
                batch, padding=True, truncation=True,
                max_length=MAX_LEN, return_tensors='pt'
            ).to(device)
            outputs = bert_model(**encoded)
            cls = outputs.last_hidden_state[:, 0, :].cpu().numpy()
            all_embeddings.append(cls)

    train_raw_emb = np.vstack(all_embeddings)
    print(f"Train embeddings: {train_raw_emb.shape}")

    del bert_model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    print("GPU memory released.")

    # ── Step 3: Apply existing PCA ────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("STEP 3 — Applying pca_v1.0.2.pkl")
    print("=" * 60)

    pca = joblib.load(ML / "models/v1.0.2/pca_v1.0.2.pkl")
    print(f"PCA: {pca.n_features_in_} → {pca.n_components_} dims")
    print(f"Variance retained: {pca.explained_variance_ratio_.sum()*100:.1f}%")

    train_pca = pca.transform(train_raw_emb)
    pca_cols  = [f"biobert_pca_{i+1}" for i in range(pca.n_components_)]
    pca_df    = pd.DataFrame(train_pca, columns=pca_cols, index=clean_df.index)

    pca_df.to_csv(embed_csv, index=False)
    print(f"Saved: kaggle_submission/train_biobert_pca.csv  {pca_df.shape}")

# ── Step 4: Build final feature matrix ───────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 4 — Building final feature matrix")
print("=" * 60)

final_df = pd.concat([
    clean_df.drop(columns=['chief_complaint_raw', 'triage_acuity']),
    pca_df
], axis=1)

Y = clean_df['triage_acuity'].values
X = final_df

# Verify column order matches what models expect
model_check = CatBoostClassifier()
model_check.load_model(str(ML / "models/v1.0.2/model_v1.0.2_fold_1.cbm"))
expected = model_check.feature_names_

assert list(X.columns) == list(expected), \
    f"Feature mismatch!\nGot: {list(X.columns)}\nExpected: {list(expected)}"

# Match exactly how notebook 2 trained: pass cat feature names, not indices
cat_features = list(X.select_dtypes(include=['object', 'string']).columns)

print(f"Feature matrix: {X.shape}")
print(f"Feature names match model: ✓")
print(f"Categorical features ({len(cat_features)}): {cat_features}")

# ── Step 5: OOF evaluation on v1.0.2 ─────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 5 — OOF evaluation using v1.0.2 fold models")
print("=" * 60)

skf       = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
oof_preds = np.zeros(len(Y), dtype=int)
oof_probs = np.zeros((len(Y), 5))
qwk_folds = []
f1_folds  = []

for fold, (tr_idx, val_idx) in enumerate(skf.split(X, Y)):
    model = CatBoostClassifier()
    model.load_model(str(ML / f"models/v1.0.2/model_v1.0.2_fold_{fold+1}.cbm"))

    val_pool = Pool(X.iloc[val_idx], cat_features=cat_features)
    probs    = model.predict_proba(val_pool)
    preds    = np.argmax(probs, axis=1) + 1

    oof_probs[val_idx] = probs
    oof_preds[val_idx] = preds

    fold_qwk = cohen_kappa_score(Y[val_idx], preds, weights='quadratic')
    fold_f1  = f1_score(Y[val_idx], preds, average='macro')
    qwk_folds.append(fold_qwk)
    f1_folds.append(fold_f1)
    print(f"  Fold {fold+1}  |  QWK: {fold_qwk:.4f}  |  Macro-F1: {fold_f1:.4f}")

# ── Step 6: All metrics ───────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 6 — Full metric report (v1.0.2 OOF)")
print("=" * 60)

qwk  = cohen_kappa_score(Y, oof_preds, weights='quadratic')
lwk  = cohen_kappa_score(Y, oof_preds, weights='linear')
uk   = cohen_kappa_score(Y, oof_preds, weights=None)
mf1  = f1_score(Y, oof_preds, average='macro')
wf1  = f1_score(Y, oof_preds, average='weighted')
acc  = accuracy_score(Y, oof_preds)
undertriage = np.sum(oof_preds > Y) / len(Y)
overtriage  = np.sum(oof_preds < Y) / len(Y)

print(f"\nCV  QWK:                    {np.mean(qwk_folds):.4f} ± {np.std(qwk_folds):.4f}")
print(f"OOF QWK:                    {qwk:.4f}")
print(f"OOF Linear Weighted Kappa:  {lwk:.4f}")
print(f"OOF Unweighted Kappa:       {uk:.4f}")
print(f"OOF Macro-F1:               {mf1:.4f}")
print(f"OOF Weighted-F1:            {wf1:.4f}")
print(f"OOF Accuracy:               {acc:.4f}")
print(f"Under-triage rate:          {undertriage*100:.2f}%")
print(f"Over-triage rate:           {overtriage*100:.2f}%")
print(f"\n{classification_report(Y, oof_preds, target_names=['ESI-1','ESI-2','ESI-3','ESI-4','ESI-5'])}")

# Save metrics to file
results = {
    "model_version": "v1.0.2",
    "oof_qwk": round(qwk, 4),
    "oof_linear_kappa": round(lwk, 4),
    "oof_unweighted_kappa": round(uk, 4),
    "oof_macro_f1": round(mf1, 4),
    "oof_weighted_f1": round(wf1, 4),
    "oof_accuracy": round(acc, 4),
    "undertriage_rate": round(undertriage, 4),
    "overtriage_rate": round(overtriage, 4),
    "cv_qwk_mean": round(np.mean(qwk_folds), 4),
    "cv_qwk_std": round(np.std(qwk_folds), 4),
    "fold_qwk": {f"fold_{i+1}": round(v, 4) for i, v in enumerate(qwk_folds)},
    "fold_macro_f1": {f"fold_{i+1}": round(v, 4) for i, v in enumerate(f1_folds)},
}

import json
out_path = Path("v102_oof_metrics.json")
with open(out_path, "w") as f:
    json.dump(results, f, indent=4)
print(f"\nMetrics saved to: kaggle_submission/v102_oof_metrics.json")
print(f"Train embeddings saved to: kaggle_submission/train_biobert_pca.csv")
print("\nDone.")
