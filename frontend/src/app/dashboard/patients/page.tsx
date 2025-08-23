import { PatientList } from "@/components/patientlist";

const patients = [
  {
    firstName: "Jaith",
    lastName: "Darrah",
    dateOfBirth: "03/04/2005",
    gender: "male",
    phoneNumber: "123-456-7890",
  },
];

const PatientsPage = () => {
  return <PatientList props={[]} />;
};

export default PatientsPage;
