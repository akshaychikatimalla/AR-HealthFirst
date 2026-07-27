patient_profiles = {
    "demo_user": {
        "name": "Ramu (Demo Patient)",
        "age": 68,
        "medicines": ["warfarin", "metformin", "paracetamol"]
    }
}

def get_patient_profile(patient_id: str) -> dict:
    return patient_profiles.get(patient_id, {
        "name": "Unknown",
        "age": 0,
        "medicines": []
    })

def add_medicine(patient_id: str, medicine: str):
    if patient_id not in patient_profiles:
        patient_profiles[patient_id] = {
            "name": "New Patient",
            "age": 0,
            "medicines": []
        }
    patient_profiles[patient_id]["medicines"].append(medicine.lower())