# agents.py
# Helpers for PhenoML grounding and patient record management.

import os, json, requests
from typing import List, Dict, Any, Optional, Tuple
import openai
from datetime import datetime
import uuid

# -------- env --------
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(usecwd=True) or ".env", override=True)
except Exception:
    pass

def _clean(s: Optional[str]) -> str:
    return (s or "").strip().strip('"').strip("'").replace("\r","").replace("\ufeff","")

PHENOML_BASE = _clean(os.getenv("PHENOML_BASE"))
PHENOML_JWT  = _clean(os.getenv("PHENOML_JWT"))
OPENAI_API_KEY = _clean(os.getenv("OPENAI_API_KEY") or "")
DEEPGRAM_API_KEY = _clean(os.getenv("DEEPGRAM_API_KEY") or "")

assert PHENOML_BASE and PHENOML_JWT, "Set PHENOML_BASE and PHENOML_JWT in .env"

HEADERS = {"Authorization": f"Bearer {PHENOML_JWT}", "Content-Type": "application/json"}
ICD10_SEARCH = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
SNOMED_FHIR_LOOKUP = "https://ontoserver.aws.gel.ac/fhir/CodeSystem/$lookup"

DB_PATH = "patients.json"

# -------- DB helpers --------
def load_db() -> List[Dict[str, Any]]:
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    return json.load(open(DB_PATH, "r", encoding="utf-8"))

def save_db(db: List[Dict[str, Any]]):
    tmp = DB_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DB_PATH)

def next_id(db: List[Dict[str, Any]]) -> str:
    return str(max([int(p.get("id",0)) for p in db] + [0]) + 1)

def split_name(name: str) -> Tuple[str,str]:
    parts = [x for x in (name or "").strip().split() if x]
    if not parts: return "",""
    if len(parts)==1: return parts[0].capitalize(),""
    return parts[0].capitalize()," ".join(w.capitalize() for w in parts[1:])

def find_patient(db: List[Dict[str, Any]], id_or_name: str) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    s = (id_or_name or "").strip().lower()
    if not s: return None,[]
    if s.isdigit():
        for p in db:
            if str(p.get("id","")).strip() == s:
                return p,[]
        return None,[]
    matches=[]
    for p in db:
        full=f"{p.get('firstName','')} {p.get('lastName','')}".strip().lower()
        if s in full: matches.append(p)
    if len(matches)==1: return matches[0],[]
    return None,matches

def ensure_patient_by_name(name: str) -> Dict[str, Any]:
    db=load_db()
    p,_=find_patient(db, name)
    if p: return p
    first,last=split_name(name)
    pid=next_id(db)
    patient={"id":pid,"firstName":first,"lastName":last,
             "conditions":[],"appointments":[],"nextAppointment":None}
    db.append(patient); save_db(db)
    return patient

def get_patient_by_id(pid: str) -> Optional[Dict[str, Any]]:
    db=load_db(); p,_=find_patient(db, pid); return p

def update_patient(patient: Dict[str, Any]):
    db=load_db()
    for i,p in enumerate(db):
        if str(p.get("id",""))==str(patient.get("id","")):
            db[i]=patient; save_db(db); return
    db.append(patient); save_db(db)

# -------- Appointment helpers --------
def book_appointment(patient: Dict[str,Any], when: str, doctor: Optional[str]=None) -> str:
    appt={"when":when,"doctor":doctor,"status":"booked"}
    arr=patient.get("appointments") or []
    arr.append(appt)
    patient["appointments"]=arr
    patient["nextAppointment"]=when
    update_patient(patient)
    who=f"{patient.get('firstName','')} {patient.get('lastName','')}".strip()
    return f"one sec… okay, you’re booked {when}" + (f" with {doctor}." if doctor else ".")

def cancel_next(patient: Dict[str,Any]) -> str:
    arr=patient.get("appointments") or []
    if arr: arr[-1]["status"]="canceled"
    patient["nextAppointment"]=None
    patient["appointments"]=arr; update_patient(patient)
    who=f"{patient.get('firstName','')} {patient.get('lastName','')}".strip()
    return f"done — I canceled your appointment."

def next_appt(patient: Dict[str,Any]) -> str:
    nxt=patient.get("nextAppointment")
    return f"you’ve got one {nxt}." if nxt else "no appointment on file."

def get_field(patient: Dict[str,Any], field: str) -> str:
    val=patient.get(field, None)
    if isinstance(val,list): return ", ".join(val) or "none"
    return str(val) if val else "not on file"

def add_condition(patient: Dict[str,Any], term: str):
    if not term: return
    arr=patient.get("conditions") or []
    if term.lower() not in [x.lower() for x in arr]:
        arr.append(term)
        patient["conditions"]=arr; update_patient(patient)

# -------- PhenoML grounding --------
def construe(text: str) -> Dict[str, Any]:
    r=requests.post(f"{PHENOML_BASE}/construe/extract",headers=HEADERS,
                    json={"text":text,"target_systems":["ICD10","SNOMED"]},timeout=15)
    r.raise_for_status(); return r.json()

def enrich_terms(cj: Dict[str,Any]) -> List[str]:
    terms=[]
    if not isinstance(cj,dict): return terms
    if isinstance(cj.get("codes"),list):
        for c in cj["codes"]:
            if "description" in c: terms.append(c["description"])
    if isinstance(cj.get("concepts"),list):
        for c in cj["concepts"]:
            if "display" in c: terms.append(c["display"])
    # dedupe
    out=[]; seen=set()
    for t in terms:
        if t.lower() not in seen: seen.add(t.lower()); out.append(t)
    return out[:3]

# -------- OpenAI Integration --------
def call_openai_chat(messages: List[Dict[str, str]], model: str = "gpt-4o-mini", max_tokens: int = 200, temperature: float = 0.1) -> Optional[str]:
    """Make OpenAI API call with error handling using new OpenAI v1.0+ API"""
    if not OPENAI_API_KEY:
        return None
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
        
    except ImportError:
        print("OpenAI library not installed. Run: pip install openai>=1.0.0")
        return None
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

# -------- Patient and Symptom Report Extraction Agent --------

def extract_patient_and_symptoms_from_transcript(transcript: str, patient_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract patient details and symptom reports from a conversation transcript.
    Returns a dictionary with 'patient' and 'symptomReports' keys.
    """
    
    # Initialize OpenAI client
    if not OPENAI_API_KEY:
        return {"error": "OpenAI API key not configured"}
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
    except ImportError:
        return {"error": "OpenAI library not installed"}
    
    # Create the extraction prompt
    extraction_prompt = f"""
You are a medical AI assistant tasked with extracting structured patient information and symptom reports from a conversation transcript.

Please analyze the following transcript and extract:

1. PATIENT INFORMATION (if mentioned):
- First and last name
- Date of birth
- Gender
- Phone number
- Email address
- Address (street, city, state, zip)
- Insurance information
- Medical history
- Family history
- Allergies
- Current medications
- Medical conditions

2. SYMPTOM REPORTS:
- All symptoms mentioned with severity (mild/moderate/severe/critical)
- Duration of symptoms
- Frequency
- Triggers
- Source of information (patient/caregiver/doctor)
- Any AI analysis or suggested actions

TRANSCRIPT:
{transcript}

Please respond with a JSON object in this exact format:
{{
  "patient": {{
    "id": "{patient_id or 'auto_generated'}",
    "firstName": "string or null",
    "lastName": "string or null", 
    "dateOfBirth": "YYYY-MM-DD or null",
    "gender": "male|female|other or null",
    "phoneNumber": "string or null",
    "email": "string or null",
    "address": {{
      "street": "string or null",
      "city": "string or null", 
      "state": "string or null",
      "zipCode": "string or null"
    }} or null,
    "insuranceProvider": "string or null",
    "memberId": "string or null",
    "policyHolder": "string or null",
    "paymentOption": "string or null",
    "familyHistory": "string or null",
    "medicalHistory": "string or null",
    "allergies": ["array of strings"] or [],
    "medications": ["array of strings"] or [],
    "conditions": ["array of strings"] or []
  }},
  "symptomReports": [
    {{
      "id": "auto_generated",
      "timestamp": "ISO timestamp",
      "reportedBy": "patient|ai|caregiver|doctor",
      "source": "chat|phone|email|visit|ai_analysis",
      "symptoms": [
        {{
          "description": "string",
          "severity": "mild|moderate|severe|critical",
          "duration": "string or null",
          "frequency": "string or null", 
          "triggers": ["array of strings"] or []
        }}
      ],
      "aiAnalysis": {{
        "summary": "string",
        "urgency": "low|medium|high|urgent",
        "suggestedActions": ["array of strings"],
        "confidence": number (0-100),
        "relatedConditions": ["array of strings"] or []
      }} or null,
      "status": "new",
      "assignedTo": "string or null",
      "notes": "string or null",
      "attachments": [
        {{
          "type": "transcript|recording|document|image",
          "url": "string",
          "description": "string"
        }}
      ] or []
    }}
  ]
}}

IMPORTANT:
- Only include fields that are explicitly mentioned in the transcript
- Use null for missing information, not empty strings
- Generate realistic severity assessments based on symptom descriptions
- Set urgency based on symptom severity and context
- Include confidence scores for AI analysis
- Generate unique IDs for symptom reports
- Use current timestamp for symptom report timestamps
- Be conservative with severity assessments - default to mild/moderate unless clearly severe
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a medical AI assistant that extracts structured patient information from transcripts. Respond only with valid JSON."},
                {"role": "user", "content": extraction_prompt}
            ],
            max_tokens=4000,
            temperature=0.1
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Clean up the response - remove markdown formatting if present
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        
        result = json.loads(result_text)
        
        # Post-process the results
        result = post_process_extraction_result(result, patient_id)
        
        return result
        
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse JSON response: {e}", "raw_response": result_text}
    except Exception as e:
        return {"error": f"Extraction failed: {e}"}

def post_process_extraction_result(result: Dict[str, Any], patient_id: Optional[str] = None) -> Dict[str, Any]:
    """Post-process and validate the extraction results"""
    
    # Ensure patient ID is set
    if patient_id and "patient" in result:
        result["patient"]["id"] = patient_id
    
    # Generate IDs for symptom reports if missing
    if "symptomReports" in result:
        for report in result["symptomReports"]:
            if not report.get("id"):
                report["id"] = f"sr-{uuid.uuid4().hex[:8]}"
            
            # Ensure timestamp is set
            if not report.get("timestamp"):
                report["timestamp"] = datetime.utcnow().isoformat() + "Z"
            
            # Validate severity levels
            for symptom in report.get("symptoms", []):
                if symptom.get("severity") not in ["mild", "moderate", "severe", "critical"]:
                    symptom["severity"] = "moderate"  # Default to moderate
            
            # Validate urgency levels
            if report.get("aiAnalysis") and report["aiAnalysis"].get("urgency"):
                if report["aiAnalysis"]["urgency"] not in ["low", "medium", "high", "urgent"]:
                    report["aiAnalysis"]["urgency"] = "medium"  # Default to medium
    
    return result

def save_extracted_data_to_patient(extraction_result: Dict[str, Any], patient_id: str) -> Dict[str, Any]:
    """
    Save extracted patient data and symptom reports to the patient record.
    Returns success status and any errors.
    """
    
    if "error" in extraction_result:
        return {"success": False, "error": extraction_result["error"]}
    
    try:
        # Load current patient data
        patient = get_patient_by_id(patient_id)
        if not patient:
            return {"success": False, "error": f"Patient {patient_id} not found"}
        
        # Update patient information
        if "patient" in extraction_result:
            patient_data = extraction_result["patient"]
            
            # Update basic info (only if not already set or if new info is provided)
            for field in ["firstName", "lastName", "dateOfBirth", "gender", "phoneNumber", "email"]:
                if patient_data.get(field) and not patient.get(field):
                    patient[field] = patient_data[field]
            
            # Update address
            if patient_data.get("address") and not patient.get("address"):
                patient["address"] = patient_data["address"]
            
            # Update insurance info
            for field in ["insuranceProvider", "memberId", "policyHolder", "paymentOption"]:
                if patient_data.get(field) and not patient.get(field):
                    patient[field] = patient_data[field]
            
            # Update medical info
            for field in ["familyHistory", "medicalHistory"]:
                if patient_data.get(field) and not patient.get(field):
                    patient[field] = patient_data[field]
            
            # Update arrays (append new items)
            for field in ["allergies", "medications", "conditions"]:
                if patient_data.get(field):
                    existing = patient.get(field, [])
                    new_items = [item for item in patient_data[field] if item not in existing]
                    if new_items:
                        patient[field] = existing + new_items
        
        # Add symptom reports
        if "symptomReports" in extraction_result and extraction_result["symptomReports"]:
            existing_reports = patient.get("symptomReports", [])
            new_reports = extraction_result["symptomReports"]
            
            # Add conversation transcript as attachment to each report
            for report in new_reports:
                if not report.get("attachments"):
                    report["attachments"] = []
                report["attachments"].append({
                    "type": "transcript",
                    "url": f"/transcripts/{patient_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    "description": "Conversation transcript"
                })
            
            # Prepend new reports (most recent first)
            patient["symptomReports"] = new_reports + existing_reports
        
        # Generate AI summary if not present
        if not patient.get("aiSummary") and extraction_result.get("symptomReports"):
            patient["aiSummary"] = generate_ai_summary(extraction_result["symptomReports"])
        
        # Save updated patient
        update_patient(patient)
        
        return {
            "success": True,
            "patient_id": patient_id,
            "symptom_reports_added": len(extraction_result.get("symptomReports", [])),
            "patient_updated": True
        }
        
    except Exception as e:
        return {"success": False, "error": f"Failed to save data: {e}"}

def generate_ai_summary(symptom_reports: List[Dict[str, Any]]) -> str:
    """Generate an AI summary from symptom reports"""
    
    if not symptom_reports:
        return "No symptom reports available."
    
    # Get the most recent report
    latest_report = symptom_reports[0]
    
    symptoms_text = ", ".join([s["description"] for s in latest_report.get("symptoms", [])])
    urgency = latest_report.get("aiAnalysis", {}).get("urgency", "medium")
    
    if urgency in ["high", "urgent"]:
        return f"Patient experiencing {symptoms_text}. Urgent attention recommended."
    elif urgency == "medium":
        return f"Patient reporting {symptoms_text}. Follow-up recommended within 1-2 weeks."
    else:
        return f"Patient mentions {symptoms_text}. Routine monitoring advised."

def extract_and_save_from_transcript(transcript: str, patient_id: str) -> Dict[str, Any]:
    """
    Complete workflow: extract data from transcript and save to patient record.
    This is the main function to use for processing transcripts.
    """
    
    # Extract data from transcript
    extraction_result = extract_patient_and_symptoms_from_transcript(transcript, patient_id)
    
    if "error" in extraction_result:
        return extraction_result
    
    # Save to patient record
    save_result = save_extracted_data_to_patient(extraction_result, patient_id)
    
    return {
        "extraction": extraction_result,
        "save_result": save_result
    }