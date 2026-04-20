import logging
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from src.chatbot.llm import extract_fields, normalize_chief_complaint
from utils.fuzzy import fuzzy_match_patients

log = logging.getLogger(__name__)

_COMPLAINT_FIELDS_ORDERED = [
    "mental_status_triage",
    "chief_complaint_raw",
    "pain_location",
    "pain_score",
    "arrival_mode",
    "transport_origin",
]

_REQUIRED_COMPLAINT_FIELDS = {
    "mental_status_triage",
    "chief_complaint_raw",
    "pain_location",
    "pain_score",
    "arrival_mode",
}

_VITALS_BATCH_1 = ["heart_rate", "respiratory_rate", "temperature_c"]
_VITALS_BATCH_2 = ["spo2", "gcs_total"]
_VITALS_BATCH_3 = ["systolic_bp", "diastolic_bp"]
_VITALS_BASIC = ["heart_rate", "temperature_c"]


class ChatbotState(TypedDict):
    session_id: str
    user_role: str | None
    patient_id: str | None
    current_step: str
    collected_fields: dict
    missing_fields: list[str]
    low_confidence_fields: list[str]
    conversation_raw: Annotated[list, add_messages]
    vitals_taken: bool | None
    pending_confirmation: str | None
    verify_candidates: list[dict]
    vitals_batch: int


def _bot_message(text: str) -> dict:
    from datetime import datetime, UTC
    return {"role": "bot", "text": text, "ts": datetime.now(UTC).isoformat()}


def _all_required_collected(state: ChatbotState) -> bool:
    fields = state["collected_fields"]
    return all(
        f in fields and fields[f] is not None
        for f in _REQUIRED_COMPLAINT_FIELDS
        if f != "pain_score" or fields.get("mental_status_triage") != "unresponsive"
    )


# ── Node: role detection ──────────────────────────────────────────────────────

def node_role_detection(state: ChatbotState, utterance: str) -> dict:
    utterance_lower = utterance.lower()

    attendant_signals = [
        "my father", "my mother", "my son", "my daughter", "my friend",
        "my husband", "my wife", "my brother", "my sister", "my parent",
        "he is", "she is", "they are", "not responding", "unconscious",
    ]
    role = "patient"
    for signal in attendant_signals:
        if signal in utterance_lower:
            role = "attendant"
            break

    if role == "patient":
        extracted = extract_fields(utterance, ["mental_status_triage"])
        if extracted.get("mental_status_triage", {}).get("value") == "unresponsive":
            role = "attendant"

    pronoun = "the patient's" if role == "attendant" else "your"
    reply = (
        f"I'll note you as {'an attendant' if role == 'attendant' else 'the patient'}. "
        f"Let's find {pronoun} record. Please tell me {pronoun} name and age, "
        f"or {pronoun} patient ID if you have it."
    )

    return {
        "user_role": role,
        "current_step": "verification",
        "conversation_raw": [_bot_message(reply)],
    }


# ── Node: patient verification ────────────────────────────────────────────────

def node_verification(state: ChatbotState, utterance: str) -> dict:
    extracted = extract_fields(utterance, ["patient_id", "name", "age"])

    patient_id = extracted.get("patient_id", {}).get("value")
    name = extracted.get("name", {}).get("value") or utterance.strip()
    age_raw = extracted.get("age", {}).get("value")
    age = int(age_raw) if age_raw is not None else None

    candidates = fuzzy_match_patients(name=name, age=age)

    if not candidates:
        reply = (
            "I couldn't find a matching record. "
            "Please approach the front desk to register as a new patient."
        )
        return {
            "current_step": "verification_failed",
            "conversation_raw": [_bot_message(reply)],
            "verify_candidates": [],
        }

    if len(candidates) == 1 and candidates[0]["combined_score"] >= 95:
        patient = candidates[0]
        reply = (
            f"Found: {patient['name']}, age {patient['age']}. "
            "Is that correct? Say yes to confirm or no to try again."
        )
        return {
            "current_step": "verification_confirm",
            "verify_candidates": candidates,
            "conversation_raw": [_bot_message(reply)],
        }

    options = "\n".join(
        f"{i+1}. {c['name']}, age {c['age']}"
        for i, c in enumerate(candidates[:3])
    )
    reply = f"I found a few possible matches:\n{options}\nWhich one is correct? Say the number."
    return {
        "current_step": "verification_select",
        "verify_candidates": candidates[:3],
        "conversation_raw": [_bot_message(reply)],
    }


def node_verification_confirm(state: ChatbotState, utterance: str) -> dict:
    if any(w in utterance.lower() for w in ["yes", "correct", "that's right", "yep", "yeah"]):
        patient = state["verify_candidates"][0]
        reply = (
            f"Great. Now, is {patient['name']} alert? Confused? Drowsy? Or not responding?"
        )
        return {
            "patient_id": patient["patient_id"],
            "current_step": "complaint",
            "missing_fields": list(_COMPLAINT_FIELDS_ORDERED),
            "conversation_raw": [_bot_message(reply)],
        }

    reply = "No problem. Please tell me the name and age again."
    return {
        "current_step": "verification",
        "verify_candidates": [],
        "conversation_raw": [_bot_message(reply)],
    }


def node_verification_select(state: ChatbotState, utterance: str) -> dict:
    candidates = state["verify_candidates"]
    selected = None

    for i, candidate in enumerate(candidates):
        if str(i + 1) in utterance:
            selected = candidate
            break
        if candidate["name"].lower() in utterance.lower():
            selected = candidate
            break

    if not selected:
        options = "\n".join(
            f"{i+1}. {c['name']}, age {c['age']}"
            for i, c in enumerate(candidates)
        )
        reply = f"Please say the number of the correct patient:\n{options}"
        return {"conversation_raw": [_bot_message(reply)]}

    reply = (
        f"Got it — {selected['name']}, age {selected['age']}. "
        f"Is that correct? Say yes or no."
    )
    return {
        "current_step": "verification_confirm",
        "verify_candidates": [selected],
        "conversation_raw": [_bot_message(reply)],
    }


# ── Node: complaint collection ────────────────────────────────────────────────

def node_complaint(state: ChatbotState, utterance: str) -> dict:
    missing = state.get("missing_fields", list(_COMPLAINT_FIELDS_ORDERED))
    collected = dict(state.get("collected_fields", {}))
    low_confidence = list(state.get("low_confidence_fields", []))

    dont_know_signals = ["don't know", "dont know", "no idea", "not sure", "unknown", "skip"]
    is_dont_know = any(s in utterance.lower() for s in dont_know_signals)

    if low_confidence:
        field_to_confirm = low_confidence[0]
        if is_dont_know:
            collected[field_to_confirm] = None
        else:
            extracted = extract_fields(utterance, [field_to_confirm])
            entry = extracted.get(field_to_confirm, {})
            collected[field_to_confirm] = entry.get("value")
        low_confidence = low_confidence[1:]
    else:
        extractable = [f for f in missing if f in _COMPLAINT_FIELDS_ORDERED]
        if extractable:
            extracted = extract_fields(utterance, extractable)
            for field, entry in extracted.items():
                confidence = entry.get("confidence", 0.0)
                value = entry.get("value")
                if value is None or is_dont_know:
                    collected[field] = None
                elif confidence < 0.75:
                    low_confidence.append(field)
                    collected[field] = value
                else:
                    collected[field] = value

    missing = [f for f in _COMPLAINT_FIELDS_ORDERED if f not in collected]

    if low_confidence:
        field = low_confidence[0]
        reply = f"Just to confirm — I heard '{collected.get(field)}' for {field.replace('_', ' ')}. Is that correct?"
        return {
            "collected_fields": collected,
            "missing_fields": missing,
            "low_confidence_fields": low_confidence,
            "conversation_raw": [_bot_message(reply)],
        }

    if _all_required_collected({"collected_fields": collected, **state}):
        if "chief_complaint_raw" in collected and collected["chief_complaint_raw"]:
            normalized = normalize_chief_complaint(collected["chief_complaint_raw"])
            if normalized:
                collected["chief_complaint_normalized"] = normalized

        reply = "Thank you. Now, have the patient's vitals been taken by a nurse? Say yes or no."
        return {
            "collected_fields": collected,
            "missing_fields": [],
            "low_confidence_fields": [],
            "current_step": "vitals",
            "conversation_raw": [_bot_message(reply)],
        }

    next_field = next((f for f in _COMPLAINT_FIELDS_ORDERED if f not in collected), None)
    reply = _question_for_field(next_field, state.get("user_role", "patient"))
    return {
        "collected_fields": collected,
        "missing_fields": missing,
        "low_confidence_fields": low_confidence,
        "conversation_raw": [_bot_message(reply)],
    }


def _question_for_field(field: str | None, user_role: str) -> str:
    p = "the patient's" if user_role == "attendant" else "your"
    questions = {
        "mental_status_triage": f"Is {p} patient alert? Confused? Drowsy? Or not responding?",
        "chief_complaint_raw": f"What is {p} main problem — what brought you in today?",
        "pain_location": f"Where exactly is {p} pain or discomfort?",
        "pain_score": f"On a scale of 0 to 10, how bad is {p} pain?",
        "arrival_mode": f"How did {p} patient get to the hospital?",
        "transport_origin": f"Where were you coming from — home, workplace, another hospital?",
    }
    return questions.get(field, "Could you tell me more?")


# ── Node: vitals ──────────────────────────────────────────────────────────────

def node_vitals(state: ChatbotState, utterance: str) -> dict:
    collected = dict(state.get("collected_fields", {}))
    batch = state.get("vitals_batch", 0)
    vitals_taken = state.get("vitals_taken")

    dont_know_signals = ["don't know", "dont know", "no idea", "not sure", "skip", "no"]

    if vitals_taken is None:
        if any(w in utterance.lower() for w in ["yes", "yeah", "yep", "taken", "done"]):
            reply = "Please give me the heart rate, respiratory rate, and temperature."
            return {
                "vitals_taken": True,
                "vitals_batch": 1,
                "conversation_raw": [_bot_message(reply)],
            }
        else:
            extractable = _VITALS_BASIC
            extracted = extract_fields(utterance, extractable)
            for field, entry in extracted.items():
                if entry.get("value") is not None:
                    collected[field] = entry["value"]
            reply = "Noted — vitals will be taken by a nurse. Let me confirm what we have so far."
            return {
                "vitals_taken": False,
                "collected_fields": collected,
                "current_step": "confirm",
                "conversation_raw": [_bot_message(reply)],
            }

    is_skip = any(s in utterance.lower() for s in dont_know_signals)

    if batch == 1:
        if not is_skip:
            extracted = extract_fields(utterance, _VITALS_BATCH_1)
            for field, entry in extracted.items():
                if entry.get("value") is not None:
                    collected[field] = entry["value"]
        reply = "Got it. Do you have the SpO2 reading or the GCS score?"
        return {
            "collected_fields": collected,
            "vitals_batch": 2,
            "conversation_raw": [_bot_message(reply)],
        }

    if batch == 2:
        if not is_skip:
            extracted = extract_fields(utterance, _VITALS_BATCH_2)
            for field, entry in extracted.items():
                if entry.get("value") is not None:
                    collected[field] = entry["value"]
        reply = "Do you have the blood pressure readings — systolic and diastolic?"
        return {
            "collected_fields": collected,
            "vitals_batch": 3,
            "conversation_raw": [_bot_message(reply)],
        }

    if batch == 3:
        if not is_skip:
            extracted = extract_fields(utterance, _VITALS_BATCH_3)
            bp_values = {
                f: extracted[f]["value"]
                for f in _VITALS_BATCH_3
                if f in extracted and extracted[f].get("value") is not None
            }
            if len(bp_values) == 2:
                collected.update(bp_values)

        fields_missing = _compute_missing_vitals(collected)
        reply = "Thank you. Let me show you everything we've collected before submitting."
        return {
            "collected_fields": collected,
            "missing_fields": fields_missing,
            "current_step": "confirm",
            "conversation_raw": [_bot_message(reply)],
        }

    return {"current_step": "confirm"}


def _compute_missing_vitals(collected: dict) -> list[str]:
    all_vitals = _VITALS_BATCH_1 + _VITALS_BATCH_2 + _VITALS_BATCH_3
    return [f for f in all_vitals if collected.get(f) is None]


# ── Node: confirm ─────────────────────────────────────────────────────────────

def node_confirm(state: ChatbotState, utterance: str) -> dict:
    if any(w in utterance.lower() for w in ["submit", "yes", "correct", "confirm", "send", "ok", "okay"]):
        return {"current_step": "submit"}

    extracted = extract_fields(utterance, list(_FIELD_DESCRIPTIONS.keys()))
    if extracted:
        collected = dict(state.get("collected_fields", {}))
        for field, entry in extracted.items():
            if entry.get("value") is not None:
                collected[field] = entry["value"]
        reply = "Updated. Should I submit now?"
        return {
            "collected_fields": collected,
            "conversation_raw": [_bot_message(reply)],
        }

    reply = "Say 'submit' to confirm, or tell me what you'd like to change."
    return {"conversation_raw": [_bot_message(reply)]}


# ── Graph assembly ────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(ChatbotState)

    graph.add_node("role_detection", node_role_detection)
    graph.add_node("verification", node_verification)
    graph.add_node("verification_confirm", node_verification_confirm)
    graph.add_node("verification_select", node_verification_select)
    graph.add_node("complaint", node_complaint)
    graph.add_node("vitals", node_vitals)
    graph.add_node("confirm", node_confirm)

    graph.set_entry_point("role_detection")

    graph.add_conditional_edges("role_detection", lambda s: s["current_step"], {
        "verification": "verification",
    })
    graph.add_conditional_edges("verification", lambda s: s["current_step"], {
        "verification_confirm": "verification_confirm",
        "verification_select": "verification_select",
        "verification_failed": END,
    })
    graph.add_conditional_edges("verification_confirm", lambda s: s["current_step"], {
        "complaint": "complaint",
        "verification": "verification",
    })
    graph.add_conditional_edges("verification_select", lambda s: s["current_step"], {
        "verification_confirm": "verification_confirm",
        "verification_select": "verification_select",
    })
    graph.add_conditional_edges("complaint", lambda s: s["current_step"], {
        "complaint": "complaint",
        "vitals": "vitals",
    })
    graph.add_conditional_edges("vitals", lambda s: s["current_step"], {
        "vitals": "vitals",
        "confirm": "confirm",
    })
    graph.add_conditional_edges("confirm", lambda s: s["current_step"], {
        "confirm": "confirm",
        "submit": END,
    })

    return graph.compile()


def make_initial_state(session_id: str) -> ChatbotState:
    return ChatbotState(
        session_id=session_id,
        user_role=None,
        patient_id=None,
        current_step="role_detection",
        collected_fields={},
        missing_fields=list(_COMPLAINT_FIELDS_ORDERED),
        low_confidence_fields=[],
        conversation_raw=[],
        vitals_taken=None,
        pending_confirmation=None,
        verify_candidates=[],
        vitals_batch=0,
    )
