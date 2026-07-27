import boto3
import json

client = boto3.client("bedrock-runtime", region_name="us-east-1")

def read_medicine_label(image_bytes: bytes) -> dict:
    prompt = """You are a pharmacist analyzing a medicine strip or tablet packaging photo.

Extract ALL information visible on the label.

Return ONLY a valid JSON object with EXACTLY these fields:
{
  "medicine_name": "brand name",
  "compositions": ["paracetamol", "caffeine"],
  "dosage": "500mg",
  "frequency": "twice daily",
  "instructions": "take after food",
  "warnings": ["warning1", "warning2"]
}

CRITICAL RULES for compositions field:
- compositions must be a LIST of active ingredient names
- Use generic chemical names (paracetamol NOT Calpol, ibuprofen NOT Brufen)
- Remove dosage numbers from names (paracetamol NOT paracetamol 500mg)
- If you see active_ingredient or composition on the label, put those values in the compositions list
- NEVER return an empty compositions list — always identify at least one ingredient
- Example: if label says "Paracetamol IP 650mg" then compositions = ["paracetamol"]
- Example: if label says "Ibuprofen 400mg + Paracetamol 325mg" then compositions = ["ibuprofen", "paracetamol"]

Return ONLY the JSON. No markdown. No explanation."""

    # Detect image format from bytes
    format = "jpeg"
    if image_bytes[:4] == b'RIFF' or image_bytes[8:12] == b'WEBP':
        format = "webp"
    elif image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        format = "png"

    response = client.converse(
        modelId="us.amazon.nova-lite-v1:0",
        messages=[{
            "role": "user",
            "content": [
                {
                    "image": {
                        "format": format,
                        "source": {"bytes": image_bytes}
                    }
                },
                {"text": prompt}
            ]
        }]
    )

    raw = response["output"]["message"]["content"][0]["text"]
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)

        # Safety net: if compositions is missing or empty
        # but active_ingredient exists, use that
        if not result.get("compositions"):
            if result.get("active_ingredient"):
                ingredient = result["active_ingredient"]
                # Clean dosage numbers out
                clean = ingredient.split("IP")[0].split("BP")[0].strip()
                clean = ''.join([c for c in clean if not c.isdigit()]).strip()
                result["compositions"] = [clean.lower().strip()]
            else:
                result["compositions"] = []

        # Clean all compositions
        cleaned = []
        for comp in result["compositions"]:
            c = comp.split("IP")[0].split("BP")[0].strip()
            c = ''.join([ch for ch in c if not ch.isdigit()]).strip().lower()
            if c:
                cleaned.append(c)
        result["compositions"] = cleaned

        return result

    except Exception as e:
        return {
            "medicine_name": "Unknown",
            "compositions": [],
            "dosage": None,
            "frequency": None,
            "instructions": raw,
            "warnings": []
        }