import json
import logging
import os
import re

import ollama
from groq import Groq

log = logging.getLogger(__name__)

_OLLAMA_MODEL = "llama3.2"
_GROQ_MODEL = "llama-3.2-11b-text-preview"
_CONFIDENCE_THRESHOLD = 0.75

_FIELD_DESCRIPTIONS = {
    "mental_status_triage": "patient's mental/consciousness status — one of: alert, confused, drowsy, agitated, unresponsive",
    "chief_complaint_raw": "main reason for visiting, in patient's own words",
    "pain_location": "location of pain — one of: abdomen, back, chest, extremity, head, multiple, none, pelvis, unknown",
    "pain_score": "pain intensity 0-10 integer, or null if unconscious/unknown",
    "arrival_mode": "how patient arrived — one of: ambulance, brought_by_family, helicopter, police, transfer, walk-in",
    "transport_origin": "where patient came from — one of: home, nursing_home, other_hospital, outdoor, public_space, school, workplace",
    "heart_rate": "heart rate in beats per minute (integer 20-260)",
    "respiratory_rate": "respiratory rate in breaths per minute (integer 0-80)",
    "temperature_c": "body temperature in Celsius (float 30.0-45.0)",
    "spo2": "blood oxygen saturation percentage (float 0-100)",
    "systolic_bp": "systolic blood pressure in mmHg (float 40-300)",
    "diastolic_bp": "diastolic blood pressure in mmHg (float 20-200)",
    "gcs_total": "Glasgow Coma Scale total score (integer 3-15)",
}

_EXTRACTION_SYSTEM_PROMPT = """You are a JSON data extraction API for a hospital triage system.
You MUST respond with ONLY a valid JSON object. No code. No explanation. No markdown. No prose.

For each field listed below that is mentioned in the patient's message, output:
  "field_name": {{"value": <extracted value>, "confidence": <float 0.0-1.0>}}

If a field is not mentioned at all, omit it entirely.
If the patient says they don't know, output {{"value": null, "confidence": 1.0}}.
For enum fields, map to the closest allowed value listed in the description.

Example output format:
{{
  "pain_score": {{"value": 8, "confidence": 0.98}},
  "arrival_mode": {{"value": "ambulance", "confidence": 0.99}}
}}

Fields to extract:
{field_descriptions}"""

_NORMALIZATION_SYSTEM_PROMPT = """You are a clinical documentation API.
Rewrite the input as a terse nurse-written phrase. Maximum 6 words. English only. No subject ("Patient reports...").
Example: "chest pain since morning" or "shortness of breath, acute onset".
Respond with ONLY the phrase. No explanation, no quotes."""


def extract_fields(utterance: str, fields_needed: list[str]) -> dict[str, dict]:
    field_descriptions = "\n".join(
        f"- {f}: {_FIELD_DESCRIPTIONS.get(f, f)}"
        for f in fields_needed
        if f in _FIELD_DESCRIPTIONS
    )
    system_prompt = _EXTRACTION_SYSTEM_PROMPT.format(field_descriptions=field_descriptions)

    raw = _call_llm(system_prompt=system_prompt, user_message=utterance)
    return _parse_extraction_response(raw, fields_needed)


def normalize_chief_complaint(raw_complaint: str) -> str | None:
    result = _call_llm(
        system_prompt=_NORMALIZATION_SYSTEM_PROMPT,
        user_message=raw_complaint,
    )
    if not result:
        return None
    normalized = result.strip().strip('"').strip("'")
    return normalized if normalized else None


def _call_llm(system_prompt: str, user_message: str) -> str | None:
    try:
        response = ollama.chat(
            model=_OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            options={"num_gpu": 99},  # use all available GPU layers
            keep_alive=0,             # unload model from VRAM immediately after response
        )
        return response["message"]["content"]
    except Exception as ollama_exc:
        log.warning("Ollama unavailable (%s), falling back to Groq.", ollama_exc)
        return _call_groq(system_prompt=system_prompt, user_message=user_message)


def _call_groq(system_prompt: str, user_message: str) -> str | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        log.error("Groq fallback requested but GROQ_API_KEY is not set.")
        return None
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=_GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content
    except Exception as groq_exc:
        log.error("Groq fallback also failed: %s", groq_exc)
        return None


def _parse_extraction_response(raw: str | None, fields_needed: list[str]) -> dict[str, dict]:
    if not raw:
        return {}
    try:
        json_str = _extract_json(raw)
        parsed = json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        log.warning("LLM returned non-JSON extraction response: %s", raw[:200])
        return {}

    result = {}
    for field in fields_needed:
        if field not in parsed:
            continue
        entry = parsed[field]
        if not isinstance(entry, dict):
            continue
        value = entry.get("value")
        confidence = float(entry.get("confidence", 0.0))
        result[field] = {"value": value, "confidence": confidence}

    return result


def _extract_json(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return text
