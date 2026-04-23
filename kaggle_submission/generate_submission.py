"""
generate_submission.py
======================
Generates the Kaggle submission CSV using the trained v1.0.2 models.

What this script does:
  1. Loads test.csv + chief_complaints.csv
  2. Runs BioBERT on test chief complaints (same way as training)
  3. Loads the existing pca_v1.0.2.pkl and transforms embeddings to 10 dims
  4. Loads all 5 trained fold models and averages their predictions
  5. Saves submission.csv

Run from the ml/ directory:
  cd /home/saumy/Documents/ML-Project---TRIAGEGEIST/ml
  python generate_submission.py
"""

import pandas as pd
import numpy as np
import joblib
import torch
import json
from pathlib import Path
from transformers import AutoTokenizer, AutoModel
from catboost import CatBoostClassifier, Pool
from tqdm.auto import tqdm

ML = Path(".")

# ── Config ────────────────────────────────────────────────────────────────────
BERT_MODEL  = "dmis-lab/biobert-v1.1"
BATCH_SIZE  = 64
MAX_LEN     = 64
N_FOLDS     = 5
RANDOM_SEED = 42

CAT_FEATURES = [
    'arrival_mode', 'age_group', 'sex', 'pain_location',
    'mental_status_triage', 'chief_complaint_system'
]

# Columns dropped during training (must drop same ones from test)
DROP_COLS = [
    'patient_id', 'site_id', 'triage_nurse_id',
    'arrival_hour', 'arrival_day', 'arrival_month', 'arrival_season', 'shift',
    'language', 'transport_origin', 'insurance_type',
    'disposition', 'ed_los_hours'  # not in test, but safe to ignore
]

# ── Step 1: Load test data ────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1 — Loading test data")
print("=" * 60)

test_raw = pd.read_csv(ML / "dataset/raw/test.csv")
cc_df    = pd.read_csv(ML / "dataset/raw/chief_complaints.csv")
hist_df  = pd.read_csv(ML / "dataset/raw/patient_history.csv")

print(f"Test rows:             {len(test_raw):,}")
print(f"Chief complaints rows: {len(cc_df):,}")
print(f"Patient history rows:  {len(hist_df):,}")

# Save patient_ids for submission before dropping
test_patient_ids = test_raw['patient_id'].copy()

# Merge history and complaints
test = test_raw.merge(hist_df, on='patient_id', how='left')
test = test.merge(cc_df[['patient_id', 'chief_complaint_raw']], on='patient_id', how='left')

print(f"After merge: {test.shape}")

# ── Step 2: Same preprocessing as training ────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 2 — Preprocessing (matching training pipeline)")
print("=" * 60)

# Drop same columns as training
drop_existing = [c for c in DROP_COLS if c in test.columns]
test = test.drop(columns=drop_existing)

# Fill text
test['chief_complaint_raw'] = test['chief_complaint_raw'].fillna("No Data")

# Fill categoricals
cat_cols = test.select_dtypes(include=['object', 'string']).columns
test[cat_cols] = test[cat_cols].fillna("Unknown")

print(f"Shape after preprocessing: {test.shape}")
print(f"Columns: {list(test.columns)}")

# ── Step 3: BioBERT embeddings on test complaints ─────────────────────────────
print("\n" + "=" * 60)
print("STEP 3 — BioBERT embedding extraction")
print("=" * 60)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Device: {device}")

print(f"Loading {BERT_MODEL}...")
tokenizer  = AutoTokenizer.from_pretrained(BERT_MODEL)
bert_model = AutoModel.from_pretrained(BERT_MODEL).to(device)
bert_model.eval()

texts = test['chief_complaint_raw'].tolist()
all_embeddings = []

print(f"Embedding {len(texts):,} test complaints...")
with torch.no_grad():
    for i in tqdm(range(0, len(texts), BATCH_SIZE)):
        batch = texts[i : i + BATCH_SIZE]
        encoded = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=MAX_LEN,
            return_tensors='pt'
        ).to(device)
        outputs = bert_model(**encoded)
        cls_embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        all_embeddings.append(cls_embeddings)

raw_embeddings = np.vstack(all_embeddings)
print(f"Raw embedding matrix: {raw_embeddings.shape}")  # (20000, 768)

# Free GPU memory
del bert_model
if torch.cuda.is_available():
    torch.cuda.empty_cache()
print("GPU memory released.")

# ── Step 4: Apply existing PCA ────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 4 — Applying pca_v1.0.2.pkl (768 → 10 dims)")
print("=" * 60)

pca = joblib.load(ML / "models/v1.0.2/pca_v1.0.2.pkl")
print(f"PCA loaded: {pca.n_features_in_} → {pca.n_components_} components")
print(f"Variance retained: {pca.explained_variance_ratio_.sum() * 100:.1f}%")

compressed = pca.transform(raw_embeddings)  # (20000, 10)
print(f"Compressed: {compressed.shape}")

pca_cols = [f"biobert_pca_{i+1}" for i in range(pca.n_components_)]
pca_df   = pd.DataFrame(compressed, columns=pca_cols, index=test.index)

# Build final feature matrix — same structure as training
X_test = pd.concat([
    test.drop(columns=['chief_complaint_raw', 'patient_id'], errors='ignore'),
    pca_df
], axis=1)

print(f"Final feature matrix: {X_test.shape}")

# Get cat feature indices for CatBoost Pool
cat_indices = [i for i, c in enumerate(X_test.columns) if c in CAT_FEATURES]
print(f"Categorical feature indices ({len(cat_indices)}): {[X_test.columns[i] for i in cat_indices]}")

# ── Step 5: Load all 5 fold models and ensemble ───────────────────────────────
print("\n" + "=" * 60)
print("STEP 5 — Ensemble inference (5 fold models)")
print("=" * 60)

test_pool  = Pool(X_test, cat_features=cat_indices)
test_probs = np.zeros((len(X_test), 5))

for fold in range(1, N_FOLDS + 1):
    model_path = ML / f"models/v1.0.2/model_v1.0.2_fold_{fold}.cbm"
    model = CatBoostClassifier()
    model.load_model(str(model_path))
    probs = model.predict_proba(test_pool)
    test_probs += probs / N_FOLDS
    print(f"  Fold {fold} loaded — prediction distribution: {np.bincount(np.argmax(probs, axis=1) + 1, minlength=6)[1:]}")

# Final predictions — argmax of averaged probabilities
test_preds = np.argmax(test_probs, axis=1) + 1  # back to 1-indexed ESI

# ── Step 6: Save submission ───────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 6 — Saving submission.csv")
print("=" * 60)

submission = pd.DataFrame({
    'patient_id':    test_patient_ids,
    'triage_acuity': test_preds
})

print("Submission acuity distribution:")
print(submission['triage_acuity'].value_counts().sort_index())

out_path = ML / "submission.csv"
submission.to_csv(out_path, index=False)
print(f"\nSaved to: {out_path}")
print(f"Total rows: {len(submission):,}")
print(submission.head())
print("\nDone.")
