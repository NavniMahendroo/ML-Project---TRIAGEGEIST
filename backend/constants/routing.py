SPECIALTY_FALLBACK = "Emergency"

# Map likely chief complaint system/body-system labels to hospital specialties.
SPECIALTY_KEYWORDS = {
    "Cardiology": ["cardio", "heart", "vascular", "chest"],
    "Neurology": ["neuro", "brain", "stroke", "seizure", "head"],
    "Orthopedics": ["ortho", "bone", "joint", "musculoskeletal", "extremity", "trauma"],
    "Pediatrics": ["pedi", "child", "infant", "newborn"],
    "Pulmonology": ["pulm", "resp", "lung"],
    "Gastroenterology": ["gastro", "digest", "abd", "abdomen", "hepato"],
    "Nephrology": ["renal", "kidney", "genitourinary", "urinary", "uro"],
    "Psychiatry": ["psych", "mental", "behavior"],
    "Obstetrics & Gynecology": ["pregnan", "obst", "gyn", "reproductive"],
    "ENT": ["ent", "ear", "nose", "throat"],
    "Dermatology": ["derm", "skin"],
    "Oncology": ["onco", "cancer", "malignan"],
}

EMERGENCY_ACUITY_LEVELS = {1, 2}
