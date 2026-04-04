from fastapi import APIRouter

from src.triage.schema import TriageResponse, TriageSubmission
from src.triage.service import get_form_options, submit_triage

router = APIRouter(tags=["triage"])


@router.get("/triage/options")
def triage_options():
    return get_form_options()


@router.post("/predict", response_model=TriageResponse)
def predict(submission: TriageSubmission):
    return submit_triage(submission)
