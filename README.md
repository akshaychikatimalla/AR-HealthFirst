# AR HealthFirst
### AI-powered medicine safety assistant for elderly patients

Built with Amazon Nova on AWS for the Amazon Nova AI Hackathon hosted on Devpost.

## The Problem
300 million elderly patients in India misread medicine labels daily.
Wrong dosage, dangerous combinations, and missed interactions cause
over 5 million hospitalizations annually.

## The Solution
AR HealthFirst uses your phone camera to scan any medicine strip
and instantly tells you:
- What it is and how to take it
- Whether it conflicts with your other medicines
- A plain-language verdict read aloud in English, Hindi, or Telugu

## Amazon Nova Models Used
- **Amazon Nova Lite** — reads medicine labels from images,
  extracts compositions, generates plain-language verdicts,
  builds daily schedules, reads prescriptions
- **Amazon Polly** — speaks the verdict aloud in English,
  Hindi, and Telugu

## Features
1. Live camera medicine scanner
2. Upload medicine image from gallery
3. Automatic drug composition extraction
4. Drug interaction checker (40+ combinations)
5. Voice verdict in English, Hindi, Telugu
6. Full prescription scanner
7. Daily medicine schedule generator
8. WhatsApp caregiver alert for severe interactions
9. Complete scan history with export
10. Works as Android PWA — installs on phone from browser

## SDG Alignment
SDG 3 — Good Health and Wellbeing
Specifically targeting elderly patients in rural India who
cannot read English labels or afford pharmacist consultations.

## Tech Stack
- Amazon Nova Lite (AWS Bedrock) — vision + reasoning
- Amazon Polly — multilingual text-to-speech
- FastAPI — backend server
- Python — nova_vision, drug_db, verdict_engine
- HTML/CSS/JS — progressive web app frontend
- AWS EC2 — deployment

## How to Run
```bash
pip install boto3 fastapi uvicorn pillow python-multipart pandas
aws configure  # add your AWS credentials
uvicorn main:app --reload --port 8000
# Open http://localhost:8000
```

## Team
- Saketh Ram — ML pipeline, data science, backend
- Sailesh — Cloud, Nova API integration
- Kaarthikeya — Security, DevOps, frontend
