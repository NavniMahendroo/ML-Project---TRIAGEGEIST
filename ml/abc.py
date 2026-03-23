import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import torch
import shap
from tqdm import tqdm
from catboost import CatBoostClassifier, Pool
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from transformers import AutoTokenizer, AutoModel

train = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')
print(train.shape)
train.head()

print(test.shape)
test.head()

train_columns_list = list(train.columns)
test_columns_list = list(test.columns)

print('train columns', train_columns_list)
print('test_columns ', test_columns_list)


target = 'triage_acuity'
train_cols = set(train.columns)
test_cols = set(test.columns)

leakage_candidates = list(train_cols - test_cols - {target})

print(f"--- Data Integrity Check ---")
print(f"Potential Leakage Columns detected: {leakage_candidates}")

leakage_candidates

leakage_analysis = train[leakage_candidates + [target]].copy()
leakage_analysis.tail(10)

le = LabelEncoder()

leakage_analysis["disposition_num"] = le.fit_transform(leakage_analysis["disposition"])
leakage_analysis.drop('disposition', axis=1).corr()

cols_to_drop = leakage_candidates

print(f"\nAction: Dropping {cols_to_drop} to prevent Target Leakage.")
train_cleaned = train.drop(columns=cols_to_drop)
train_cleaned.head()

print(f"Cleaned Train shape: {train_cleaned.shape}")
print(f"Test shape: {test.shape}")
print(f"Fatures are now aligned (excluding target).")

plt.figure(figsize=(10, 6))
sns.boxplot(x=target, y='ed_los_hours', data=train)
plt.title('Leakage Evidence: ED Length of Stay vs Triage Acuity')
plt.xlabel('Triage Acuity (1: Most Urgent, 5: Least Urgent)')
plt.ylabel('ED LOS (Hours)')
plt.savefig('leakage_evidence.png')

patient_history = pd.read_csv('patient_history.csv')
chief_complaints = pd.read_csv('chief_complaints.csv')

patient_history.head()

chief_complaints.head()
le = LabelEncoder()

chief_complaints['chief_complaint_system_number'] = le.fit_transform(chief_complaints['chief_complaint_system'])
chief_complaints

train_merged = train.merge(patient_history, on='patient_id', how='left')
test_merged = test.merge(patient_history, on='patient_id', how='left')

complaints_subset = chief_complaints[['patient_id', 'chief_complaint_raw']]
train_merged = train_merged.merge(complaints_subset, on='patient_id', how='left')
test_merged = test_merged.merge(complaints_subset, on='patient_id', how='left')

leakage_cols = ['ed_los_hours', 'disposition']
train_merged = train_merged.drop(columns=leakage_cols)

print(f"Final number of columns in training data: {len(train_merged.columns)}")
print(f"Examples of added patient history: {patient_history.columns[1:5].tolist()}")

train_merged.head()

model_name = "dmis-lab/biobert-v1.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)


def get_bert_embeddings(text_list, batch_size=32):
    model.eval()
    all_embeddings = []

    for i in tqdm(range(0, len(text_list), batch_size)):
        batch_texts = text_list[i:i + batch_size]
        inputs = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=64,
            return_tensors="pt",
        ).to(device)

        with torch.no_grad():
            outputs = model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
            all_embeddings.append(embeddings)

    return np.vstack(all_embeddings)


texts = train_merged['chief_complaint_raw'].fillna("No Data").to_list()
bert_features = get_bert_embeddings(texts)


from sklearn.decomposition import PCA

pca = PCA(n_components=10)
bert_pca = pca.fit_transform(bert_features)

bert_pca

bert_cols = [f'bert_pca_{i}' for i in range(10)]
print(bert_cols)
df_bert = pd.DataFrame(bert_pca, columns=bert_cols)
train_merged = pd.concat([train_merged, df_bert], axis=1)

train_merged.head()

train = train_merged

# train = pd.concat([train, bert_df], axis=1)
train.head()

drop_cols = ['patient_id', 'triage_nurse_id', 'chief_complaint_raw', target]

X = train.drop(columns=drop_cols)
y = train[target]

X.columns.values

cat_features = X.select_dtypes(include=['object']).columns.tolist()
cat_features

X[cat_features]

for col in X.columns:
    print(col)


kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = []
models = []

print("\nStarting Cross-Validation...")
for fold, (train_idx, val_idx) in enumerate(kf.split(X, y)):
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

    train_pool = Pool(X_train, y_train, cat_features=cat_features)
    val_pool = Pool(X_val, y_val, cat_features=cat_features)

    model = CatBoostClassifier(
        iterations=10000,
        learning_rate=0.05,
        depth=6,
        loss_function='MultiClass',
        early_stopping_rounds=50,
        verbose=100,
        random_seed=42,
        task_type="GPU" if torch.cuda.is_available() else "CPU",
    )

    model.fit(train_pool, eval_set=val_pool)

    preds = model.predict(X_val)
    score = accuracy_score(y_val, preds)
    cv_scores.append(score)
    models.append(model)
    print(f"Fold {fold + 1} Accuracy: {score:.4f}")

print(f"\nMean CV Accuracy: {np.mean(cv_scores):.4f}")

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_val)
shap_values

shap_values.shape

X_val.shape

shap_values[:, :, 0].shape


shap.summary_plot(shap_values[:, :, 0], X_val)

# Re-run Cross-Validation to ensure variables are defined for SHAP explanation
kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = []
models = []

print("\nRe-running Cross-Validation to prepare for SHAP...")
for fold, (train_idx, val_idx) in enumerate(kf.split(X, y)):
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

    train_pool = Pool(X_train, y_train, cat_features=cat_features)
    val_pool = Pool(X_val, y_val, cat_features=cat_features)

    model = CatBoostClassifier(
        iterations=1000,
        learning_rate=0.05,
        depth=6,
        loss_function='MultiClass',
        early_stopping_rounds=50,
        verbose=0,  # Suppress verbose output for re-run
        random_seed=42,
        task_type="GPU" if torch.cuda.is_available() else "CPU",
    )

    model.fit(train_pool, eval_set=val_pool)

    preds = model.predict(X_val)
    score = accuracy_score(y_val, preds)
    cv_scores.append(score)
    models.append(model)

    # Save variables from the last fold for SHAP explanation
    if fold == kf.n_splits - 1:
        last_X_val = X_val
        last_preds = preds
        last_model = model
        last_target_names = ["1 (Resuscitation)", "2 (Emergent)", "3 (Urgent)", "4 (Less Urgent)", "5 (Non-Urgent)"]

print(f"Mean CV Accuracy from re-run: {np.mean(cv_scores):.4f}")

# Define the corrected explanation function
def explain_prediction_in_english(patient_index, X_data, shap_vals, preds, target_names):
    p_idx_raw = preds[patient_index]
    pred_class_idx_original = int(p_idx_raw.flatten()[0])  # Original class label (1 to 5)
    pred_class_idx_0_indexed = pred_class_idx_original - 1  # 0-indexed for shap_vals access (0 to 4)

    print(f"DEBUG: preds[patient_index]: {p_idx_raw}")
    print(f"DEBUG: pred_class_idx_original: {pred_class_idx_original}")
    print(f"DEBUG: pred_class_idx_0_indexed: {pred_class_idx_0_indexed}")
    print(f"DEBUG: shap_vals type: {type(shap_vals)}")
    if isinstance(shap_vals, np.ndarray):
        print(f"DEBUG: shap_vals shape: {shap_vals.shape}")
    elif isinstance(shap_vals, list):
        print(f"DEBUG: shap_vals (list) length: {len(shap_vals)}")
        if len(shap_vals) > 0:
            print(f"DEBUG: shap_vals[0] shape: {shap_vals[0].shape}")

    current_shap_vals = None
    if isinstance(shap_vals, np.ndarray) and shap_vals.ndim == 3:
        # Case 1: 3D numpy array (N_samples, N_features, N_classes)
        # Check if the class index is within bounds for axis 2
        if pred_class_idx_0_indexed < shap_vals.shape[2]:
            current_shap_vals = shap_vals[patient_index, :, pred_class_idx_0_indexed]
        else:
            raise IndexError(
                f"Class index {pred_class_idx_0_indexed} out of bounds for shap_vals axis 2 with size {shap_vals.shape[2]}"
            )
    elif isinstance(shap_vals, list) and len(shap_vals) > pred_class_idx_0_indexed:
        # Case 2: List of 2D numpy arrays (N_classes items, each (N_samples, N_features))
        current_shap_vals = shap_vals[pred_class_idx_0_indexed][patient_index]
    else:
        raise ValueError(
            f"Unexpected shape or type of shap_vals. Received type: {type(shap_vals)}, ndim: {getattr(shap_vals, 'ndim', 'N/A')}. Expected 3D numpy array or list of 2D arrays, with class index {pred_class_idx_0_indexed} accessible."
        )

    # Ensure current_shap_vals is not None before proceeding
    if current_shap_vals is None:
        raise ValueError("Failed to retrieve current_shap_vals for explanation.")

    # Check lengths before creating DataFrame
    if len(X_data.columns.tolist()) != len(current_shap_vals.flatten()):
        print(f"DEBUG: X_data columns length: {len(X_data.columns.tolist())}")
        print(f"DEBUG: current_shap_vals flattened length: {len(current_shap_vals.flatten())}")
        raise ValueError("Mismatch in feature names and SHAP values length.")

    feature_importance = pd.DataFrame(
        {
            'feature': X_data.columns.tolist(),
            'importance': current_shap_vals.flatten(),
        }
    )

    feature_importance_positive = feature_importance[feature_importance['importance'] > 0].sort_values(
        by='importance', ascending=False
    )
    feature_importance_negative = feature_importance[feature_importance['importance'] < 0].sort_values(
        by='importance', ascending=True
    )

    explanation = f"[Prediction Result] Predicted Class: {target_names[pred_class_idx_0_indexed]}\n"  # Adjust for 0-indexed target_names

    explanation += "\n[Main Factors Increasing Urgency]\n"
    if not feature_importance_positive.empty:
        for i, row in feature_importance_positive.head(3).iterrows():
            val = X_data.iloc[patient_index][row['feature']]
            explanation += f"- {row['feature']} (Value: {val}) -> Contribution: +{row['importance']:.3f}\n"
    else:
        explanation += "(None in particular)\n"

    explanation += "\n[Main Factors Decreasing Urgency (or keeping it normal)]\n"
    if not feature_importance_negative.empty:
        for i, row in feature_importance_negative.head(3).iterrows():
            val = X_data.iloc[patient_index][row['feature']]
            explanation += f"- {row['feature']} (Value: {val}) -> Contribution: {row['importance']:.3f}\n"
    else:
        explanation += "(None in particular)\n"

    return explanation


# Calculate SHAP values for the last fold's model and validation set
print("Calculating SHAP values...")
explainer = shap.TreeExplainer(last_model)
# CatBoost's predict() returns 1-5, but SHAP's shap_values for MultiClass will be 0-indexed for classes.
# So, when accessing shap_vals, we need to subtract 1 from the predicted class label.
shap_values = explainer.shap_values(last_X_val)

# Execute the explanation function for the first patient in the last validation set
print("\n--- Individual Patient Explanation ---")
print(explain_prediction_in_english(0, last_X_val, shap_values, last_preds, last_target_names))

# Generate Summary Plot (Beeswarm)
print("\n--- SHAP Summary Plot (Beeswarm) ---")
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, last_X_val, show=False)
plt.title("SHAP Beeswarm Plot")
plt.tight_layout()
plt.savefig('shap_summary_beeswarm.png')
plt.show()  # Display the plot in Colab

# Generate Summary Plot (Bar)
print("\n--- SHAP Summary Plot (Bar) ---")
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, last_X_val, plot_type="bar", show=False)
plt.title("SHAP Bar Plot of Feature Importance")
plt.tight_layout()
plt.savefig('shap_importance_bar.png')
plt.show()  # Display the plot in Colab
