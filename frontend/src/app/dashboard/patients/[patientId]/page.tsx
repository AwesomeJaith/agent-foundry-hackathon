"use client";

import { useParams, useRouter } from "next/navigation";
import { patientsDatabase } from "@/dummyDatabase/database";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  ArrowLeft,
  Phone,
  Mail,
  Calendar,
  User,
  Shield,
  CreditCard,
  FileText,
  Activity,
  Pill,
  AlertTriangle,
  Stethoscope,
  FileCheck,
  MapPin,
  Plus,
  Edit,
} from "lucide-react";

export default function PatientDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const patientId = params.patientId;

  const patient = patientsDatabase.find((p) => p.id === patientId);

  if (!patient) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Patient Not Found
          </h1>
          <p className="text-gray-600 mb-4">
            The patient you're looking for doesn't exist.
          </p>
          <Button onClick={() => router.back()}>Go Back</Button>
        </div>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const formatPhone = (phone: string) => {
    const cleaned = phone.replace(/\D/g, "");
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
    if (match) {
      return `(${match[1]}) ${match[2]}-${match[3]}`;
    }
    return phone;
  };

  const calculateAge = (dateOfBirth: string) => {
    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (
      monthDiff < 0 ||
      (monthDiff === 0 && today.getDate() < birthDate.getDate())
    ) {
      age--;
    }
    return age;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.back()}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Patients</span>
              </Button>
              <Separator orientation="vertical" className="h-6" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {patient.firstName} {patient.lastName}
                </h1>
                <p className="text-sm text-gray-500">
                  Patient ID: {patient.id}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant="secondary">
                {calculateAge(patient.dateOfBirth)} years old
              </Badge>
              <Button variant="outline" size="sm">
                <Phone className="h-4 w-4 mr-2" />
                Call Patient
              </Button>
              <Button size="sm">
                <Mail className="h-4 w-4 mr-2" />
                Send Message
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Basic Info & Quick Actions */}
          <div className="lg:col-span-1 space-y-6">
            {/* Basic Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="h-5 w-5" />
                  <span>Basic Information</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                    <User className="h-8 w-8 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">
                      {patient.firstName} {patient.lastName}
                    </h3>
                    <p className="text-sm text-gray-500">Patient</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <Calendar className="h-4 w-4 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium">Date of Birth</p>
                      <p className="text-sm text-gray-600">
                        {formatDate(patient.dateOfBirth)}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <User className="h-4 w-4 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium">Gender</p>
                      <p className="text-sm text-gray-600 capitalize">
                        {patient.gender}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <Phone className="h-4 w-4 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium">Phone Number</p>
                      <p className="text-sm text-gray-600">
                        {formatPhone(patient.phoneNumber)}
                      </p>
                    </div>
                  </div>

                  {patient.email && (
                    <div className="flex items-center space-x-3">
                      <Mail className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium">Email</p>
                        <p className="text-sm text-gray-600">{patient.email}</p>
                      </div>
                    </div>
                  )}

                  {patient.address && (
                    <div className="flex items-center space-x-3">
                      <MapPin className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium">Address</p>
                        <p className="text-sm text-gray-600">
                          {patient.address.street}
                          <br />
                          {patient.address.city}, {patient.address.state}{" "}
                          {patient.address.zipCode}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full justify-start">
                  <Calendar className="h-4 w-4 mr-2" />
                  Schedule Appointment
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <FileText className="h-4 w-4 mr-2" />
                  View Records
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <CreditCard className="h-4 w-4 mr-2" />
                  Billing & Payments
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Mail className="h-4 w-4 mr-2" />
                  Send Message
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Edit className="h-4 w-4 mr-2" />
                  Edit Patient Info
                </Button>
              </CardContent>
            </Card>

            {/* Appointments */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Calendar className="h-5 w-5" />
                  <span>Appointments</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {patient.lastVisit && (
                  <div>
                    <h4 className="font-medium text-sm text-gray-500 mb-1">
                      Last Visit
                    </h4>
                    <p className="text-sm">{formatDate(patient.lastVisit)}</p>
                  </div>
                )}
                {patient.nextAppointment && (
                  <div>
                    <h4 className="font-medium text-sm text-gray-500 mb-1">
                      Next Appointment
                    </h4>
                    <p className="text-sm font-medium text-blue-600">
                      {formatDate(patient.nextAppointment)}
                    </p>
                  </div>
                )}
                <Button variant="outline" size="sm" className="w-full">
                  <Plus className="h-4 w-4 mr-2" />
                  Schedule New Appointment
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Detailed Information */}
          <div className="lg:col-span-2 space-y-6">
            {/* Insurance & Payment Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="h-5 w-5" />
                  <span>Insurance & Payment</span>
                </CardTitle>
                <CardDescription>
                  Insurance provider, member ID, and payment options
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-sm text-gray-500 mb-1">
                        Insurance Provider
                      </h4>
                      <p className="text-sm">
                        {patient.insuranceProvider || "Not specified"}
                      </p>
                    </div>
                    <div>
                      <h4 className="font-medium text-sm text-gray-500 mb-1">
                        Member ID
                      </h4>
                      <p className="text-sm font-mono">
                        {patient.memberId || "Not specified"}
                      </p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-sm text-gray-500 mb-1">
                        Policy Holder
                      </h4>
                      <p className="text-sm">
                        {patient.policyHolder || "Self"}
                      </p>
                    </div>
                    <div>
                      <h4 className="font-medium text-sm text-gray-500 mb-1">
                        Payment Option
                      </h4>
                      <Badge variant="outline">
                        {patient.paymentOption || "Self-pay"}
                      </Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Medical Conditions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Stethoscope className="h-5 w-5" />
                  <span>Medical Conditions</span>
                </CardTitle>
                <CardDescription>
                  Current and past medical conditions
                </CardDescription>
              </CardHeader>
              <CardContent>
                {patient.conditions && patient.conditions.length > 0 ? (
                  <div className="space-y-3">
                    {patient.conditions.map((condition, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg"
                      >
                        <div className="flex items-center space-x-3">
                          <Stethoscope className="h-4 w-4 text-red-600" />
                          <span className="text-sm font-medium">
                            {condition}
                          </span>
                        </div>
                        <Badge
                          variant="secondary"
                          className="bg-red-100 text-red-800"
                        >
                          Active
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Stethoscope className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      No Conditions
                    </h3>
                    <p className="text-gray-500 mb-4">
                      No medical conditions recorded.
                    </p>
                    <Button variant="outline" size="sm">
                      Add Condition
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Medications */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Pill className="h-5 w-5" />
                  <span>Current Medications</span>
                </CardTitle>
                <CardDescription>
                  Active medications and prescriptions
                </CardDescription>
              </CardHeader>
              <CardContent>
                {patient.medications && patient.medications.length > 0 ? (
                  <div className="space-y-3">
                    {patient.medications.map((medication, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg"
                      >
                        <div className="flex items-center space-x-3">
                          <Pill className="h-4 w-4 text-blue-600" />
                          <span className="text-sm font-medium">
                            {medication}
                          </span>
                        </div>
                        <Badge
                          variant="secondary"
                          className="bg-blue-100 text-blue-800"
                        >
                          Active
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Pill className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      No Medications
                    </h3>
                    <p className="text-gray-500 mb-4">
                      No current medications recorded.
                    </p>
                    <Button variant="outline" size="sm">
                      Add Medication
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Allergies */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <AlertTriangle className="h-5 w-5" />
                  <span>Allergies</span>
                </CardTitle>
                <CardDescription>Known allergies and reactions</CardDescription>
              </CardHeader>
              <CardContent>
                {patient.allergies && patient.allergies.length > 0 ? (
                  <div className="space-y-3">
                    {patient.allergies.map((allergy, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-yellow-50 border border-yellow-200 rounded-lg"
                      >
                        <div className="flex items-center space-x-3">
                          <AlertTriangle className="h-4 w-4 text-yellow-600" />
                          <span className="text-sm font-medium">{allergy}</span>
                        </div>
                        <Badge
                          variant="secondary"
                          className="bg-yellow-100 text-yellow-800"
                        >
                          Allergy
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <AlertTriangle className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      No Allergies
                    </h3>
                    <p className="text-gray-500 mb-4">
                      No known allergies recorded.
                    </p>
                    <Button variant="outline" size="sm">
                      Add Allergy
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Medical History */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Activity className="h-5 w-5" />
                  <span>Medical History</span>
                </CardTitle>
                <CardDescription>
                  Past visits, conditions, and medical information
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                      <Phone className="h-4 w-4 text-blue-500" />
                      <div>
                        <h4 className="font-medium text-sm">Phone Calls</h4>
                        <p className="text-2xl font-bold text-blue-600">
                          {patient.phoneCalls || 0}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Mail className="h-4 w-4 text-green-500" />
                      <div>
                        <h4 className="font-medium text-sm">Emails</h4>
                        <p className="text-2xl font-bold text-green-600">
                          {patient.emails || 0}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-sm text-gray-500 mb-2">
                        Family History
                      </h4>
                      <p className="text-sm bg-gray-50 p-3 rounded-lg">
                        {patient.familyHistory || "No family history recorded"}
                      </p>
                    </div>
                    <div>
                      <h4 className="font-medium text-sm text-gray-500 mb-2">
                        Medical History
                      </h4>
                      <p className="text-sm bg-gray-50 p-3 rounded-lg">
                        {patient.medicalHistory ||
                          "No medical history recorded"}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Consent Forms */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <FileCheck className="h-5 w-5" />
                  <span>Consent Forms</span>
                </CardTitle>
                <CardDescription>
                  Signed consent forms and legal documents
                </CardDescription>
              </CardHeader>
              <CardContent>
                {patient.consentForms && patient.consentForms.length > 0 ? (
                  <div className="space-y-3">
                    {patient.consentForms.map((form, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg"
                      >
                        <div className="flex items-center space-x-3">
                          <FileCheck className="h-4 w-4 text-green-600" />
                          <span className="text-sm font-medium">{form}</span>
                        </div>
                        <Badge
                          variant="secondary"
                          className="bg-green-100 text-green-800"
                        >
                          Signed
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <FileCheck className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      No Consent Forms
                    </h3>
                    <p className="text-gray-500 mb-4">
                      No consent forms have been signed yet.
                    </p>
                    <Button variant="outline" size="sm">
                      Request Consent Form
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Activity className="h-5 w-5" />
                  <span>Recent Activity</span>
                </CardTitle>
                <CardDescription>
                  Latest interactions and updates
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">
                        Patient profile updated
                      </p>
                      <p className="text-xs text-gray-500">2 days ago</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">
                        Appointment scheduled
                      </p>
                      <p className="text-xs text-gray-500">1 week ago</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">
                        Insurance information updated
                      </p>
                      <p className="text-xs text-gray-500">2 weeks ago</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
