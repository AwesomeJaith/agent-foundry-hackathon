# agents.py
# Helpers for PhenoML grounding and patient record management.

import os, json, requests
from typing import List, Dict, Any, Optional, Tuple

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