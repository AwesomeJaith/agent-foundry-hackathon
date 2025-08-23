export interface SymptomReport {
  id: string;
  timestamp: string;
  reportedBy: "patient" | "ai" | "caregiver" | "doctor";
  source: "chat" | "phone" | "email" | "visit" | "ai_analysis";
  symptoms: {
    description: string;
    severity: "mild" | "moderate" | "severe" | "critical";
    duration?: string;
    frequency?: string;
    triggers?: string[];
  }[];
  aiAnalysis?: {
    summary: string;
    urgency: "low" | "medium" | "high" | "urgent";
    suggestedActions: string[];
    confidence: number; // 0-100
    relatedConditions?: string[];
  };
  status: "new" | "reviewed" | "in_progress" | "resolved" | "addressed";
  assignedTo?: string;
  notes?: string;
  attachments?: {
    type: "transcript" | "recording" | "document" | "image";
    url: string;
    description: string;
  }[];
}

export interface Patient {
  id: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  gender: "male" | "female" | "other";
  phoneNumber: string;
  email?: string;
  address?: {
    street: string;
    city: string;
    state: string;
    zipCode: string;
  };
  insuranceProvider?: string;
  memberId?: string;
  policyHolder?: string;
  paymentOption?: string;
  phoneCalls?: number;
  emails?: number;
  familyHistory?: string;
  medicalHistory?: string;
  consentForms?: string[];
  allergies?: string[];
  medications?: string[];
  conditions?: string[];
  lastVisit?: string;
  nextAppointment?: string;
  symptomReports?: SymptomReport[];
  aiSummary?: string;
}

export const patientsDatabase: Patient[] = [
  {
    id: "1",
    firstName: "Emily",
    lastName: "Johnson",
    dateOfBirth: "1990-05-12",
    gender: "female",
    phoneNumber: "555-123-4567",
    email: "emily.johnson@email.com",
    address: {
      street: "123 Oak Street",
      city: "Springfield",
      state: "IL",
      zipCode: "62701",
    },
    insuranceProvider: "Blue Cross Blue Shield",
    memberId: "BCBS123456789",
    policyHolder: "Emily Johnson",
    paymentOption: "Insurance",
    phoneCalls: 3,
    emails: 2,
    familyHistory: "Father: Hypertension, Mother: Diabetes",
    medicalHistory: "Seasonal allergies, mild asthma",
    consentForms: [
      "Treatment Consent",
      "HIPAA Privacy Notice",
      "Financial Agreement",
    ],
    allergies: ["Penicillin", "Pollen"],
    medications: ["Albuterol inhaler", "Cetirizine"],
    conditions: ["Asthma", "Seasonal allergies"],
    lastVisit: "2024-01-15",
    nextAppointment: "2024-03-20",
    aiSummary:
      "Patient shows signs of mild anxiety and stress-related symptoms. Recommended follow-up in 2 weeks.",
    symptomReports: [
      {
        id: "sr-001",
        timestamp: "2024-03-18T10:30:00Z",
        reportedBy: "ai",
        source: "ai_analysis",
        symptoms: [
          {
            description: "Persistent headaches for the past week",
            severity: "moderate",
            duration: "7 days",
            frequency: "Daily",
            triggers: ["Stress", "Screen time"],
          },
          {
            description: "Difficulty sleeping (4-5 hours per night)",
            severity: "moderate",
            duration: "2 weeks",
            frequency: "Every night",
            triggers: ["Anxiety", "Work stress"],
          },
          {
            description: "Increased stress and anxiety levels",
            severity: "moderate",
            duration: "3 weeks",
            frequency: "Continuous",
            triggers: ["Work pressure", "Personal issues"],
          },
        ],
        aiAnalysis: {
          summary:
            "Patient exhibiting symptoms consistent with stress-related anxiety and sleep disturbances. Headaches appear to be tension-related.",
          urgency: "medium",
          suggestedActions: [
            "Schedule follow-up appointment within 1 week",
            "Consider stress management techniques",
            "Monitor sleep patterns and document changes",
            "Evaluate work-life balance",
          ],
          confidence: 85,
          relatedConditions: [
            "Anxiety",
            "Sleep disorders",
            "Tension headaches",
          ],
        },
        status: "new",
        assignedTo: "Dr. Smith",
        notes:
          "Patient has history of seasonal allergies but current symptoms appear stress-related.",
        attachments: [
          {
            type: "transcript",
            url: "/transcripts/emily-johnson-2024-03-18",
            description: "Chat conversation with patient",
          },
        ],
      },
      {
        id: "sr-001-past",
        timestamp: "2024-02-15T14:20:00Z",
        reportedBy: "patient",
        source: "visit",
        symptoms: [
          {
            description: "Seasonal allergy symptoms",
            severity: "moderate",
            duration: "2 weeks",
            frequency: "Daily",
            triggers: ["Pollen", "Dust"],
          },
        ],
        aiAnalysis: {
          summary:
            "Patient experiencing typical seasonal allergy symptoms consistent with spring pollen exposure.",
          urgency: "low",
          suggestedActions: [
            "Continue current allergy medication",
            "Recommend air purifier for home",
            "Schedule follow-up if symptoms worsen",
          ],
          confidence: 90,
          relatedConditions: ["Seasonal allergies"],
        },
        status: "addressed",
        assignedTo: "Dr. Smith",
        notes:
          "Prescribed Cetirizine 10mg daily. Symptoms resolved within 1 week.",
        attachments: [
          {
            type: "document",
            url: "/documents/emily-johnson-allergy-treatment-2024-02",
            description: "Allergy treatment plan",
          },
        ],
      },
    ],
  },
  {
    id: "2",
    firstName: "Michael",
    lastName: "Anderson",
    dateOfBirth: "1984-11-23",
    gender: "male",
    phoneNumber: "555-234-5678",
    email: "michael.anderson@email.com",
    address: {
      street: "456 Pine Avenue",
      city: "Chicago",
      state: "IL",
      zipCode: "60601",
    },
    insuranceProvider: "Aetna",
    memberId: "AET987654321",
    policyHolder: "Michael Anderson",
    paymentOption: "Insurance",
    phoneCalls: 1,
    emails: 0,
    familyHistory: "No significant family history",
    medicalHistory: "Hypertension, controlled with medication",
    consentForms: ["Treatment Consent", "HIPAA Privacy Notice"],
    allergies: ["None known"],
    medications: ["Lisinopril 10mg daily"],
    conditions: ["Hypertension"],
    lastVisit: "2024-02-10",
    nextAppointment: "2024-05-15",
    aiSummary:
      "Patient's blood pressure readings show slight elevation. Monitoring recommended.",
    symptomReports: [
      {
        id: "sr-002",
        timestamp: "2024-03-17T14:20:00Z",
        reportedBy: "patient",
        source: "phone",
        symptoms: [
          {
            description: "Elevated blood pressure readings",
            severity: "mild",
            duration: "3 days",
            frequency: "Daily readings",
            triggers: ["Stress", "Caffeine"],
          },
          {
            description: "Mild dizziness when standing",
            severity: "mild",
            duration: "2 days",
            frequency: "Occasional",
            triggers: ["Rapid position changes"],
          },
        ],
        aiAnalysis: {
          summary:
            "Patient reporting elevated BP readings above normal range. Symptoms consistent with mild hypertension.",
          urgency: "medium",
          suggestedActions: [
            "Verify blood pressure readings with office visit",
            "Review current medication effectiveness",
            "Recommend lifestyle modifications",
            "Schedule follow-up within 1 week",
          ],
          confidence: 78,
          relatedConditions: ["Hypertension", "Orthostatic hypotension"],
        },
        status: "addressed",
        assignedTo: "Dr. Johnson",
        notes:
          "Patient has been on Lisinopril for 6 months. Dosage adjusted to 15mg daily. Patient reports improvement in BP readings.",
        attachments: [
          {
            type: "recording",
            url: "/recordings/michael-anderson-2024-03-17",
            description: "Phone call recording",
          },
        ],
      },
    ],
  },
  {
    id: "3",
    firstName: "Sophia",
    lastName: "Martinez",
    dateOfBirth: "2001-03-17",
    gender: "female",
    phoneNumber: "555-345-6789",
    email: "sophia.martinez@email.com",
    address: {
      street: "789 Elm Drive",
      city: "Peoria",
      state: "IL",
      zipCode: "61601",
    },
    insuranceProvider: "UnitedHealth",
    memberId: "UHC456789123",
    policyHolder: "Maria Martinez (Mother)",
    paymentOption: "Insurance",
    phoneCalls: 5,
    emails: 3,
    familyHistory: "Mother: Migraines, Father: Heart disease",
    medicalHistory: "Migraines, anxiety",
    consentForms: [
      "Treatment Consent",
      "HIPAA Privacy Notice",
      "Mental Health Consent",
    ],
    allergies: ["Sulfa drugs"],
    medications: ["Sumatriptan", "Sertraline"],
    conditions: ["Migraines", "Anxiety"],
    lastVisit: "2024-01-30",
    nextAppointment: "2024-04-12",
    aiSummary:
      "Patient experiencing increased migraine frequency. Current medication may need adjustment.",
    symptomReports: [
      {
        id: "sr-003",
        timestamp: "2024-03-19T09:15:00Z",
        reportedBy: "ai",
        source: "chat",
        symptoms: [
          {
            description: "Severe migraine with aura",
            severity: "severe",
            duration: "6 hours",
            frequency: "3 times this week",
            triggers: ["Stress", "Bright lights", "Lack of sleep"],
          },
          {
            description: "Nausea and vomiting",
            severity: "moderate",
            duration: "4 hours",
            frequency: "With each migraine",
            triggers: ["Severe headache"],
          },
          {
            description: "Sensitivity to light and sound",
            severity: "severe",
            duration: "6 hours",
            frequency: "With each migraine",
            triggers: ["Migraine onset"],
          },
        ],
        aiAnalysis: {
          summary:
            "Patient experiencing severe migraine episodes with classic aura symptoms. Frequency has increased significantly.",
          urgency: "high",
          suggestedActions: [
            "Immediate medication review and adjustment",
            "Consider preventive migraine medication",
            "Schedule urgent follow-up appointment",
            "Evaluate trigger factors and lifestyle modifications",
            "Consider referral to neurologist if symptoms persist",
          ],
          confidence: 92,
          relatedConditions: ["Migraine with aura", "Chronic migraine"],
        },
        status: "new",
        assignedTo: "Dr. Williams",
        notes:
          "Patient has been on Sumatriptan but frequency suggests need for preventive treatment.",
        attachments: [
          {
            type: "transcript",
            url: "/transcripts/sophia-martinez-2024-03-19",
            description: "Chat conversation with patient",
          },
          {
            type: "document",
            url: "/documents/sophia-martinez-migraine-log",
            description: "Patient's migraine symptom log",
          },
        ],
      },
    ],
  },
  {
    id: "4",
    firstName: "Daniel",
    lastName: "Lee",
    dateOfBirth: "1978-07-04",
    gender: "male",
    phoneNumber: "555-456-7890",
    email: "daniel.lee@email.com",
    address: {
      street: "321 Maple Lane",
      city: "Rockford",
      state: "IL",
      zipCode: "61101",
    },
    insuranceProvider: "Cigna",
    memberId: "CIG789123456",
    policyHolder: "Daniel Lee",
    paymentOption: "Insurance",
    phoneCalls: 2,
    emails: 1,
    familyHistory: "Father: Prostate cancer, Mother: Osteoporosis",
    medicalHistory: "Type 2 diabetes, high cholesterol",
    consentForms: [
      "Treatment Consent",
      "HIPAA Privacy Notice",
      "Diabetes Management",
    ],
    allergies: ["None known"],
    medications: ["Metformin", "Atorvastatin"],
    conditions: ["Type 2 Diabetes", "High Cholesterol"],
    lastVisit: "2024-02-05",
    nextAppointment: "2024-05-01",
  },
  {
    id: "5",
    firstName: "Sarah",
    lastName: "Williams",
    dateOfBirth: "1995-09-28",
    gender: "female",
    phoneNumber: "555-567-8901",
    email: "sarah.williams@email.com",
    address: {
      street: "654 Birch Road",
      city: "Naperville",
      state: "IL",
      zipCode: "60540",
    },
    insuranceProvider: "Humana",
    memberId: "HUM321654987",
    policyHolder: "Sarah Williams",
    paymentOption: "Insurance",
    phoneCalls: 0,
    emails: 0,
    familyHistory: "No significant family history",
    medicalHistory: "Healthy, routine checkups only",
    consentForms: ["Treatment Consent", "HIPAA Privacy Notice"],
    allergies: ["None known"],
    medications: ["None"],
    conditions: ["None"],
    lastVisit: "2024-01-20",
    nextAppointment: "2024-07-15",
  },
];
