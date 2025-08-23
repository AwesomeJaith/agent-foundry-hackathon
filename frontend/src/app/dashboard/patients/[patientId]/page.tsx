"use client";

import { useParams } from "next/navigation";
import { patientsDatabase } from "@/dummyDatabase/database";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function PatientDetailsPage() {
  const params = useParams();
  const patientId = params.patientId;

  const patient = patientsDatabase.find((p) => p.id === patientId);

  if (!patient) return <div>Patient not found</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
      {/* Patient Basic Info */}
      <Card>
        <CardContent>
          <div className="flex flex-col gap-4">
            <div className="font-semibold text-lg">
              {patient.firstName} {patient.lastName}
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <h2 className="font-medium">Sex</h2>
                <p>
                  {patient.gender.charAt(0).toUpperCase() +
                    patient.gender.slice(1)}
                </p>
              </div>
              <div>
                <h2 className="font-medium">Date of Birth</h2>
                <p>{patient.dateOfBirth}</p>
              </div>
              <div>
                <h2 className="font-medium">Phone</h2>
                <p>{patient.phoneNumber}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Insurance & Payment */}
      <Card>
        <CardHeader>
          <CardTitle>Insurance & Payment</CardTitle>
          <CardDescription>
            Insurance provider, member ID, and payment options
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-2">
            <p>
              <span className="font-semibold">Provider:</span>{" "}
              {patient.insuranceProvider || "N/A"}
            </p>
            <p>
              <span className="font-semibold">Member ID:</span>{" "}
              {patient.memberId || "N/A"}
            </p>
            <p>
              <span className="font-semibold">Policy Holder:</span>{" "}
              {patient.policyHolder || "N/A"}
            </p>
            <p>
              <span className="font-semibold">Payment Option:</span>{" "}
              {patient.paymentOption || "Self-pay"}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Visits / History */}
      <Card>
        <CardHeader>
          <CardTitle>History</CardTitle>
          <CardDescription>
            Past visits, phone calls, emails, family and medical history
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-2">
            <p>
              <span className="font-semibold">Phone Calls:</span>{" "}
              {patient.phoneCalls || 0}
            </p>
            <p>
              <span className="font-semibold">Emails:</span>{" "}
              {patient.emails || 0}
            </p>
            <p>
              <span className="font-semibold">Family History:</span>{" "}
              {patient.familyHistory || "N/A"}
            </p>
            <p>
              <span className="font-semibold">Medical History:</span>{" "}
              {patient.medicalHistory || "N/A"}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Consent Forms */}
      <Card>
        <CardHeader>
          <CardTitle>Consent Forms</CardTitle>
          <CardDescription>Signed consent forms</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-2">
            {patient.consentForms?.length > 0 ? (
              patient.consentForms.map((form: string, index: number) => (
                <p key={index}>{form}</p>
              ))
            ) : (
              <p>No consent forms on file.</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
