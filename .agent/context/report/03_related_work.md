# II. Related Work

## A. Triage Acuity Prediction
Supervised machine learning for ESI prediction has attracted growing research attention since large curated ED datasets became available. Gradient-boosted tree ensembles applied to MIMIC-IV-ED data consistently outperform logistic regression and random forests on macro-averaged F1 metrics [2]. The tabular structure of clinical intake data, with its mixture of continuous vitals, ordinal scores, and nominal categories, particularly favours tree-based models over deep neural networks when training data is in the tens of thousands of records.

## B. CatBoost for Clinical Data
CatBoost [3] introduces ordered boosting—a permutation-driven technique that eliminates target leakage during categorical feature encoding. This property is especially valuable in healthcare settings where categorical variables (arrival mode, pain location, mental status at triage) are numerous and label encoding risks inflating apparent accuracy during training. CatBoost's native handling of missing values as NaN is additionally important in clinical contexts, where incomplete vitals are routine rather than exceptional.

## C. Biomedical Language Models
BioBERT [4] and its domain-specific variant PubMedBERT [5] pre-train transformer encoders exclusively on biomedical corpora, producing contextual embeddings that outperform general-domain BERT on clinical NLP tasks including named entity recognition, relation extraction, and symptom classification. Free-text chief complaints, which constitute the primary unstructured data element in ED triage forms, benefit directly from this domain adaptation.

## D. Voice-Driven Clinical Intake
Automated speech recognition applied to clinical workflows has been commercialized for documentation (Nuance DAX, Suki AI), but its integration with downstream acuity prediction pipelines remains underexplored. TriageGeist bridges this gap by coupling Vapi-managed voice I/O with an LLM assistant that extracts structured clinical fields in real time and feeds them directly into the ML inference endpoint, without requiring a local GPU for speech or language processing.

## E. Multi-Model Inference Pipelines
Ensemble and cascaded model architectures are established in general ML literature but remain uncommon in clinical triage systems, which typically deploy a single monolithic classifier. TriageGeist's three-model pipeline—where a text classifier prepares a missing input for the primary model, and a fallback model handles data-sparse patients—reflects the real-world variability of ED intake data quality and is a novel design contribution in this domain.
