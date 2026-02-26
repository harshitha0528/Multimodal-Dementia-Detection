import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const MAX_AUDIO_MB = 15;
const MAX_MRI_MB = 10;

function BrainIcon() {
  return (
    <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M9 5a3 3 0 0 0-3 3v8a3 3 0 0 0 3 3h1V5H9z" />
      <path d="M15 5a3 3 0 0 1 3 3v8a3 3 0 0 1-3 3h-1V5h1z" />
      <path d="M10 7a2.5 2.5 0 0 1 2 2.4A2.5 2.5 0 0 1 14 12a2.5 2.5 0 0 1-2 2.6A2.5 2.5 0 0 1 10 17" />
      <path d="M14 7a2.5 2.5 0 0 0-2 2.4A2.5 2.5 0 0 0 10 12a2.5 2.5 0 0 0 2 2.6A2.5 2.5 0 0 0 14 17" />
    </svg>
  );
}

function UploadArrowIcon() {
  return (
    <svg viewBox="0 0 24 24" width="38" height="38" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 16V6" />
      <path d="M7 11l5-5 5 5" />
      <path d="M5 18v1a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1" />
    </svg>
  );
}

function UploadPage() {
  const [mri, setMri] = useState(null);
  const [audio, setAudio] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { patientName, age, gender, mobileNumber, city } = location.state || {};

  const validateFileSize = (file, maxMb, label) => {
    if (!file) return true;
    const sizeMb = file.size / (1024 * 1024);
    if (sizeMb > maxMb) {
      alert(`${label} file is too large (${sizeMb.toFixed(1)} MB). Max allowed is ${maxMb} MB.`);
      return false;
    }
    return true;
  };

  const handleAudioChange = (e) => {
    const file = e.target.files?.[0] || null;
    if (!file) {
      setAudio(null);
      return;
    }

    if (!validateFileSize(file, MAX_AUDIO_MB, "Audio")) {
      e.target.value = "";
      setAudio(null);
      return;
    }

    setAudio(file);
  };

  const handleMriChange = (e) => {
    const file = e.target.files?.[0] || null;
    if (!file) {
      setMri(null);
      return;
    }

    if (!validateFileSize(file, MAX_MRI_MB, "MRI")) {
      e.target.value = "";
      setMri(null);
      return;
    }

    setMri(file);
  };

  const handleNext = () => {
    if (!audio) {
      alert("Please upload audio first.");
      return;
    }

    if (!mri) {
      alert("Please upload MRI image first.");
      return;
    }

    navigate("/cognitive", {
      state: { mri, audio, patientName, age, gender, mobileNumber, city },
    });
  };

  return (
    <div className="uploadPage">
      <div className="uploadCard">
        <div className="uploadTop">
          <div className="uploadBrand">
            <span className="uploadBrandIcon"><BrainIcon /></span>
            <span>NeuroFusion AI</span>
          </div>
        </div>

        <div className="uploadBody">
          <div className="uploadGrid">
            <div className="uploadSection">
              <h3>MRI Brain Scan</h3>
              <label className={`dropZone ${mri ? "selected" : ""}`}>
                <input type="file" accept=".jpg,.jpeg,.png" onChange={handleMriChange} />
                <span className="dropIcon"><UploadArrowIcon /></span>
                <span className="dropTitle">Drag & Drop</span>
                <span className="dropSub">or Click to Browse</span>
                <span className="dropFormats">JPG, PNG</span>
                <span className="dropFileName">{mri ? mri.name : "No file selected"}</span>
              </label>
            </div>

            <div className="uploadSection">
              <h3>Speech Sample (.flac)</h3>
              <label className={`dropZone primary ${audio ? "selected" : ""}`}>
                <input type="file" accept=".wav,.mp3,.flac" onChange={handleAudioChange} />
                <span className="dropIcon"><UploadArrowIcon /></span>
                <span className="dropTitle">Drag & Drop</span>
                <span className="dropSub">or Click to Browse</span>
                <span className="dropFormats">FLAC, WAV, MP3</span>
                <span className="dropFileName">{audio ? audio.name : "No file selected"}</span>
              </label>
            </div>
          </div>

          <button className="uploadCta" onClick={handleNext}>
            Start Cognitive Test →
          </button>
        </div>
      </div>
    </div>
  );
}

export default UploadPage;
