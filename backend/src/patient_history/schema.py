from pydantic import BaseModel, ConfigDict


class PatientHistoryDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    patient_id: str
    hx_hypertension: bool | None = None
    hx_diabetes_type2: bool | None = None
    hx_diabetes_type1: bool | None = None
    hx_asthma: bool | None = None
    hx_copd: bool | None = None
    hx_heart_failure: bool | None = None
    hx_atrial_fibrillation: bool | None = None
    hx_ckd: bool | None = None
    hx_liver_disease: bool | None = None
    hx_malignancy: bool | None = None
    hx_obesity: bool | None = None
    hx_depression: bool | None = None
    hx_anxiety: bool | None = None
    hx_dementia: bool | None = None
    hx_epilepsy: bool | None = None
    hx_hypothyroidism: bool | None = None
    hx_hyperthyroidism: bool | None = None
    hx_hiv: bool | None = None
    hx_coagulopathy: bool | None = None
    hx_immunosuppressed: bool | None = None
    hx_pregnant: bool | None = None
    hx_substance_use_disorder: bool | None = None
    hx_coronary_artery_disease: bool | None = None
    hx_stroke_prior: bool | None = None
    hx_peripheral_vascular_disease: bool | None = None
