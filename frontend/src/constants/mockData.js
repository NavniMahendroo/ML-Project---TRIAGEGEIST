export const departmentStats = [
  { name: "Emergency", patients: 46, color: "#f97316" },
  { name: "Cardiology", patients: 28, color: "#ef4444" },
  { name: "Neurology", patients: 22, color: "#06b6d4" },
  { name: "Orthopedics", patients: 18, color: "#22c55e" },
  { name: "Pediatrics", patients: 14, color: "#eab308" },
];

export const adminPatientsByDepartment = {
  Emergency: [
    { id: "PT-104", name: "Riya Das", status: "Admitted", acuity: 2 },
    { id: "PT-132", name: "Samar Khan", status: "Observation", acuity: 3 },
    { id: "PT-145", name: "Mina Roy", status: "Discharged", acuity: 4 },
  ],
  Cardiology: [
    { id: "PT-088", name: "Vikram Iyer", status: "Admitted", acuity: 1 },
    { id: "PT-121", name: "Nazia Ali", status: "Observation", acuity: 2 },
  ],
  Neurology: [
    { id: "PT-098", name: "Aarav Singh", status: "Admitted", acuity: 2 },
    { id: "PT-157", name: "Priya Menon", status: "Discharged", acuity: 4 },
  ],
};

export const doctors = [
  { id: "DR-11", name: "Dr. Meera Nair", department: "Emergency", onDuty: true },
  { id: "DR-18", name: "Dr. Karan Patel", department: "Cardiology", onDuty: true },
  { id: "DR-22", name: "Dr. Hafsa Noor", department: "Neurology", onDuty: false },
  { id: "DR-34", name: "Dr. Rohan Bedi", department: "Orthopedics", onDuty: true },
];

export const staffPatients = [
  { id: "PT-301", name: "Anil Gupta", bed: "B-14", acuity: 2, state: "Admitted" },
  { id: "PT-314", name: "Neha Jain", bed: "B-18", acuity: 3, state: "Observation" },
  { id: "PT-327", name: "Imran Malik", bed: "B-07", acuity: 4, state: "Stabilized" },
];

export const staffTasks = {
  upcoming: [
    { id: "TK-08", title: "Re-check vitals for PT-301", due: "09:30 AM" },
    { id: "TK-11", title: "Medication round in Bay B", due: "10:00 AM" },
    { id: "TK-14", title: "Update shift handover notes", due: "11:15 AM" },
  ],
  completed: [
    { id: "TK-02", title: "Lab sample dispatch", type: "Lab", doneAt: "07:40 AM" },
    { id: "TK-04", title: "Doctor consult prep", type: "Consult", doneAt: "08:15 AM" },
    { id: "TK-05", title: "Medication administration", type: "Medication", doneAt: "08:45 AM" },
    { id: "TK-06", title: "Discharge documentation", type: "Documentation", doneAt: "09:05 AM" },
    { id: "TK-07", title: "Bedside reassessment", type: "Assessment", doneAt: "09:20 AM" },
  ],
};
