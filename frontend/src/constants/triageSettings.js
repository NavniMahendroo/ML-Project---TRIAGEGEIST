// Severity configuration
const severityConfig = {
  1: {
    label: "Resuscitation",
    sublabel: "Immediate life-saving intervention required",
    chip: "bg-rose-600 text-rose-50",
    card: "border-rose-400/50 bg-rose-950/60 text-rose-100",
    meter: "from-rose-500 to-red-700",
    glow: "shadow-rose-500/30",
    icon: "🔴",
  },
  2: {
    label: "Emergent",
    sublabel: "Time-critical condition — attend within 10 min",
    chip: "bg-orange-600 text-orange-50",
    card: "border-orange-400/50 bg-orange-950/60 text-orange-100",
    meter: "from-orange-400 to-orange-600",
    glow: "shadow-orange-500/30",
    icon: "🟠",
  },
  3: {
    label: "Urgent",
    sublabel: "Significant condition — attend within 30 min",
    chip: "bg-yellow-600 text-yellow-50",
    card: "border-yellow-400/50 bg-yellow-950/60 text-yellow-100",
    meter: "from-yellow-400 to-yellow-600",
    glow: "shadow-yellow-500/25",
    icon: "🟡",
  },
  4: {
    label: "Less Urgent",
    sublabel: "Non-critical — attend within 60 min",
    chip: "bg-lime-600 text-lime-50",
    card: "border-lime-400/50 bg-lime-950/60 text-lime-100",
    meter: "from-lime-400 to-lime-600",
    glow: "shadow-lime-500/20",
    icon: "🟢",
  },
  5: {
    label: "Non-Urgent",
    sublabel: "Minor concern — standard queue",
    chip: "bg-emerald-600 text-emerald-50",
    card: "border-emerald-400/50 bg-emerald-950/60 text-emerald-100",
    meter: "from-emerald-400 to-emerald-700",
    glow: "shadow-emerald-500/20",
    icon: "🟢",
  },
};

// Form defaults — 13 clinical features
const intakeDefaults = {
  age: "",
  sex: "",
  arrival_mode: "",
  chief_complaint_raw: "",
  heart_rate: "",
  respiratory_rate: "",
  spo2: "",
  systolic_bp: "",
  diastolic_bp: "",
  temperature_c: "",
  pain_score: "",
  gcs_total: "",
  news2_score: "",
};

export { severityConfig, intakeDefaults };
