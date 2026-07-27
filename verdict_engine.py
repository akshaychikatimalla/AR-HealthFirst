import boto3
import json

client = boto3.client("bedrock-runtime", region_name="us-east-1")

def generate_verdict(
    label_data: dict,
    patient_medicines: list,
    interactions: list
) -> dict:

    compositions = label_data.get("compositions", [])

    if interactions:
        interaction_text = ""
        for i in interactions:
            interaction_text += (
                f"\n- {i['ingredient']} conflicts with "
                f"{i['conflicts_with']}: {i['description']} "
                f"(severity: {i['severity']})"
            )
        has_warning = any(i["severity"] == "severe" for i in interactions)
    else:
        interaction_text = "No interactions found."
        has_warning = False

    prompt = f"""You are a pharmacist giving simple clear advice to an elderly patient.

Medicine scanned: {label_data.get('medicine_name', 'Unknown')}
Active ingredients found: {', '.join(compositions) if compositions else 'Unknown'}
Dosage: {label_data.get('dosage', 'Unknown')}
Instructions on label: {label_data.get('instructions', 'None')}
Label warnings: {label_data.get('warnings', [])}
Patient currently takes: {', '.join(patient_medicines) if patient_medicines else 'nothing'}
Drug interaction results: {interaction_text}

Write EXACTLY 3 lines. Simple words. Max 20 words per line.
Line 1: How and when to take this medicine
Line 2: WARNING about interactions if any, or "Safe with your current medicines" if none
Line 3: One practical reminder about food timing or storage

Return ONLY this JSON:
{{
  "line1": "...",
  "line2": "...",
  "line3": "..."
}}"""

    response = client.converse(
        modelId="us.amazon.nova-lite-v1:0",
        messages=[{"role": "user", "content": [{"text": prompt}]}]
    )

    raw = response["output"]["message"]["content"][0]["text"]
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
        result["has_warning"] = has_warning
        return result
    except:
        return {
            "line1": "Take as directed by your doctor.",
            "line2": "Please consult your doctor before use.",
            "line3": "Keep medicines away from children.",
            "has_warning": has_warning
        }