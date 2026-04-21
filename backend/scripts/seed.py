import sys
from datetime import UTC, datetime
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from database import ensure_indexes, get_collection, initialize_database  # noqa: E402
from src.doctors.schema import DoctorDocument  # noqa: E402
from src.patient_history.schema import PatientHistoryDocument  # noqa: E402
from src.nurses.schema import NurseDocument  # noqa: E402
from src.patients.schema import PatientDocument  # noqa: E402
from src.sites.schema import SiteDocument  # noqa: E402
from src.superadmin.schema import SuperAdminDocument  # noqa: E402
from utils.clinical_utils import calculate_age_group, calculate_bmi  # noqa: E402
from utils.security import hash_password  # noqa: E402


def _seed_documents(collection_name: str, key_field: str, documents: list[dict]) -> int:
    collection = get_collection(collection_name)
    inserted = 0
    for document in documents:
        result = collection.update_one(
            {key_field: document[key_field]},
            {"$setOnInsert": document},
            upsert=True,
        )
        if result.upserted_id is not None:
            inserted += 1
    return inserted


def _sync_counter(name: str, documents: list[dict], key_field: str, prefix: str) -> None:
    max_seq = 0
    for document in documents:
        key = document.get(key_field, "")
        if not isinstance(key, str) or not key.startswith(f"{prefix}-"):
            continue
        try:
            max_seq = max(max_seq, int(key.removeprefix(f"{prefix}-")))
        except ValueError:
            continue

    if max_seq == 0:
        return

    get_collection("_system_counters").update_one(
        {"_id": name},
        {"$max": {"seq": max_seq}},
        upsert=True,
    )


def _backfill_nurse_passwords(nurses: list[dict]) -> int:
    collection = get_collection("nurses")
    updated = 0
    for nurse in nurses:
        result = collection.update_one(
            {"nurse_id": nurse["nurse_id"]},
            {"$set": {"password": nurse["password"]}},
        )
        updated += result.modified_count
    return updated


def _backfill_nurse_roles(nurses: list[dict]) -> int:
    collection = get_collection("nurses")
    updated = 0
    for nurse in nurses:
        result = collection.update_one(
            {
                "nurse_id": nurse["nurse_id"],
                "$or": [
                    {"role": {"$exists": False}},
                    {"role": ""},
                    {"role": None},
                ],
            },
            {"$set": {"role": nurse["role"]}},
        )
        updated += result.modified_count
    return updated


def _backfill_nurse_on_duty(nurses: list[dict]) -> int:
    collection = get_collection("nurses")
    updated = 0
    for nurse in nurses:
        result = collection.update_one(
            {"nurse_id": nurse["nurse_id"]},
            {"$set": {"on_duty": nurse["on_duty"]}},
        )
        updated += result.modified_count
    return updated


def _backfill_doctor_credentials(doctors: list[dict]) -> tuple[int, int, int, int]:
    collection = get_collection("doctors")
    password_updates = 0
    role_updates = 0
    specialty_updates = 0
    on_duty_updates = 0
    for doctor in doctors:
        password_result = collection.update_one(
            {"doctor_id": doctor["doctor_id"]},
            {"$set": {"password": doctor["password"]}},
        )
        role_result = collection.update_one(
            {"doctor_id": doctor["doctor_id"]},
            {"$set": {"role": doctor["role"]}},
        )
        specialty_result = collection.update_one(
            {"doctor_id": doctor["doctor_id"]},
            {"$set": {"specialty": doctor["specialty"]}},
        )
        on_duty_result = collection.update_one(
            {"doctor_id": doctor["doctor_id"]},
            {"$set": {"on_duty": doctor["on_duty"]}},
        )
        password_updates += password_result.modified_count
        role_updates += role_result.modified_count
        specialty_updates += specialty_result.modified_count
        on_duty_updates += on_duty_result.modified_count
    return password_updates, role_updates, specialty_updates, on_duty_updates


def _backfill_superadmin_passwords(superadmins: list[dict]) -> int:
    collection = get_collection("superadmins")
    updated = 0
    for admin in superadmins:
        result = collection.update_one(
            {"admin_id": admin["admin_id"]},
            {"$set": {"password": admin["password"]}},
        )
        updated += result.modified_count
    return updated


def main():
    initialize_database()
    ensure_indexes()
    now = datetime.now(UTC)

    sites = [
        SiteDocument(site_id="SITE-0001", name="Central Emergency Department").model_dump(),
        SiteDocument(site_id="SITE-0002", name="Northside Triage Center").model_dump(),
        SiteDocument(site_id="SITE-0003", name="Riverfront Emergency Unit").model_dump(),
        SiteDocument(site_id="SITE-0004", name="West City Acute Care").model_dump(),
        SiteDocument(site_id="SITE-0005", name="South Gate Emergency Hub").model_dump(),
    ]
    nurses = [
        NurseDocument(
            nurse_id=f"NURSE-{index:04d}",
            name=f"Nurse {index:02d}",
            password=hash_password("12345678"),
            on_duty=True,
            role="staff",
        ).model_dump()
        for index in range(1, 11)
    ]
    doctor_specs = [
        ("DOC-0001", "Dr. Meera Nair", "Emergency", True),
        ("DOC-0002", "Dr. Karan Patel", "Cardiology", True),
        ("DOC-0003", "Dr. Hafsa Noor", "Neurology", True),
        ("DOC-0004", "Dr. Rohan Bedi", "Orthopedics", True),
        ("DOC-0005", "Dr. Elena D'Souza", "Pediatrics", True),
        ("DOC-0006", "Dr. Arjun Malhotra", "Pulmonology", True),
        ("DOC-0007", "Dr. Sana Qureshi", "Gastroenterology", False),
        ("DOC-0008", "Dr. Vikram Rao", "Nephrology", True),
        ("DOC-0009", "Dr. Leah Fernandes", "Obstetrics & Gynecology", True),
        ("DOC-0010", "Dr. Omar Siddiqui", "Emergency", False),
    ]
    doctors = [
        DoctorDocument(
            doctor_id=doctor_id,
            name=name,
            password=hash_password("12345678"),
            specialty=specialty,
            on_duty=on_duty,
            role="admin",
        ).model_dump()
        for doctor_id, name, specialty, on_duty in doctor_specs
    ]
    superadmins = [
        SuperAdminDocument(
            admin_id="SA-0001",
            name="Super Admin",
            password=hash_password("12345678"),
            role="superadmin",
        ).model_dump(),
        SuperAdminDocument(
            admin_id="SA-0002",
            name="Operations Lead",
            password=hash_password("12345678"),
            role="superadmin",
        ).model_dump(),
        SuperAdminDocument(
            admin_id="SA-0003",
            name="Clinical Director",
            password=hash_password("12345678"),
            role="superadmin",
        ).model_dump(),
    ]
    patients = [
        PatientDocument(
            patient_id="TG-0001",
            name="Aarav Sharma",
            age=27,
            sex="male",
            language="english",
            insurance_type="private",
            num_prior_ed_visits_12m=1,
            num_prior_admissions_12m=0,
            num_active_medications=1,
            num_comorbidities=0,
            weight_kg=72.4,
            height_cm=178.0,
            age_group=calculate_age_group(27),
            bmi=calculate_bmi(72.4, 178.0),
            created_at=now,
            updated_at=now,
        ).model_dump(),
        PatientDocument(
            patient_id="TG-0002",
            name="Priya Nair",
            age=43,
            sex="female",
            language="hindi",
            insurance_type="government",
            num_prior_ed_visits_12m=2,
            num_prior_admissions_12m=1,
            num_active_medications=3,
            num_comorbidities=2,
            weight_kg=68.0,
            height_cm=162.0,
            age_group=calculate_age_group(43),
            bmi=calculate_bmi(68.0, 162.0),
            created_at=now,
            updated_at=now,
        ).model_dump(),
        PatientDocument(
            patient_id="TG-0003",
            name="Rahul Verma",
            age=61,
            sex="male",
            language="english",
            insurance_type="self_pay",
            num_prior_ed_visits_12m=0,
            num_prior_admissions_12m=0,
            num_active_medications=2,
            num_comorbidities=1,
            weight_kg=84.2,
            height_cm=171.0,
            age_group=calculate_age_group(61),
            bmi=calculate_bmi(84.2, 171.0),
            created_at=now,
            updated_at=now,
        ).model_dump(),
        PatientDocument(
            patient_id="TG-0004",
            name="Fatima Khan",
            age=35,
            sex="female",
            language="urdu",
            insurance_type="private",
            num_prior_ed_visits_12m=3,
            num_prior_admissions_12m=1,
            num_active_medications=4,
            num_comorbidities=3,
            weight_kg=91.5,
            height_cm=165.0,
            age_group=calculate_age_group(35),
            bmi=calculate_bmi(91.5, 165.0),
            created_at=now,
            updated_at=now,
        ).model_dump(),
        PatientDocument(
            patient_id="TG-0005",
            name="Joseph Dsouza",
            age=74,
            sex="male",
            language="english",
            insurance_type="medicare",
            num_prior_ed_visits_12m=4,
            num_prior_admissions_12m=2,
            num_active_medications=6,
            num_comorbidities=4,
            weight_kg=76.3,
            height_cm=169.0,
            age_group=calculate_age_group(74),
            bmi=calculate_bmi(76.3, 169.0),
            created_at=now,
            updated_at=now,
        ).model_dump(),
        PatientDocument(
            patient_id="TG-0006",
            name="Meera Iyer",
            age=31,
            sex="female",
            language="english",
            insurance_type="private",
            num_prior_ed_visits_12m=0,
            num_prior_admissions_12m=0,
            num_active_medications=0,
            num_comorbidities=0,
            weight_kg=58.7,
            height_cm=160.0,
            age_group=calculate_age_group(31),
            bmi=calculate_bmi(58.7, 160.0),
            created_at=now,
            updated_at=now,
        ).model_dump(),
        PatientDocument(
            patient_id="TG-0007",
            name="Karan Malhotra",
            age=49,
            sex="male",
            language="hindi",
            insurance_type="employer",
            num_prior_ed_visits_12m=1,
            num_prior_admissions_12m=0,
            num_active_medications=2,
            num_comorbidities=1,
            weight_kg=79.1,
            height_cm=174.0,
            age_group=calculate_age_group(49),
            bmi=calculate_bmi(79.1, 174.0),
            created_at=now,
            updated_at=now,
        ).model_dump(),
        PatientDocument(
            patient_id="TG-0008",
            name="Ananya Bose",
            age=22,
            sex="female",
            language="bengali",
            insurance_type="self_pay",
            num_prior_ed_visits_12m=0,
            num_prior_admissions_12m=0,
            num_active_medications=1,
            num_comorbidities=0,
            weight_kg=54.0,
            height_cm=157.0,
            age_group=calculate_age_group(22),
            bmi=calculate_bmi(54.0, 157.0),
            created_at=now,
            updated_at=now,
        ).model_dump(),
    ]
    patient_history = [
        PatientHistoryDocument(
            patient_id="TG-0002",
            hx_hypertension=True,
            hx_diabetes_type2=True,
            hx_asthma=False,
            hx_ckd=False,
            hx_obesity=False,
            hx_depression=False,
            hx_anxiety=True,
        ).model_dump(),
        PatientHistoryDocument(
            patient_id="TG-0004",
            hx_hypertension=True,
            hx_diabetes_type2=False,
            hx_asthma=True,
            hx_obesity=True,
            hx_depression=True,
            hx_anxiety=True,
            hx_pregnant=False,
        ).model_dump(),
        PatientHistoryDocument(
            patient_id="TG-0005",
            hx_hypertension=True,
            hx_heart_failure=True,
            hx_atrial_fibrillation=True,
            hx_ckd=True,
            hx_coronary_artery_disease=True,
            hx_stroke_prior=False,
        ).model_dump(),
    ]

    site_count = _seed_documents("sites", "site_id", sites)
    nurse_count = _seed_documents("nurses", "nurse_id", nurses)
    doctor_count = _seed_documents("doctors", "doctor_id", doctors)
    superadmin_count = _seed_documents("superadmins", "admin_id", superadmins)
    nurse_password_backfill_count = _backfill_nurse_passwords(nurses)
    nurse_role_backfill_count = _backfill_nurse_roles(nurses)
    nurse_on_duty_backfill_count = _backfill_nurse_on_duty(nurses)
    doctor_password_backfill_count, doctor_role_backfill_count, doctor_specialty_backfill_count, doctor_on_duty_backfill_count = _backfill_doctor_credentials(doctors)
    superadmin_password_backfill_count = _backfill_superadmin_passwords(superadmins)
    patient_count = _seed_documents("patients", "patient_id", patients)
    history_count = _seed_documents("patient_history", "patient_id", patient_history)
    _sync_counter("patients", patients, "patient_id", "TG")

    print(
        "Seed complete. "
        f"Inserted {site_count} site(s), {nurse_count} nurse(s), {doctor_count} doctor(s), {superadmin_count} superadmin(s), "
        f"backfilled {nurse_password_backfill_count} nurse password(s), {nurse_role_backfill_count} nurse role(s), {nurse_on_duty_backfill_count} nurse on-duty field(s), "
        f"{doctor_password_backfill_count} doctor password(s), {doctor_role_backfill_count} doctor role(s), "
        f"{doctor_specialty_backfill_count} doctor specialty field(s), {doctor_on_duty_backfill_count} doctor on-duty field(s), "
        f"{superadmin_password_backfill_count} superadmin password(s), "
        f"{patient_count} patient(s), and {history_count} patient history record(s)."
    )


if __name__ == "__main__":
    main()
