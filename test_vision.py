from nova_vision import read_medicine_label
import json

with open("test_medicine.jpg", "rb") as f:
    image_bytes = f.read()

result = read_medicine_label(image_bytes)
print(json.dumps(result, indent=2))