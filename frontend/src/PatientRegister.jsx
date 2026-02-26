import { useState } from "react";
import { useNavigate } from "react-router-dom";

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

function PatientRegister() {
  const navigate = useNavigate();

  const [patientName, setPatientName] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [mobileNumber, setMobileNumber] = useState("+91");
  const [city, setCity] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!patientName || !age || !gender || !mobileNumber || !city) {
      alert("Please fill all fields");
      return;
    }

    navigate("/upload", {
      state: {
        patientName,
        age,
        gender,
        mobileNumber,
        city,
      },
    });
  };

  return (
    <div className="registerPage">
      <div className="registerCard">
        <div className="registerTop">
          <div className="registerBrand">
            <span className="registerBrandIcon"><BrainIcon /></span>
            <span>NeuroFusion AI</span>
          </div>
          <h1>Patient Registration</h1>
        </div>

        <form onSubmit={handleSubmit} className="registerForm">
          <div className="registerField">
            <label>Full Name *</label>
            <input
              type="text"
              value={patientName}
              onChange={(e) => setPatientName(e.target.value)}
              placeholder="Enter patient's full name"
            />
          </div>

          <div className="registerField">
            <label>Age *</label>
            <input
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              placeholder="Enter age"
            />
          </div>

          <div className="registerField">
            <label>Gender *</label>
            <div className="genderRow">
              {["Male", "Female", "Other"].map((option) => (
                <button
                  key={option}
                  type="button"
                  className={`genderBtn ${gender === option ? "active" : ""}`}
                  onClick={() => setGender(option)}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>

          <div className="registerField">
            <label>Phone Number *</label>
            <input
              type="text"
              value={mobileNumber}
              onChange={(e) => setMobileNumber(e.target.value)}
              placeholder="+91"
            />
          </div>

          <div className="registerField">
            <label>City *</label>
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="Enter city"
            />
          </div>

          <button type="submit" className="registerSubmit">
            Continue →
          </button>
        </form>
      </div>
    </div>
  );
}

export default PatientRegister;
