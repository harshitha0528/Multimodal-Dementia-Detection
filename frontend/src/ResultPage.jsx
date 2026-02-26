import { useLocation, useNavigate } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";

const STAGE_META = {
  NonDemented: {
    label: "No Dementia Detected",
    hasDementia: false,
    severity: "None",
    precautions: [
      "Maintain regular physical activity (at least 30 minutes most days).",
      "Follow a balanced diet rich in fruits, vegetables, and healthy fats.",
      "Keep brain active with reading, puzzles, or social interaction.",
      "Do yearly cognitive health checkups, especially after age 60.",
    ],
  },
  VeryMildDemented: {
    label: "Very Mild Dementia",
    hasDementia: true,
    severity: "Low",
    precautions: [
      "Establish a daily routine and use reminders for medications/tasks.",
      "Schedule periodic cognitive screening with a neurologist.",
      "Ensure 7-8 hours of sleep and reduce stress triggers.",
      "Involve family in early planning for support and follow-ups.",
    ],
  },
  MildDemented: {
    label: "Mild Dementia",
    hasDementia: true,
    severity: "Moderate",
    precautions: [
      "Consult a specialist for formal assessment and treatment planning.",
      "Supervise medication management and daily finances.",
      "Use home safety measures (labels, alarms, fall prevention).",
      "Encourage regular memory exercises and social engagement.",
    ],
  },
  ModerateDemented: {
    label: "Moderate Dementia",
    hasDementia: true,
    severity: "High",
    precautions: [
      "Seek continuous medical follow-up and caregiver support plan.",
      "Avoid patient being alone in risky situations (cooking, travel).",
      "Improve home safety with close supervision and emergency contacts.",
      "Discuss long-term care, legal, and financial planning with family.",
    ],
  },
};

function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const { mri, audio, cognitiveScore, patientName, age, gender, mobileNumber, city } = location.state || {};

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!location.state) {
      setError("No data received.");
      setLoading(false);
      return;
    }

    if (!mri || !audio) {
      setError("MRI and audio files are required.");
      setLoading(false);
      return;
    }

    const runPrediction = async () => {
      try {
        const payload = new FormData();
        payload.append("mri_file", mri);
        payload.append("audio_file", audio);
        payload.append("patient_name", patientName);
        payload.append("age", String(age));
        payload.append("gender", gender);
        payload.append("mobile_number", mobileNumber);
        payload.append("city", city);
        payload.append("cognitive_score", String(cognitiveScore));

        const response = await fetch("http://127.0.0.1:8010/predict", {
          method: "POST",
          body: payload,
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(typeof data.detail === "string" ? data.detail : "Prediction failed");
        }

        setResult(data);
      } catch (err) {
        setError(err.message || "Prediction failed");
      } finally {
        setLoading(false);
      }
    };

    runPrediction();
  }, []);

  const reportMeta = useMemo(() => {
    if (!result?.predicted_class) return null;
    return STAGE_META[result.predicted_class] || {
      label: result.predicted_class,
      hasDementia: true,
      severity: "Unknown",
      precautions: ["Consult a specialist for detailed interpretation."],
    };
  }, [result]);

  const handleDownloadReport = () => {
    if (!result || !reportMeta) return;

    const lines = [
      "Multimodal Dementia Detection Report",
      "===================================",
      `Generated At: ${new Date().toLocaleString()}`,
      "",
      "Patient Details",
      "---------------",
      `Name: ${patientName}`,
      `Age: ${age}`,
      `Gender: ${gender}`,
      `Mobile Number: ${mobileNumber}`,
      `City: ${city}`,
      "",
      "Assessment Summary",
      "------------------",
      `Dementia Detected: ${reportMeta.hasDementia ? "Yes" : "No"}`,
      `Predicted Stage: ${reportMeta.label}`,
      `Severity: ${reportMeta.severity}`,
      `Confidence: ${(result.confidence * 100).toFixed(2)}%`,
      `Cognitive Score: ${(Number(cognitiveScore) * 100).toFixed(0)}%`,
      "",
      "Precautions",
      "-----------",
      ...reportMeta.precautions.map((p, i) => `${i + 1}. ${p}`),
      "",
      "Disclaimer: This is a screening result and not a final clinical diagnosis.",
    ];

    const blob = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const safeName = (patientName || "patient").replace(/\s+/g, "_");
    link.href = url;
    link.download = `${safeName}_dementia_report.txt`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  };

  if (loading) return <h2>Running Analysis...</h2>;
  if (error) return <h2>Error: {error}</h2>;
  if (!result || !reportMeta) return <h2>Error: Unable to generate report.</h2>;

  return (
    <div className="assessmentPage assessmentResult">
      <h1>Dementia Assessment Report</h1>

      <div style={{ background: "#f7faff", border: "1px solid #d7e4f8", borderRadius: "12px", padding: "16px", marginBottom: "18px" }}>
        <h3 style={{ marginTop: 0 }}>Patient Details</h3>
        <p><strong>Name:</strong> {patientName}</p>
        <p><strong>Age:</strong> {age}</p>
        <p><strong>Gender:</strong> {gender}</p>
        <p><strong>Mobile Number:</strong> {mobileNumber}</p>
        <p><strong>City:</strong> {city}</p>
      </div>

      <div style={{ background: "#fff", border: "1px solid #d7e4f8", borderRadius: "12px", padding: "16px", marginBottom: "18px" }}>
        <h3 style={{ marginTop: 0 }}>Assessment Summary</h3>
        <p><strong>Dementia Detected:</strong> {reportMeta.hasDementia ? "Yes" : "No"}</p>
        <p><strong>Predicted Stage:</strong> {reportMeta.label}</p>
        <p><strong>Severity:</strong> {reportMeta.severity}</p>
        <p><strong>Model Confidence:</strong> {(result.confidence * 100).toFixed(2)}%</p>
        <p><strong>Cognitive Test Score:</strong> {(Number(cognitiveScore) * 100).toFixed(0)}%</p>
      </div>

      <div style={{ background: "#fff", border: "1px solid #d7e4f8", borderRadius: "12px", padding: "16px", marginBottom: "18px" }}>
        <h3 style={{ marginTop: 0 }}>Recommended Precautions</h3>
        <ol>
          {reportMeta.precautions.map((item) => (
            <li key={item} style={{ marginBottom: "8px" }}>{item}</li>
          ))}
        </ol>
      </div>

      <p style={{ fontSize: "0.92rem", color: "#425d88" }}>
        Disclaimer: This result is for screening support only and should be confirmed by a qualified medical professional.
      </p>

      <div style={{ display: "flex", gap: "10px", marginTop: "16px", flexWrap: "wrap" }}>
        <button onClick={handleDownloadReport}>Download Report</button>
        <button onClick={() => window.print()}>Print Report</button>
        <button onClick={() => navigate("/patients/new")}>Start Again</button>
      </div>
    </div>
  );
}

export default ResultPage;
