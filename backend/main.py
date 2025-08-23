# main.py
# Intelligent conversational loop with dynamic intent recognition and function routing.
# Now with audio support for voice conversations!

import json
import re
import time
import asyncio
import os
from typing import Dict, Any, Optional, List, Callable
import agents as A
import audio

# Global context
ctx = {
    "patient_id": None,
    "patient_name": None,
    "pending": {"mode": "none", "when": None, "doctor": None},
    "cache": {"last_symptom_text": None, "last_terms": []},
    "conversation_history": [],
    "audio_mode": False,
    "audio_manager": None
}

def say(s: str): 
    """Output response to user - text only (audio handled separately in async context)"""
    print(s.strip())
    ctx["conversation_history"].append({"role": "assistant", "content": s.strip()})

async def speak_async(text: str):
    """Async wrapper for speaking text"""
    try:
        await audio.speak(text)
    except Exception as e:
        print(f"Speech error: {e}")

def log_user_input(text: str):
    """Log user input to conversation history"""
    ctx["conversation_history"].append({"role": "user", "content": text})

async def listen_for_input() -> str:
    """Listen for audio input and return transcribed text"""
    if not ctx["audio_mode"]:
        return input("> ").strip()
    
    try:
        print("🎤 Listening... (speak now)")
        
        # Record and transcribe audio - continuous listening
        text = await audio.listen(duration=15, use_silence_detection=True)
        
        if text and text.strip():
            print(f"You said: {text}")
            return text.strip()
        else:
            print("🔇 No speech detected, listening again...")
            # Try again automatically
            return await listen_for_input()
        
    except Exception as e:
        print(f"Audio input error: {e}")
        print("Falling back to text input...")
        return input("> ").strip()

# -------- Intent Classification --------
def classify_intent(text: str) -> Dict[str, Any]:
    """Classify user intent using OpenAI API with smart context and fast reasoning"""
    if not A.OPENAI_API_KEY:
        return {"intent": "general_conversation", "confidence": 0.2, "extracted_info": {}}
    
    # Get conversation context efficiently
    context_info = ""
    if ctx["pending"]["mode"] != "none":
        context_info += f"CURRENT_STATE: {ctx['pending']['mode']} mode. "
    
    if ctx["patient_id"]:
        context_info += f"KNOWN_PATIENT: {ctx['patient_name']}. "
    
    # Get last assistant message for immediate context
    last_assistant_msg = ""
    if len(ctx["conversation_history"]) > 0:
        for msg in reversed(ctx["conversation_history"]):
            if msg["role"] == "assistant":
                last_assistant_msg = msg["content"]
                break
    
    # Streamlined, fast classification prompt
    system_prompt = f"""Fast medical appointment intent classifier. Analyze user message with context.
    
    CONTEXT: {context_info}
    LAST_BOT_MSG: "{last_assistant_msg}"
    
    INTENTS: greeting, identify, book_appointment, cancel_appointment, check_appointment, symptoms, general_conversation
    
    SMART RULES:
    - "yes/sure/please" after booking question → book_appointment
    - Name after name request → identify
    - Symptoms/illness → symptoms  
    - Book/schedule → book_appointment
    - Cancel → cancel_appointment
    - Check/next appointment → check_appointment
    - Confused responses like "what?", "huh?", "???" → general_conversation
    - Single letters or unclear text → general_conversation
    
    EXTRACT: patient_name, patient_id, time_preference, doctor_preference, symptoms_described
    
    IMPORTANT: If user seems confused or gives unclear responses, classify as general_conversation, NOT booking.
    
    JSON: {{"intent":"...", "confidence":0.0-1.0, "extracted_info":{{...}}}}"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]
    
    # Fast call with optimized parameters
    response = A.call_openai_chat(messages, model="gpt-4o-mini", max_tokens=150, temperature=0.0)
    if response:
        try:
            result = json.loads(response)
            # Ensure we have required fields
            if "intent" not in result:
                result["intent"] = "general_conversation"
            if "confidence" not in result:
                result["confidence"] = 0.5
            if "extracted_info" not in result:
                result["extracted_info"] = {}
            return result
        except json.JSONDecodeError:
            print(f"Failed to parse OpenAI response: {response}")
    
    # Simple fallback
    return {"intent": "general_conversation", "confidence": 0.3, "extracted_info": {}}

def _fallback_intent_classification(text: str) -> Dict[str, Any]:
    """Fallback intent classification using OpenAI with simplified context"""
    if not A.OPENAI_API_KEY:
        return {"intent": "general_conversation", "confidence": 0.3, "extracted_info": {}}
    
    # Get conversation context
    context_info = ""
    if ctx["pending"]["mode"] != "none":
        context_info += f"CURRENT STATE: User is in {ctx['pending']['mode']} mode. "
    
    if ctx["patient_id"]:
        context_info += f"KNOWN PATIENT: {ctx['patient_name']} (ID: {ctx['patient_id']}). "
    
    # Get last assistant message for context
    last_assistant_msg = ""
    if len(ctx["conversation_history"]) > 0:
        for msg in reversed(ctx["conversation_history"]):
            if msg["role"] == "assistant":
                last_assistant_msg = msg["content"]
                break
    
    # Create a simple, fast classification prompt
    system_prompt = f"""You are a fast intent classifier for a medical appointment system. 
    Classify this user message and extract key information.
    
    CONTEXT: {context_info}
    LAST ASSISTANT MESSAGE: "{last_assistant_msg}"
    
    Intents: greeting, identify, book_appointment, cancel_appointment, check_appointment, symptoms, general_conversation
    
    RULES:
    - If user says "yes/sure/please" after being asked about booking → book_appointment
    - If user provides a name after being asked for name → identify  
    - If user mentions symptoms/feeling sick → symptoms
    - If user wants to book/schedule → book_appointment
    - If user wants to cancel → cancel_appointment
    - If user asks about next appointment → check_appointment
    
    Extract: patient_name, patient_id, time_preference, doctor_preference, symptoms_described
    
    Respond with JSON: {{"intent": "...", "confidence": 0.0-1.0, "extracted_info": {{...}}}}"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]
    
    # Use a faster, simpler call for fallback
    response = A.call_openai_chat(messages, model="gpt-4o-mini", max_tokens=100, temperature=0.0)
    if response:
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            pass
    
    # Ultimate fallback
    return {"intent": "general_conversation", "confidence": 0.2, "extracted_info": {}}

# -------- Action Handlers --------
def handle_greeting(text: str, intent_data: Dict[str, Any]) -> bool:
    """Handle greeting intents"""
    responses = [
        "Hey there! How can I help you today?",
        "Hi! What can I do for you?", 
        "Hello! How may I assist you?"
    ]
    import random
    say(random.choice(responses))
    return True

def handle_identify(text: str, intent_data: Dict[str, Any]) -> bool:
    """Handle patient identification"""
    extracted = intent_data.get("extracted_info", {})
    
    if "patient_id" in extracted:
        pid = extracted["patient_id"]
        p = A.get_patient_by_id(pid)
        if p:
            ctx["patient_id"] = p["id"]
            ctx["patient_name"] = p.get("firstName", "")
            say("Got it!")
            # Continue with pending booking if we were in booking mode
            if ctx["pending"]["mode"] == "booking":
                return handle_book_appointment(text, {"extracted_info": {}})
            return True
        else:
            say("I couldn't find that ID in our system.")
            return True
    
    if "patient_name" in extracted:
        name = extracted["patient_name"]
        p = A.ensure_patient_by_name(name)
        ctx["patient_id"] = p["id"]
        ctx["patient_name"] = p["firstName"]
        say(f"Got it, {ctx['patient_name']}!")
        # Continue with pending booking if we were in booking mode
        if ctx["pending"]["mode"] == "booking":
            return handle_book_appointment(text, {"extracted_info": {}})
        return True
    
    # If no name extracted, try to use the raw text as name
    if text.strip() and len(text.strip().split()) <= 3:  # Likely a name
        p = A.ensure_patient_by_name(text.strip())
        ctx["patient_id"] = p["id"]
        ctx["patient_name"] = p["firstName"]
        say(f"Got it, {ctx['patient_name']}!")
        # Continue with pending booking if we were in booking mode
        if ctx["pending"]["mode"] == "booking":
            return handle_book_appointment(text, {"extracted_info": {}})
        return True
    
    say("I didn't catch your name or ID. Could you tell me again?")
    return True

def handle_book_appointment(text: str, intent_data: Dict[str, Any]) -> bool:
    """Handle appointment booking with improved flow and confirmation"""
    extracted = intent_data.get("extracted_info", {})
    
    when = extracted.get("time_preference")
    doctor = extracted.get("doctor_preference")
    
    # If we're already in booking mode, collect missing info
    if ctx["pending"]["mode"] == "booking":
        if when:
            ctx["pending"]["when"] = when
        if doctor:
            ctx["pending"]["doctor"] = doctor
        
        # Check if we have everything we need
        if not ctx["patient_id"]:
            say("What name should I put the appointment under?")
            return True
        if not ctx["pending"]["when"]:
            say("What time would work best for you?")
            return True
        
        # We have everything - confirm and book ONCE
        p = A.get_patient_by_id(ctx["patient_id"])
        if p:
            confirm_msg = f"Perfect! Let me confirm: booking an appointment for {ctx['patient_name']}"
            if ctx["pending"]["when"]:
                confirm_msg += f" {ctx['pending']['when']}"
            if ctx["pending"]["doctor"]:
                confirm_msg += f" with {ctx['pending']['doctor']}"
            confirm_msg += "."
            
            say(confirm_msg)
            say(A.book_appointment(p, ctx["pending"]["when"], ctx["pending"]["doctor"]))
            
            # IMPORTANT: Clear pending state to prevent duplicate bookings
            ctx["pending"] = {"mode": "none", "when": None, "doctor": None}
        return True
    
    # Start new booking process
    if not ctx["patient_id"]:
        ctx["pending"] = {"mode": "booking", "when": when, "doctor": doctor}
        say("I'd be happy to book an appointment for you! What name should I put it under?")
        return True
    
    if not when:
        ctx["pending"] = {"mode": "booking", "when": None, "doctor": doctor}
        say(f"Great, {ctx['patient_name']}! What time would work best for you?")
        return True
    
    # We have patient and time - confirm and book ONCE
    p = A.get_patient_by_id(ctx["patient_id"])
    if p:
        confirm_msg = f"Perfect! Let me book an appointment for {ctx['patient_name']} {when}"
        if doctor:
            confirm_msg += f" with {doctor}"
        confirm_msg += "."
        
        say(confirm_msg)
        say(A.book_appointment(p, when, doctor))
        
        # IMPORTANT: Clear any pending state
        ctx["pending"] = {"mode": "none", "when": None, "doctor": None}
    return True

def handle_cancel_appointment(text: str, intent_data: Dict[str, Any]) -> bool:
    """Handle appointment cancellation"""
    if not ctx["patient_id"]:
        say("What name should I cancel the appointment under?")
        return True
    
    p = A.get_patient_by_id(ctx["patient_id"])
    if p:
        say(A.cancel_next(p))
    return True

def handle_check_appointment(text: str, intent_data: Dict[str, Any]) -> bool:
    """Handle appointment checking"""
    if not ctx["patient_id"]:
        say("What name should I check appointments under?")
        return True
    
    p = A.get_patient_by_id(ctx["patient_id"])
    if p:
        say(A.next_appt(p))
    return True

def handle_symptoms(text: str, intent_data: Dict[str, Any]) -> bool:
    """Handle symptom reporting with better booking transition"""
    symptoms_text = intent_data.get("extracted_info", {}).get("symptoms_described", text)
    
    if symptoms_text == ctx["cache"]["last_symptom_text"]:
        terms = ctx["cache"]["last_terms"]
    else:
        try:
            terms = A.enrich_terms(A.construe(symptoms_text))
        except:
            terms = []
        ctx["cache"]["last_symptom_text"] = symptoms_text
        ctx["cache"]["last_terms"] = terms
        
        if terms and ctx["patient_id"]:
            p = A.get_patient_by_id(ctx["patient_id"])
            if p:
                A.add_condition(p, terms[0])
    
    # Set up for potential booking
    ctx["pending"] = {"mode": "booking", "when": None, "doctor": None}
    
    if terms:
        say(f"I'm sorry to hear you're experiencing {', '.join(terms)}. Would you like me to book you an appointment to see a doctor?")
    else:
        say("I understand you're not feeling well. Would you like me to book you an appointment to see a doctor?")
    return True

def handle_general_conversation(text: str, intent_data: Dict[str, Any]) -> bool:
    """Handle general conversation with contextual responses"""
    text_lower = text.lower().strip()
    
    # Handle confused responses
    if any(word in text_lower for word in ["what", "huh", "?", "confused", "don't understand"]):
        if ctx["patient_id"] and ctx["patient_id"]:
            # Check if they have a recent appointment
            p = A.get_patient_by_id(ctx["patient_id"])
            if p and p.get("nextAppointment"):
                say(f"You're all set, {ctx['patient_name']}! I just booked your appointment {p.get('nextAppointment')}. Is there anything else you need?")
                return True
        
        say("Sorry if I was unclear! Let me know what you'd like to do - I can help you book appointments, check your schedule, or answer medical questions.")
        return True
    
    # Generate contextual response based on conversation state
    if ctx["patient_id"]:
        responses = [
            f"I'm here to help, {ctx['patient_name']}. Is there anything specific you need assistance with?",
            "What else can I help you with today?",
            "Is there anything medical-related I can assist you with?"
        ]
    else:
        responses = [
            "I'm here to help with medical appointments and questions. How can I assist you?",
            "I can help you book appointments, check your schedule, or answer medical questions. What would you like to do?",
            "How can I help you today? I can assist with appointments or medical concerns."
        ]
    
    import random
    say(random.choice(responses))
    return True

# -------- Intent Router --------
INTENT_HANDLERS: Dict[str, Callable[[str, Dict[str, Any]], bool]] = {
    "greeting": handle_greeting,
    "identify": handle_identify,
    "book_appointment": handle_book_appointment,
    "cancel_appointment": handle_cancel_appointment,
    "check_appointment": handle_check_appointment,
    "symptoms": handle_symptoms,
    "general_conversation": handle_general_conversation
}

def process_user_input(text: str) -> bool:
    """Process user input with intelligent intent recognition and routing"""
    log_user_input(text)
    
    # Classify the intent
    intent_data = classify_intent(text)
    intent = intent_data.get("intent", "general_conversation")
    confidence = intent_data.get("confidence", 0.0)
    
    # Debug info (can be removed in production)
    print(f"[DEBUG] Intent: {intent}, Confidence: {confidence:.2f}")
    
    # Route to appropriate handler
    handler = INTENT_HANDLERS.get(intent, handle_general_conversation)
    return handler(text, intent_data)

# -------- Audio Setup --------
def setup_audio_mode():
    """Setup audio mode with DeepGram API"""
    deepgram_key = A._clean(os.getenv("DEEPGRAM_API_KEY"))
    if not deepgram_key:
        print("⚠️  DEEPGRAM_API_KEY not found in environment variables.")
        print("   Add it to your .env file to enable audio mode.")
        return False
    
    try:
        audio.initialize_audio(deepgram_key)
        ctx["audio_mode"] = True
        print("🎤 Audio mode enabled! You can now speak to the AI.")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize audio: {e}")
        return False

# -------- Main Loop --------
async def main_async():
    """Async main conversational loop with audio support"""
    # Ask user for input mode
    print("Welcome to the Medical Appointment AI!")
    print("Choose your input mode:")
    print("1. Text mode (type your messages)")
    print("2. Audio mode (speak your messages)")
    
    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            ctx["audio_mode"] = False
            break
        elif choice == "2":
            if setup_audio_mode():
                break
            else:
                print("Falling back to text mode...")
                ctx["audio_mode"] = False
                break
        else:
            print("Please enter 1 or 2")
    
    # Welcome message
    welcome_msg = "Hey! How can I help you today?"
    if ctx["audio_mode"]:
        print(f"\n🤖 {welcome_msg}")
        await audio.speak(welcome_msg)
    else:
        say(welcome_msg)
    
    # Main conversation loop
    while True:
        try:
            # Get user input (audio or text)
            text = await listen_for_input()
        except KeyboardInterrupt:
            print("\nTake care!")
            break
            
        if not text:
            continue
            
        # Handle exit commands
        if text.lower() in ("exit", "quit", "bye", "goodbye", "stop", "end conversation", "that's all", "thank you goodbye"):
            farewell = "Take care! Have a great day!"
            if ctx["audio_mode"]:
                print(f"\n🤖 {farewell}")
                await audio.speak(farewell)
            else:
                say(farewell)
            break
        
        # Process the input with intelligent routing
        try:
            await process_user_input_async(text)
        except Exception as e:
            print(f"[ERROR] {e}")
            error_msg = "I'm sorry, I encountered an error. Could you try again?"
            if ctx["audio_mode"]:
                print(f"\n🤖 {error_msg}")
                await audio.speak(error_msg)
            else:
                say(error_msg)
    
    # Cleanup
    if ctx["audio_mode"]:
        audio.cleanup_audio()

async def process_user_input_async(text: str) -> bool:
    """Async version of process_user_input for audio support"""
    log_user_input(text)
    
    # Classify the intent
    intent_data = classify_intent(text)
    intent = intent_data.get("intent", "general_conversation")
    confidence = intent_data.get("confidence", 0.0)
    
    # Debug info (can be removed in production)
    print(f"[DEBUG] Intent: {intent}, Confidence: {confidence:.2f}")
    
    # Route to appropriate handler
    handler = INTENT_HANDLERS.get(intent, handle_general_conversation)
    
    # Handle the intent
    result = handler(text, intent_data)
    
    # If in audio mode, speak the last response
    if ctx["audio_mode"] and len(ctx["conversation_history"]) > 0:
        last_response = ctx["conversation_history"][-1]
        if last_response["role"] == "assistant":
            await audio.speak(last_response["content"])
            print("\n" + "="*50)  # Visual separator
    
    return result

def main():
    """Entry point - runs the async main loop"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
