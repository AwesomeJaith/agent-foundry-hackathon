#!/usr/bin/env python3
"""
Test script for the patient and symptom report extraction agent.
This demonstrates how to use the extraction functionality.
"""

import json
import agents as A
from main import process_transcript_endpoint, batch_process_transcripts

def test_single_transcript():
    """Test processing a single transcript"""
    
    # Sample transcript
    transcript = """
    Patient: Hi, I'm Emily Johnson. I'm 34 years old and I've been having some issues lately.
    
    Doctor: Hello Emily, what brings you in today?
    
    Patient: Well, I've been experiencing persistent headaches for the past week. They're pretty bad - I'd say moderate to severe. They happen daily, usually in the afternoon, and seem to be triggered by stress and looking at screens too long.
    
    Doctor: I see. How long do these headaches typically last?
    
    Patient: Usually 2-3 hours. I also haven't been sleeping well - only getting about 4-5 hours per night for the past two weeks. I think it's related to anxiety and work stress.
    
    Doctor: Are you taking any medications currently?
    
    Patient: Yes, I take an Albuterol inhaler for my asthma and Cetirizine for seasonal allergies. I'm allergic to penicillin and pollen.
    
    Doctor: Any family history of similar issues?
    
    Patient: My father has hypertension and my mother has diabetes.
    
    Doctor: Thank you for that information. Based on what you've described, these symptoms appear to be stress-related. I'd recommend scheduling a follow-up appointment within a week to monitor your progress.
    """
    
    # Process the transcript
    result = process_transcript_endpoint(transcript, "1")
    
    print("=== Single Transcript Processing Result ===")
    print(json.dumps(result, indent=2))
    
    return result

def test_batch_processing():
    """Test processing multiple transcripts"""
    
    transcripts = [
        {
            "transcript": """
            Patient: Hi, I'm Michael Anderson. I'm 39 and I've been monitoring my blood pressure at home.
            
            Doctor: Hello Michael, what have you been seeing with your blood pressure?
            
            Patient: Well, my readings have been elevated for the past 3 days - around 150/95. I've also been feeling a bit dizzy when I stand up quickly.
            
            Doctor: Are you still taking your Lisinopril?
            
            Patient: Yes, 10mg daily as prescribed. I've been on it for about 6 months.
            
            Doctor: I think we should adjust your dosage to 15mg daily and monitor your readings.
            """,
            "patient_id": "2"
        },
        {
            "transcript": """
            Patient: Hi, I'm Sophia Martinez. I'm 23 and I've been having terrible migraines.
            
            Doctor: Hello Sophia, tell me about these migraines.
            
            Patient: They're severe - with aura, and they last about 6 hours. I've had 3 this week alone. They come with nausea and vomiting, and I'm very sensitive to light and sound during them.
            
            Doctor: Are you taking any medication for them?
            
            Patient: I have Sumatriptan, but it's not helping much with the frequency. I also take Sertraline for anxiety.
            
            Doctor: Given the frequency and severity, I think we need to consider preventive medication.
            """,
            "patient_id": "3"
        }
    ]
    
    # Process the batch
    result = batch_process_transcripts(transcripts)
    
    print("\n=== Batch Processing Result ===")
    print(json.dumps(result, indent=2))
    
    return result

def test_extraction_only():
    """Test extraction without saving to database"""
    
    transcript = """
    Patient: Hi, I'm Sarah Williams. I'm 28 and I'm here for a routine checkup.
    
    Doctor: Hello Sarah, how have you been feeling?
    
    Patient: Pretty good overall. I'm healthy, no major issues. Just here for my annual physical.
    
    Doctor: Any changes in your health since last year?
    
    Patient: No, nothing significant. I exercise regularly and eat well.
    """
    
    # Extract data without saving
    result = A.extract_patient_and_symptoms_from_transcript(transcript, "5")
    
    print("\n=== Extraction Only Result ===")
    print(json.dumps(result, indent=2))
    
    return result

def main():
    """Run all tests"""
    print("Testing Patient and Symptom Report Extraction Agent")
    print("=" * 60)
    
    # Test 1: Single transcript processing
    test_single_transcript()
    
    # Test 2: Batch processing
    test_batch_processing()
    
    # Test 3: Extraction only
    test_extraction_only()
    
    print("\n" + "=" * 60)
    print("All tests completed!")

if __name__ == "__main__":
    main()
