import { useState } from "react";
import { useNavigate } from "react-router-dom";

function UploadPage() {
  const [mri, setMri] = useState(null);
  const [audio, setAudio] = useState(null);
  const navigate = useNavigate();

  const handleNext = () => {
    if (!mri) {
      alert("Please upload MRI image first.");
      return;
    }

    navigate("/cognitive", {
      state: { mri, audio },
    });
  };

  return (
    <div style={{ padding: "30px" }}>
      <h1>Multimodal Dementia Detection</h1>

      <div>
        <h3>🎙️ Upload Audio</h3>
        <input
          type="file"
          accept=".wav,.mp3"
          onChange={(e) => setAudio(e.target.files?.[0] || null)}
        />
      </div>

      <div style={{ marginTop: "20px" }}>
        <h3>🧠 Upload MRI Image</h3>
        <input
          type="file"
          accept=".jpg,.jpeg,.png"
          onChange={(e) => setMri(e.target.files?.[0] || null)}
        />
      </div>

      <button
        style={{ marginTop: "30px" }}
        onClick={handleNext}
      >
        Start Cognitive Test →
      </button>
    </div>
  );
}

export default UploadPage;