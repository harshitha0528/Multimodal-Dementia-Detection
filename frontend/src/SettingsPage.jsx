import { useState } from "react";

function SettingsPage({ useAuth }) {
  const { user } = useAuth();
  const [doctorName, setDoctorName] = useState(user?.name || "");
  const [specializations, setSpecializations] = useState("Neurology, Cognitive Assessment");
  const [contactNumber, setContactNumber] = useState("+91 ");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");

  const saveProfile = (e) => {
    e.preventDefault();
    setMessage("Doctor profile updated.");
  };

  const changePassword = (e) => {
    e.preventDefault();

    if (!currentPassword || !newPassword || !confirmPassword) {
      setMessage("Please fill all password fields.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setMessage("New password and confirm password do not match.");
      return;
    }

    if (newPassword.length < 6) {
      setMessage("New password must be at least 6 characters.");
      return;
    }

    setCurrentPassword("");
    setNewPassword("");
    setConfirmPassword("");
    setMessage("Password changed successfully.");
  };

  return (
    <div className="settingsPage">
      <h1>Settings</h1>

      {message ? <p className="settingsMessage">{message}</p> : null}

      <div className="settingsGrid">
        <form className="settingsCard" onSubmit={saveProfile}>
          <h3>Doctor Details</h3>

          <label>Doctor Name</label>
          <input value={doctorName} onChange={(e) => setDoctorName(e.target.value)} />

          <label>Specializations</label>
          <input
            value={specializations}
            onChange={(e) => setSpecializations(e.target.value)}
            placeholder="Neurology, Geriatrics"
          />

          <label>Contact Number</label>
          <input
            value={contactNumber}
            onChange={(e) => setContactNumber(e.target.value)}
            placeholder="+91 xxxxxxxxxx"
          />

          <button type="submit">Save Details</button>
        </form>

        <form className="settingsCard" onSubmit={changePassword}>
          <h3>Change Password</h3>

          <label>Current Password</label>
          <input
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
          />

          <label>New Password</label>
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />

          <label>Confirm New Password</label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />

          <button type="submit">Update Password</button>
        </form>
      </div>
    </div>
  );
}

export default SettingsPage;
