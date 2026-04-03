import pandas as pd
from pathlib import Path

RAW = Path(__file__).parent.parent / 'dataset' / 'raw'
OUT = Path(__file__).parent.parent / 'dataset' / 'processed' / 'schema_preview.csv'

train = pd.read_csv(RAW / 'train.csv')
history = pd.read_csv(RAW / 'patient_history.csv')
complaints = pd.read_csv(RAW / 'chief_complaints.csv')

# Drop duplicate columns before merging (only keep new cols from right side)
history = history.drop(columns=[c for c in history.columns if c in train.columns and c != 'patient_id'])
complaints = complaints.drop(columns=[c for c in complaints.columns if c in train.columns and c != 'patient_id'])
complaints = complaints.drop(columns=[c for c in complaints.columns if c in history.columns and c != 'patient_id'])

merged = train.merge(history, on='patient_id', how='left').merge(complaints, on='patient_id', how='left')

# Build: row 0 = datatypes, rows 1-10 = first 10 data rows
dtype_row = pd.DataFrame([merged.dtypes.astype(str).to_dict()])
data_rows = merged.head(10)

preview = pd.concat([dtype_row, data_rows], ignore_index=True)
preview.to_csv(OUT, index=False)

print(f'Saved schema_preview.csv → {OUT}')
print(f'Shape: {merged.shape[1]} columns, 11 rows (1 dtype + 10 data)')
