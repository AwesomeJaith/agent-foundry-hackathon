# Patient JSON Schema for Medical Appointment AI

## Overview
This document describes the JSON structure used by the Medical Appointment AI system (`main.py`) for storing patient information and appointments.

## Core Schema

### Patient Object Structure

```json
{
  "id": "string",                    // Unique patient identifier (required)
  "firstName": "string",             // Patient's first name (required)
  "lastName": "string",              // Patient's last name (optional)
  "dateOfBirth": "YYYY-MM-DD",       // Birth date in ISO format (optional)
  "gender": "string",                // "male", "female", or "other" (optional)
  "phoneNumber": "string",           // Phone number (optional)
  "email": "string",                 // Email address (optional)
  "address": {                       // Address object (optional)
    "street": "string",
    "city": "string", 
    "state": "string",
    "zipCode": "string"
  },
  "insuranceProvider": "string",     // Insurance company name (optional)
  "memberId": "string",              // Insurance member ID (optional)
  "policyHolder": "string",          // Policy holder name (optional)
  "paymentOption": "string",         // "Insurance", "Cash", "Credit Card" (optional)
  "phoneCalls": number,              // Number of phone calls made (optional, default: 0)
  "emails": number,                  // Number of emails sent (optional, default: 0)
  "familyHistory": "string",         // Family medical history (optional)
  "medicalHistory": "string",        // Personal medical history (optional)
  "consentForms": ["string"],        // Array of signed consent forms (optional)
  "allergies": ["string"],           // Array of allergies (optional)
  "medications": ["string"],         // Array of current medications (optional)
  "conditions": ["string"],          // Array of medical conditions (required for AI)
  "lastVisit": "YYYY-MM-DD",         // Date of last visit (optional)
  "nextAppointment": "string|null",  // Next appointment description (required for AI)
  "appointments": [                  // Array of appointment objects (required for AI)
    {
      "when": "string",              // Appointment time/date description
      "doctor": "string|null",       // Doctor name (optional)
      "status": "string"             // "booked", "completed", "canceled"
    }
  ]
}
```

## Required Fields for AI System

The AI system (`main.py`) specifically requires these fields to function properly:

### Essential Fields:
- `id` - Used for patient identification
- `firstName` - Used for personalized responses
- `conditions` - Array to store diagnosed conditions from symptoms
- `appointments` - Array to store appointment history
- `nextAppointment` - Current upcoming appointment

### AI Workflow Fields:
- `conditions[]` - AI adds medical conditions here when symptoms are analyzed
- `appointments[].when` - AI stores appointment times here
- `appointments[].doctor` - AI stores doctor preferences here  
- `appointments[].status` - AI tracks appointment status ("booked", "completed", "canceled")
- `nextAppointment` - AI updates this with the most recent booking

## Sample Data Examples

### Minimal Patient (AI Compatible)
```json
{
  "id": "1",
  "firstName": "John",
  "lastName": "",
  "conditions": [],
  "appointments": [],
  "nextAppointment": null
}
```

### Complete Patient Record
```json
{
  "id": "1",
  "firstName": "Emily",
  "lastName": "Johnson",
  "dateOfBirth": "1990-05-12",
  "gender": "female",
  "phoneNumber": "555-123-4567",
  "email": "emily.johnson@email.com",
  "address": {
    "street": "123 Oak Street",
    "city": "Springfield",
    "state": "IL",
    "zipCode": "62701"
  },
  "insuranceProvider": "Blue Cross Blue Shield",
  "memberId": "BCBS123456789",
  "policyHolder": "Emily Johnson",
  "paymentOption": "Insurance",
  "phoneCalls": 3,
  "emails": 2,
  "familyHistory": "Father: Hypertension, Mother: Diabetes",
  "medicalHistory": "Seasonal allergies, mild asthma",
  "consentForms": [
    "Treatment Consent",
    "HIPAA Privacy Notice",
    "Financial Agreement"
  ],
  "allergies": [
    "Penicillin",
    "Pollen"
  ],
  "medications": [
    "Albuterol inhaler",
    "Cetirizine"
  ],
  "conditions": [
    "Asthma",
    "Seasonal allergies"
  ],
  "lastVisit": "2024-01-15",
  "nextAppointment": "2024-03-20 at 2:00 PM",
  "appointments": [
    {
      "when": "2024-03-20 at 2:00 PM",
      "doctor": "Dr. Smith",
      "status": "booked"
    },
    {
      "when": "2024-01-15 at 10:30 AM", 
      "doctor": "Dr. Johnson",
      "status": "completed"
    }
  ]
}
```

## AI System Behavior

### Patient Creation
When a new patient provides their name, the AI creates a minimal record:
```json
{
  "id": "auto-generated",
  "firstName": "extracted-name",
  "lastName": "",
  "conditions": [],
  "appointments": [],
  "nextAppointment": null
}
```

### Appointment Booking
When booking an appointment, the AI updates:
```json
{
  "nextAppointment": "user-specified-time",
  "appointments": [
    {
      "when": "user-specified-time",
      "doctor": "user-specified-doctor-or-null",
      "status": "booked"
    }
  ]
}
```

### Symptom Processing
When symptoms are reported, the AI may add to:
```json
{
  "conditions": ["AI-diagnosed-condition"]
}
```

## File Location
The patient data is stored in: `backend/patients.json`

## Data Persistence
- All changes are automatically saved to the JSON file
- The AI system reads/writes to this file in real-time
- Backup the file regularly to prevent data loss

## Usage with AI System
1. Ensure `patients.json` exists (empty array `[]` if starting fresh)
2. The AI will automatically create patient records as needed
3. All appointment bookings and medical conditions are stored automatically
4. Use the provided sample data for testing and development
