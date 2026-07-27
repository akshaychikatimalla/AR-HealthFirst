from nova_vision import read_medicine_label
from drug_db import check_interactions
from verdict_engine import generate_verdict
from medication_profile import get_patient_profile
import json

print("=" * 50)
print("AR HealthFirst — Full Pipeline Test")
print("=" * 50)

# Step 1: Read medicine label from image
print("\n[1/4] Reading medicine label with Amazon Nova...")
with open("test_medicine.jpg", "rb") as f:
    image_bytes = f.read()

label = read_medicine_label(image_bytes)

print("\n=== LABEL DATA ===")
print(json.dumps(label, indent=2))

compositions = label.get("compositions", [])
print(f"\nCompositions detected: {compositions}")

# Step 2: Get patient profile
print("\n[2/4] Loading patient profile...")
profile = get_patient_profile("demo_user")
current_meds = profile["medicines"]
print(f"Patient: {profile['name']}, Age: {profile['age']}")
print(f"Currently takes: {current_meds}")

# Step 3: Check each composition against patient medicines
print("\n[3/4] Checking drug interactions...")
interactions = check_interactions(compositions, current_meds)

if interactions:
    print(f"\n=== {len(interactions)} INTERACTION(S) FOUND ===")
    print(json.dumps(interactions, indent=2))
else:
    print("\nNo interactions found — safe to take.")

# Step 4: Generate Nova verdict
print("\n[4/4] Generating verdict with Amazon Nova...")
verdict = generate_verdict(label, current_meds, interactions)

print("\n=== FINAL VERDICT ===")
print(f"Line 1 (How to take): {verdict['line1']}")
print(f"Line 2 (Warning):     {verdict['line2']}")
print(f"Line 3 (Reminder):    {verdict['line3']}")
print(f"Has warning:          {verdict['has_warning']}")

print("\n" + "=" * 50)
print("Pipeline test complete!")
print("=" * 50)