import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { createContext, useContext, useMemo, useState } from "react";
import PatientRegister from "./PatientRegister";
import UploadPage from "./UploadPage";
import CognitivePage from "./CognitivePage";
import ResultPage from "./ResultPage";
import ReportHistory from "./ReportHistory";
import HistoryPage from "./HistoryPage";
import SettingsPage from "./SettingsPage";
import LoginPage from "./LoginPage";
import DashboardPage from "./DashboardPage";
import ClinicalLayout from "./ClinicalLayout";

const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  const authValue = useMemo(
    () => ({
      user,
      login: (profile) => setUser(profile),
      logout: () => setUser(null),
    }),
    [user]
  );

  return <AuthContext.Provider value={authValue}>{children}</AuthContext.Provider>;
}

function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}

function ProtectedRoute({ children, role }) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (role && user.role !== role) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<LoginPage useAuth={useAuth} />} />
          <Route
            element={
              <ProtectedRoute>
                <ClinicalLayout useAuth={useAuth} />
              </ProtectedRoute>
            }
          >
            <Route
              path="/dashboard"
              element={<DashboardPage useAuth={useAuth} />}
            />
            <Route
              path="/reports"
              element={<ReportHistory useAuth={useAuth} />}
            />
            <Route
              path="/history"
              element={<HistoryPage useAuth={useAuth} />}
            />
            <Route
              path="/settings"
              element={<SettingsPage useAuth={useAuth} />}
            />
            <Route
              path="/patients/new"
              element={
                <ProtectedRoute role="doctor">
                  <PatientRegister />
                </ProtectedRoute>
              }
            />
            <Route
              path="/upload"
              element={
                <ProtectedRoute role="doctor">
                  <UploadPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/cognitive"
              element={
                <ProtectedRoute role="doctor">
                  <CognitivePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/result"
              element={
                <ProtectedRoute role="doctor">
                  <ResultPage />
                </ProtectedRoute>
              }
            />
          </Route>
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
