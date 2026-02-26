import { useState } from "react";
import { useNavigate } from "react-router-dom";
import logoImage from "./assets/dementia_logo.png";

const USERS = [
  { role: "doctor", email: "doctor@hospital.com", password: "doctor123", name: "Dr. Meera Shah" },
  { role: "admin", email: "admin@hospital.com", password: "admin123", name: "Admin R. Kumar" },
];

function UserIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M20 21a8 8 0 0 0-16 0" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );
}

function LockIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="4" y="11" width="16" height="10" rx="2" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
    </svg>
  );
}

function FileTextIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M14 2H7a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7z" />
      <path d="M14 2v5h5" />
      <path d="M9 13h6M9 17h6" />
    </svg>
  );
}

function LoginPage({ useAuth }) {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [role, setRole] = useState("doctor");
  const [adminPatientName, setAdminPatientName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    const match = USERS.find(
      (user) => user.role === role && user.email === email.trim().toLowerCase() && user.password === password
    );

    if (!match) {
      setError("Invalid credentials for selected role.");
      return;
    }

    if (role === "admin" && !adminPatientName.trim()) {
      setError("Please enter patient name for report filtering.");
      return;
    }

    login({
      role: match.role,
      name: match.name,
      email: match.email,
      reportPatientName: role === "admin" ? adminPatientName.trim() : "",
    });
    navigate("/dashboard");
  };

  return (
    <div className="loginPage">
      <div className="loginShell">
        <div className="loginLeft">
          <h1>LOGIN</h1>
          <p>Secure access for clinical decision support workflow</p>

          <form onSubmit={handleSubmit} className="loginForm">
            <div className="loginField">
              <label>Role</label>
              <select value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="doctor">Doctor</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            <div className="loginField">
              <label>Email</label>
              <div className="inputWithIcon">
                <span className="inputIcon">
                  <UserIcon />
                </span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={role === "doctor" ? "doctor@hospital.com" : "admin@hospital.com"}
                  required
                />
              </div>
            </div>

            <div className="loginField">
              <label>Password</label>
              <div className="inputWithIcon">
                <span className="inputIcon">
                  <LockIcon />
                </span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={role === "doctor" ? "doctor123" : "admin123"}
                  required
                />
              </div>
            </div>

            {role === "admin" ? (
              <div className="loginField">
                <label>Patient Name</label>
                <div className="inputWithIcon">
                  <span className="inputIcon">
                    <FileTextIcon />
                  </span>
                  <input
                    type="text"
                    value={adminPatientName}
                    onChange={(e) => setAdminPatientName(e.target.value)}
                    placeholder="Enter patient name for reports"
                    required
                  />
                </div>
              </div>
            ) : null}

            {error ? <p className="loginError">{error}</p> : null}

            <button type="submit" className="loginBtn">
              Login Now
            </button>
          </form>
        </div>

        <div className="loginRight">
          <div className="loginHeroFrame">
            <img src={logoImage} alt="Medical Visual" className="loginHeroImage" />
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
