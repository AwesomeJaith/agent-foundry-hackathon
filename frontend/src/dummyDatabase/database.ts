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
