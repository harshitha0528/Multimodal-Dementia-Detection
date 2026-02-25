import { useLocation, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

function ResultPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const { mri, audio, cognitiveScore } = location.state || {};

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!location.state) {
      setError("No data received.");
      setLoading(false);
      return;
    }

    const runPrediction = async () => {
      try {
        const payload = new FormData();
        payload.append("mri_file", mri);
        payload.append("cognitive_score", String(cognitiveScore));

        if (audio) {
          payload.append("audio_file", audio);
        }

        const response = await fetch("http://127.0.0.1:8000/predict", {
          method: "POST",
          body: payload,
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data?.detail || "Prediction failed");
        }

        setResult(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    runPrediction();
  }, []);

  if (loading) return <h2>Running Analysis...</h2>;
  if (error) return <h2>Error: {error}</h2>;

  return (
    <div style={{ padding: "30px" }}>
      <h1>Result</h1>
      <h2>{result.predicted_class}</h2>
      <p>Confidence: {(result.confidence * 100).toFixed(2)}%</p>
      <button onClick={() => navigate("/")}>Start Again</button>
    </div>
  );
}

export default ResultPage;