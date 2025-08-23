# casey.py
# Conversational, human-feel health case manager (CLI)
# - Ground symptoms with PhenoML (quietly; no code dumps)
# - Natural replies (optionally polished via OpenAI)
# - Register patients, auto-ID
# - Book / cancel / show appointments in a shared patients.json
# - Single file, minimal output (feels like texting a human)
#
# ⚠️ Educational only. Not medical advice.

import os, re, json, time, shutil, requests
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
try:
    from dotenv import load_dotenv, find_dotenv
    envp = find_dotenv(usecwd=True) or ".env"
    load_dotenv(envp, override=True)
except Exception:
    pass

# ---------- robust env ----------
def _clean(s: Optional[str]) -> str:
    return (s or "").strip().strip('"').strip("'").replace("\r","").replace("\ufeff","")

PHENOML_BASE = _clean(os.getenv("PHENOML_BASE"))
PHENOML_JWT  = _clean(os.getenv("PHENOML_JWT"))
OPENAI_API_KEY = _clean(os.getenv("OPENAI_API_KEY"))

assert PHENOML_BASE and PHENOML_JWT, "Set PHENOML_BASE and PHENOML_JWT in .env"

if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# ---------- constants ----------
HEADERS = {"Authorization": f"Bearer {PHENOML_JWT}", "Content-Type": "application/json"}
ICD10_SEARCH = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
SNOMED_FHIR_LOOKUP = "https://ontoserver.aws.gel.ac/fhir/CodeSystem/$lookup"
DB_PATH = "patients.json"

# ---------- persona prompts (kept inside the script) ----------
SYSTEM_TONE = (
    "You are Casey, an empathetic healthcare case manager. Be concise, warm, and practical. "
    "Do not provide diagnoses or treatment. Encourage timely care when appropriate. "
    "You may reference standardized terms if available, but never dump codes. "
    "If user requests booking and we have enough info, confirm succinctly. "
    "Always respect privacy. Educational only; not medical advice."
)

EXPLAIN_FROM_TERMS_PROMPT = (
    "Summarize the patient's symptoms in plain language using the provided standardized terms "
    "(ICD-10 / SNOMED displays), without listing codes. Be supportive, ask 1–3 focused follow-up "
    "questions, and end with: 'This is not medical advice; please consult a licensed clinician.'"
)

# ---------- tiny UI helpers ----------
def _termw() -> int:
    try: return shutil.get_terminal_size().columns
    except Exception: return 80

def say(text: str):
    # minimal chat feel (one line breaks ok)
    print(text.strip())

# ---------- patients DB ----------
def _load_db() -> List[Dict[str, Any]]:
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    try:
        return json.load(open(DB_PATH, "r", encoding="utf-8"))
    except Exception:
        return []

def _save_db(db: List[Dict[str, Any]]):
    tmp = DB_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DB_PATH)

def _next_id(db: List[Dict[str, Any]]) -> str:
    mx = 0
    for p in db:
        try: mx = max(mx, int(str(p.get("id","0")).strip() or 0))
        except: pass
    return str(mx + 1)

def _split_name(s: str) -> Tuple[str, str]:
    s = (s or "").strip()
    if not s: return "", ""
    parts = [x for x in s.split() if x]
    if len(parts) == 1: return parts[0].capitalize(), ""
    return parts[0].capitalize(), " ".join(p.capitalize() for p in parts[1:])

def find_patient(db: List[Dict[str, Any]], id_or_name: str) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    if not id_or_name: return None, []
    s = id_or_name.strip().lower()
    if s.isdigit():
        for p in db:
            if str(p.get("id","")).strip() == s:
                return p, []
        return None, []
    # name search
    matches = []
    for p in db:
        full = f"{p.get('firstName','')} {p.get('lastName','')}".strip().lower()
        if s in full:
            matches.append(p)
    if len(matches) == 1:
        return matches[0], []
    return None, matches

def ensure_patient(name_hint: Optional[str], ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Return a patient record for current user; create if name given and not found."""
    db = _load_db()
    # already linked?
    if ctx.get("patient_id"):
        p, _ = find_patient(db, ctx["patient_id"])
        if p: return p
    # if we have a name hint, try to find or create
    if name_hint:
        p, many = find_patient(db, name_hint)
        if p:
            ctx["patient_id"] = p["id"]
            ctx["name"] = f"{p.get('firstName','')} {p.get('lastName','')}".strip()
            return p
        # create new
        first, last = _split_name(name_hint)
        pid = _next_id(db)
        patient = {
            "id": pid,
            "firstName": first,
            "lastName": last,
            "dateOfBirth": None,
            "phoneNumber": None,
            "email": None,
            "address": {},
            "insuranceProvider": None,
            "memberId": None,
            "policyHolder": f"{first} {last}".strip(),
            "paymentOption": None,
            "phoneCalls": 0,
            "emails": 0,
            "familyHistory": "",
            "medicalHistory": "",
            "consentForms": [],
            "allergies": [],
            "medications": [],
            "conditions": [],
            "lastVisit": None,
            "nextAppointment": None,
            "appointments": []
        }
        db.append(patient)
        _save_db(db)
        ctx["patient_id"] = pid
        ctx["name"] = f"{first} {last}".strip()
        return patient
    return {}

def book_appointment_for(patient: Dict[str, Any], when: str, doctor: Optional[str]) -> str:
    db = _load_db()
    # refresh patient reference
    p, _ = find_patient(db, patient["id"])
    if not p:
        return "I couldn't find that patient in the records."
    appt = {"when": when, "doctor": doctor or None, "status": "booked"}
    p["nextAppointment"] = when
    arr = p.get("appointments") or []
    arr.append(appt)
    p["appointments"] = arr
    _save_db(db)
    who = f"{p.get('firstName','')} {p.get('lastName','')}".strip() or f"#{p['id']}"
    doc = f" with {doctor}" if doctor else ""
    return f"All set — I booked {who} on {when}{doc}."

def cancel_next_appointment(patient: Dict[str, Any]) -> str:
    db = _load_db()
    p, _ = find_patient(db, patient["id"])
    if not p:
        return "I couldn't find that patient in the records."
    p["nextAppointment"] = None
    arr = p.get("appointments") or []
    if arr:
        arr[-1]["status"] = "canceled"
    p["appointments"] = arr
    _save_db(db)
    who = f"{p.get('firstName','')} {p.get('lastName','')}".strip() or f"#{p['id']}"
    return f"Done — I canceled the next appointment for {who}."

def next_appt_text(patient: Dict[str, Any]) -> str:
    nxt = patient.get("nextAppointment")
    if nxt:
        who = f"{patient.get('firstName','')} {patient.get('lastName','')}".strip() or f"#{patient['id']}"
        return f"{who}'s next appointment is {nxt}."
    return "I don't see your next appointment yet."

# ---------- grounding (quiet) ----------
def construe(text: str) -> Dict[str, Any]:
    r = requests.post(
        f"{PHENOML_BASE}/construe/extract",
        headers=HEADERS,
        json={"text": text, "target_systems": ["ICD10","SNOMED"]},
        timeout=30
    )
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, dict) else {}

def interpret_icd10(code: str) -> Dict[str, Any]:
    params = {"sf": "code,name", "terms": code}
    r = requests.get(ICD10_SEARCH, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    if len(data) >= 4 and isinstance(data[3], list) and data[3]:
        for row in data[3]:
            if isinstance(row, list) and len(row) >= 2 and str(row[0]).upper() == code.upper():
                return {"system":"ICD-10-CM","code":code,"display":row[1]}
        row = data[3][0]
        return {"system":"ICD-10-CM","code":row[0] or code,"display":row[1] if len(row)>1 else ""}
    return {"system":"ICD-10-CM","code":code,"display":""}

def interpret_snomed(code: str) -> Dict[str, Any]:
    params = {"system":"http://snomed.info/sct","code":code}
    r = requests.get(SNOMED_FHIR_LOOKUP, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    display = ""
    for p in data.get("parameter", []):
        if p.get("name") == "display":
            display = p.get("valueString") or display
    return {"system":"SNOMED CT","code":code,"display":display}

def enrich_terms(cj: Dict[str, Any]) -> List[str]:
    """Return a small list of human-friendly displays (no codes)."""
    terms: List[str] = []
    if not isinstance(cj, dict) or not cj:
        return terms
    # ICD-10 shaped
    if isinstance(cj.get("codes"), list):
        for c in cj["codes"]:
            if isinstance(c, dict) and c.get("code"):
                info = interpret_icd10(c["code"])
                if info.get("display"):
                    terms.append(info["display"])
    # generic
    if isinstance(cj.get("concepts"), list):
        for c in cj["concepts"]:
            if isinstance(c, dict) and c.get("code"):
                sys = (c.get("system") or "").upper()
                if sys.startswith("ICD"):
                    info = interpret_icd10(c["code"])
                else:
                    info = interpret_snomed(c["code"])
                if info.get("display"):
                    terms.append(info["display"])
    # de-dup, keep short
    seen = set()
    out = []
    for t in terms:
        if t and t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out[:5]

# ---------- optional OpenAI rephrasing ----------
def polish_with_openai(terms: List[str], user_text: str) -> str:
    if not OPENAI_API_KEY:
        return ""
    try:
        from openai import OpenAI
        client = OpenAI()
        human_terms = ", ".join(terms) if terms else ""
        payload = (
            f"User said: {user_text}\n"
            f"Standardized terms (human-readable, no codes): {human_terms}\n"
        )
        # try fast models
        for model in ("gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"):
            try:
                res = client.chat.completions.create(
                    model=model,
                    temperature=0.2,
                    messages=[
                        {"role":"system", "content": SYSTEM_TONE},
                        {"role":"user", "content": EXPLAIN_FROM_TERMS_PROMPT + "\n\n" + payload}
                    ]
                )
                text = (res.choices[0].message.content or "").strip()
                if text: return text
            except Exception:
                continue
        return ""
    except Exception:
        return ""

def simple_explainer(terms: List[str], user_text: str) -> str:
    if not terms:
        return (
            "Thanks for sharing. I can help, but I’ll need a bit more detail—"
            "for example: when it started, how severe it feels, and what makes it better or worse. "
            "This is not medical advice; please consult a licensed clinician."
        )
    # minimal human-friendly response
    readable = ", ".join(terms)
    return (
        f"Got it. From what you shared, this could relate to: {readable}. "
        "Can you tell me how long this has been going on, and whether it’s getting better, worse, or staying the same? "
        "This is not medical advice; please consult a licensed clinician."
    )

# ---------- intent parsing ----------
RE_BOOK = re.compile(r"\b(book|schedule|appointment|appt)\b", re.I)
RE_CANCEL = re.compile(r"\b(cancel|remove)\b.*\b(appointment|appt)\b", re.I)
RE_NAME = re.compile(r"\b(i am|i'm|my name is)\s+(.+)", re.I)
RE_ID = re.compile(r"#(\d+)")
RE_TIME = re.compile(r"\b(?:on|at|when)[:\s]*([0-9:\-\/\sA-Za-z]+)", re.I)
RE_DOC = re.compile(r"\bwith\s+(Dr\.?\s*\w+|\w+\s\w+)\b", re.I)
RE_SHOW_NEXT = re.compile(r"\b(when|what).*next.*appointment\b", re.I)

# ---------- dialog context ----------
ctx = {
    "name": None,
    "patient_id": None,
    "last_terms": [],
    "pending": {
        "booking": False,
        "when": None,
        "doctor": None
    }
}

# ---------- conversation engine ----------
def handle_message(text: str):
    # greetings
    if re.search(r"\b(hi|hello|hey)\b", text, re.I):
        if not ctx.get("name"):
            say("hey — how are you feeling today?")
        else:
            say(f"hey {ctx['name'].split()[0].lower()} — what can i do for you?")
        return

    # capture name (e.g., "my name is Drake")
    mname = RE_NAME.search(text)
    if mname:
        name = mname.group(2).strip().rstrip(".")
        patient = ensure_patient(name, ctx)
        if patient:
            say(f"got it, {ctx['name']}. i saved your profile.")
        else:
            say("thanks — I’ll remember that.")
        # if we were waiting to book and have a time, proceed
        if ctx["pending"]["booking"] and ctx["pending"]["when"]:
            _do_booking_flow()
        return

    # ask for next appointment
    if RE_SHOW_NEXT.search(text):
        # ensure a patient (use current ctx)
        if not ctx.get("patient_id"):
            say("sure — what name should i look under?")
            ctx["pending"]["booking"] = False
            return
        db = _load_db()
        p, _ = find_patient(db, ctx["patient_id"])
        if p:
            say(next_appt_text(p))
        else:
            say("i couldn’t find your profile yet — what’s your name?")
        return

    # cancel appointment
    if RE_CANCEL.search(text):
        if not ctx.get("patient_id"):
            say("okay — what name should i cancel under?")
            return
        db = _load_db()
        p, _ = find_patient(db, ctx["patient_id"])
        if not p:
            say("i couldn't find your profile — what's your name?")
            return
        say("one sec…")
        time.sleep(0.8)
        say(cancel_next_appointment(p))
        return

    # booking intent
    if RE_BOOK.search(text):
        # collect time and doctor if present
        mtime = RE_TIME.search(text)
        mdoc = RE_DOC.search(text)
        when = mtime.group(1).strip() if mtime else None
        doctor = mdoc.group(1).strip() if mdoc else None

        ctx["pending"]["booking"] = True
        if when: ctx["pending"]["when"] = when
        if doctor: ctx["pending"]["doctor"] = doctor

        # do we know the patient already?
        if not ctx.get("patient_id"):
            # see if an ID was mentioned
            mid = RE_ID.search(text)
            if mid:
                db = _load_db()
                p, _ = find_patient(db, mid.group(1))
                if p:
                    ctx["patient_id"] = p["id"]
                    ctx["name"] = f"{p.get('firstName','')} {p.get('lastName','')}".strip()
                else:
                    say("i couldn't find that ID — what's your name for the booking?")
                    return
            else:
                say("sure — what name should i put the appointment under?")
                return

        # if we have name but not time, ask
        if not ctx["pending"]["when"]:
            say("got it — what time works for you? (e.g., 2025-08-24 10:30)")
            return

        # proceed to booking
        _do_booking_flow()
        return

    # if user drops a name only (e.g., "drake"), interpret as identification
    if len(text.split()) <= 3 and text[0].isalpha() and (" " in text):
        maybe_name = text.strip().rstrip(".")
        # don’t override if it's likely a symptom
        if not RE_BOOK.search(text) and not RE_CANCEL.search(text):
            patient = ensure_patient(maybe_name, ctx)
            if patient:
                say(f"thanks, {ctx['name']}. how can i help today?")
                return

    # fallback: treat as symptoms. Ground quietly, then explain.
    _symptom_flow(text)

def _do_booking_flow():
    db = _load_db()
    p, _ = find_patient(db, ctx["patient_id"])
    if not p:
        say("i couldn’t find your profile — what’s your name?")
        return
    if not ctx["pending"]["when"]:
        say("what time should i try for?")
        return
    say("got it — give me a moment…")
    time.sleep(0.9)
    msg = book_appointment_for(p, ctx["pending"]["when"], ctx["pending"]["doctor"])
    say(msg)
    # clear booking intent
    ctx["pending"] = {"booking": False, "when": None, "doctor": None}

def _symptom_flow(user_text: str):
    # ground quietly
    terms: List[str] = []
    try:
        cj = construe(user_text)
        terms = enrich_terms(cj)
    except Exception:
        terms = []

    # polish with OpenAI if available
    reply = polish_with_openai(terms, user_text)
    if not reply:
        reply = simple_explainer(terms, user_text)

    # conversational feel
    # add a gentle follow-up to offer booking if user sounds like they want help soon
    if re.search(r"\b(asap|soon|urgent|now|today|tomorrow)\b", user_text, re.I):
        reply += "\n\nif you’d like, i can try to book you the earliest available slot. want me to check?"

    say(reply)

# ---------- main loop ----------
def main():
    # opening tone
    say("hey — how can i help today?")
    while True:
        try:
            text = input("> ").strip()
        except KeyboardInterrupt:
            print("\nbye"); break
        if not text:
            continue
        if text.lower() in ("exit","quit","bye"):
            say("take care — and remember this chat isn’t medical advice. see a clinician if you’re worried.")
            break
        handle_message(text)

if __name__ == "__main__":
    main()
