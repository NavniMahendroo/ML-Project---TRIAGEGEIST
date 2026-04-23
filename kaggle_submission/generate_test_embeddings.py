"""
generate_test_embeddings.py
============================
Generates test_biobert_pca.csv (20,000 rows x 10 cols) for Kaggle dataset upload.

Run from kaggle_submission/ directory:
  cd /home/saumy/Documents/ML-Project---TRIAGEGEIST/kaggle_submission
  python generate_test_embeddings.py

Output: kaggle_submission/test_biobert_pca.csv
"""

import pandas as pd
import numpy as np
import joblib
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModel
from tqdm.auto import tqdm

ML = Path("../ml")

BERT_MODEL = "dmis-lab/biobert-v1.1"
BATCH_SIZE = 64
MAX_LEN    = 64

out_csv = Path("test_biobert_pca.csv")

if out_csv.exists():
    print(f"test_biobert_pca.csv already exists ({out_csv.stat().st_size // 1024}KB) — nothing to do.")
    import sys; sys.exit(0)

# ── Step 1: Load test data ────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1 — Loading test data")
print("=" * 60)

test_raw = pd.read_csv(ML / "dataset/raw/test.csv")
cc_df    = pd.read_csv(ML / "dataset/raw/chief_complaints.csv")

test = test_raw.merge(cc_df[['patient_id', 'chief_complaint_raw']], on='patient_id', how='left')
test['chief_complaint_raw'] = test['chief_complaint_raw'].fillna("No Data")
texts = test['chief_complaint_raw'].tolist()
print(f"Test complaints to embed: {len(texts):,}")

# ── Step 2: BioBERT embedding ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 2 — BioBERT embedding extraction")
print("=" * 60)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Device: {device}")

tokenizer  = AutoTokenizer.from_pretrained(BERT_MODEL)
bert_model = AutoModel.from_pretrained(BERT_MODEL).to(device)
bert_model.eval()

all_embeddings = []
print(f"Embedding {len(texts):,} complaints...")
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

raw_emb = np.vstack(all_embeddings)
print(f"Raw embeddings: {raw_emb.shape}")

del bert_model
if torch.cuda.is_available():
    torch.cuda.empty_cache()
print("GPU memory released.")

# ── Step 3: Apply pca_v1.0.2.pkl ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 3 — Applying pca_v1.0.2.pkl (768 → 10 dims)")
print("=" * 60)

pca = joblib.load(ML / "models/v1.0.2/pca_v1.0.2.pkl")
print(f"PCA: {pca.n_features_in_} → {pca.n_components_} dims")
print(f"Variance retained: {pca.explained_variance_ratio_.sum()*100:.1f}%")

test_pca = pca.transform(raw_emb)
pca_cols = [f"biobert_pca_{i+1}" for i in range(pca.n_components_)]
pca_df   = pd.DataFrame(test_pca, columns=pca_cols)

pca_df.to_csv(out_csv, index=False)
print(f"\nSaved: kaggle_submission/test_biobert_pca.csv  {pca_df.shape}")
print(f"File size: {out_csv.stat().st_size // 1024}KB")
print("\nDone. Upload this file to the triagegeist-biobert Kaggle dataset.")
