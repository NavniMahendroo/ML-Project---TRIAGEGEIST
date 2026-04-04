import math


def _is_missing(value) -> bool:
    if value is None:
        return True
    try:
        return math.isnan(value)
    except (TypeError, ValueError):
        return False


def calculate_age_group(age: int) -> str:
    if age <= 17:
        return "pediatric"
    if age <= 39:
        return "young_adult"
    if age <= 64:
        return "middle_aged"
    return "elderly"


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    if _is_missing(weight_kg) or _is_missing(height_cm):
        return math.nan
    height_m = height_cm / 100
    if height_m <= 0:
        return math.nan
    return round(weight_kg / (height_m**2), 3)


def calculate_mean_arterial_pressure(systolic_bp: float, diastolic_bp: float) -> float:
    if _is_missing(systolic_bp) or _is_missing(diastolic_bp):
        return math.nan
    return round((systolic_bp + (2 * diastolic_bp)) / 3, 3)


def calculate_pulse_pressure(systolic_bp: float, diastolic_bp: float) -> float:
    if _is_missing(systolic_bp) or _is_missing(diastolic_bp):
        return math.nan
    return round(systolic_bp - diastolic_bp, 3)


def calculate_shock_index(heart_rate: float, systolic_bp: float) -> float:
    if _is_missing(heart_rate) or _is_missing(systolic_bp) or systolic_bp == 0:
        return math.nan
    return round(heart_rate / systolic_bp, 3)


def calculate_news2_score(
    heart_rate: float,
    respiratory_rate: float,
    spo2: float,
    temperature_c: float,
    systolic_bp: float,
    gcs_total: int,
) -> float:
    required_values = [
        heart_rate,
        respiratory_rate,
        spo2,
        temperature_c,
        systolic_bp,
        gcs_total,
    ]
    if any(_is_missing(value) for value in required_values):
        return math.nan

    score = 0

    if heart_rate <= 40:
        score += 3
    elif heart_rate <= 50:
        score += 1
    elif heart_rate <= 90:
        score += 0
    elif heart_rate <= 110:
        score += 1
    elif heart_rate <= 130:
        score += 2
    else:
        score += 3
        
    if respiratory_rate <= 8:
        score += 3
    elif respiratory_rate <= 11:
        score += 1
    elif respiratory_rate <= 20:
        score += 0
    elif respiratory_rate <= 24:
        score += 2
    else:
        score += 3

    if spo2 <= 91:
        score += 3
    elif spo2 <= 93:
        score += 2
    elif spo2 <= 95:
        score += 1

    if temperature_c <= 35:
        score += 3
    elif temperature_c <= 36:
        score += 1
    elif temperature_c <= 38:
        score += 0
    elif temperature_c <= 39:
        score += 1
    else:
        score += 2

    if systolic_bp <= 90:
        score += 3
    elif systolic_bp <= 100:
        score += 2
    elif systolic_bp <= 110:
        score += 1
    elif systolic_bp < 220:
        score += 0
    else:
        score += 3

    if gcs_total < 15:
        score += 3

    return score
