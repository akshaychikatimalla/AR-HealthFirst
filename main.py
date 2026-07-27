from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from nova_vision import read_medicine_label
from drug_db import check_interactions
from verdict_engine import generate_verdict
from medication_profile import get_patient_profile

app = FastAPI(title="AR HealthFirst")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/analyze")
async def analyze(
    image: UploadFile = File(...),
    patient_id: str = "demo_user"
):
    image_bytes = await image.read()

    # Step 1: Nova reads label and extracts compositions
    label = read_medicine_label(image_bytes)
    compositions = label.get("compositions", [])

    # Step 2: Get patient profile
    profile = get_patient_profile(patient_id)
    current_meds = profile.get("medicines", [])

    # Step 3: Check each composition against patient medicines
    interactions = check_interactions(compositions, current_meds)

    # Step 4: Nova generates verdict
    # Step 4: Nova generates verdict
    verdict = generate_verdict(label, current_meds, interactions)

    # Step 5: Auto-add scanned medicine to patient profile
    from medication_profile import patient_profiles
    med_name = label.get("medicine_name", "")
    if med_name and med_name != "Unknown":
        # Add compositions to profile not brand name
        for comp in compositions:
            if comp and comp not in patient_profiles.get(patient_id, {}).get("medicines", []):
                patient_profiles[patient_id]["medicines"].append(comp)

    return {
        "label": label,
        "compositions_detected": compositions,
        "current_medicines": patient_profiles[patient_id]["medicines"],
        "interactions": interactions,
        "verdict": verdict
    }

    return {
        "label": label,
        "compositions_detected": compositions,
        "current_medicines": current_meds,
        "interactions": interactions,
        "verdict": verdict
    }

@app.get("/profile/{patient_id}")
def get_profile(patient_id: str):
    return get_patient_profile(patient_id)

@app.get("/generate-schedule")
async def generate_schedule(patient_id: str = "demo_user"):
    from medication_profile import get_patient_profile
    import boto3

    profile = get_patient_profile(patient_id)
    medicines = profile.get("medicines", [])

    if not medicines:
        return {
            "schedule": None,
            "message": "No medicines in profile yet. Scan some strips first."
        }

    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    prompt = f"""You are a pharmacist creating a daily medicine schedule for an elderly patient.

Patient medicines: {', '.join(medicines)}

Create a practical daily schedule. Consider:
- Metformin/diabetes medicines → with meals
- Blood thinners like warfarin → same time every day, alone
- Antibiotics → evenly spaced, complete course
- BP medicines → morning usually
- Antacids → before meals
- Avoid combining medicines that interact

Return ONLY this JSON with exactly 4 time slots:
{{
  "morning":   {{ "time": "8:00 AM",  "medicines": ["med + instruction"], "note": "one tip" }},
  "afternoon": {{ "time": "2:00 PM",  "medicines": ["med + instruction"], "note": "one tip" }},
  "evening":   {{ "time": "6:00 PM",  "medicines": ["med + instruction"], "note": "one tip" }},
  "night":     {{ "time": "10:00 PM", "medicines": ["med + instruction"], "note": "one tip" }}
}}

Rules:
- Each medicine must appear at least once
- medicines list can be empty [] if nothing at that time
- instruction must be under 8 words (e.g. "with food", "alone with water")
- note must be under 12 words
- Return ONLY JSON"""

    response = client.converse(
        modelId="us.amazon.nova-lite-v1:0",
        messages=[{"role": "user", "content": [{"text": prompt}]}]
    )

    raw = response["output"]["message"]["content"][0]["text"]
    raw = raw.replace("```json", "").replace("```", "").strip()

    import json
    try:
        schedule = json.loads(raw)
        return {
            "schedule": schedule,
            "medicines": medicines,
            "message": "success"
        }
    except:
        return {
            "schedule": None,
            "message": "Could not generate schedule. Try again."
        }

@app.post("/add-medicine")
def add_medicine_endpoint(patient_id: str = "demo_user", medicine: str = ""):
    from medication_profile import patient_profiles
    if medicine:
        patient_profiles[patient_id]["medicines"].append(medicine.lower().strip())
    return {"medicines": patient_profiles[patient_id]["medicines"]}

@app.post("/remove-medicine")
def remove_medicine_endpoint(patient_id: str = "demo_user", medicine: str = ""):
    from medication_profile import patient_profiles
    meds = patient_profiles[patient_id]["medicines"]
    patient_profiles[patient_id]["medicines"] = [
        m for m in meds if m != medicine.lower().strip()
    ]
    return {"medicines": patient_profiles[patient_id]["medicines"]}

@app.post("/clear-medicines")
def clear_medicines_endpoint(patient_id: str = "demo_user"):
    from medication_profile import patient_profiles
    patient_profiles[patient_id]["medicines"] = []
    return {"medicines": []}

@app.post("/speak-verdict")
async def speak_verdict(
    line1: str = "",
    line2: str = "",
    line3: str = "",
    language: str = "english"
):
    from fastapi.responses import Response
    import boto3

    # Language → Polly voice mapping
    # Language → Polly voice + engine mapping
    voice_map = {
        "hindi":   {"VoiceId": "Aditi",  "LanguageCode": "hi-IN", "Engine": "standard"},
        "telugu":  {"VoiceId": "Kajal",  "LanguageCode": "te-IN", "Engine": "neural"},
        "english": {"VoiceId": "Joanna", "LanguageCode": "en-US", "Engine": "neural"}
    }

    if language == "hindi":
        text = (
            f"दवाई की जानकारी। "
            f"{line1}। "
            f"{line2}। "
            f"याद रखें, {line3}"
        )
    elif language == "telugu":
        text = (
            f"మందు సమాచారం। "
            f"{line1}। "
            f"{line2}। "
            f"గుర్తుంచుకోండి, {line3}"
        )
    else:
        text = (
            f"Medicine information. "
            f"{line1}. "
            f"{line2}. "
            f"Remember: {line3}."
        )

    config = voice_map.get(language, voice_map["english"])

    try:
        polly = boto3.client("polly", region_name="us-east-1")

        response = polly.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId=config["VoiceId"],
            LanguageCode=config["LanguageCode"],
            Engine=config["Engine"]
        )

        audio_bytes = response["AudioStream"].read()

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg"
        )

    except Exception as e:
        return Response(
            content=json.dumps({"error": str(e)}).encode(),
            media_type="application/json",
            status_code=500
        )
@app.post("/scan-prescription")
async def scan_prescription(
    image: UploadFile = File(...),
    patient_id: str = "demo_user"
):
    from nova_vision import read_prescription
    from medication_profile import patient_profiles
    from drug_db import check_interactions

    image_bytes = await image.read()

    # Step 1: Nova reads the prescription
    prescription = read_prescription(image_bytes)
    medicines_found = prescription.get("medicines", [])

    if not medicines_found:
        return {
            "prescription": prescription,
            "medicines_added": [],
            "cross_interactions": [],
            "message": "No medicines found in image. Try a clearer photo."
        }

    # Step 2: Extract compositions and add to patient profile
    added_medicines = []
    all_compositions = []

    for med in medicines_found:
        comp = med.get("composition", "")
        name = med.get("name", "")

        # Use composition if available, else use name
        identifier = comp.lower().strip() if comp else name.lower().strip()

        if identifier:
            all_compositions.append(identifier)
            current = patient_profiles.get(
                patient_id, {}
            ).get("medicines", [])

            if identifier not in current:
                if patient_id not in patient_profiles:
                    patient_profiles[patient_id] = {
                        "name": "Patient",
                        "age": 0,
                        "medicines": []
                    }
                patient_profiles[patient_id]["medicines"].append(identifier)
                added_medicines.append(identifier)

    # Step 3: Cross-check ALL medicines against each other
    cross_interactions = []
    seen = set()

    for i, comp_a in enumerate(all_compositions):
        others = all_compositions[:i] + all_compositions[i+1:]
        interactions = check_interactions([comp_a], others)
        for interaction in interactions:
            key = f"{interaction['ingredient']}-{interaction['conflicts_with']}"
            reverse_key = f"{interaction['conflicts_with']}-{interaction['ingredient']}"
            if key not in seen and reverse_key not in seen:
                seen.add(key)
                cross_interactions.append(interaction)

    return {
        "prescription": prescription,
        "medicines_added": added_medicines,
        "all_compositions": all_compositions,
        "cross_interactions": cross_interactions,
        "total_medicines": len(medicines_found),
        "message": f"Found {len(medicines_found)} medicines. Added {len(added_medicines)} new ones."
    }