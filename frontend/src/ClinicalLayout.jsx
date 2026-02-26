import { Outlet, useLocation, useNavigate } from "react-router-dom";
import logoImage from "./assets/dementia_logo.png";

function ClinicalLayout({ useAuth }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const isDoctor = user?.role === "doctor";

  const isOverview = location.pathname === "/dashboard";
  const isPatients = location.pathname === "/reports";
  const isHistory = location.pathname === "/history";
  const isSettings = location.pathname === "/settings";
  const isNewAssessment = location.pathname.startsWith("/patients/new")
    || location.pathname.startsWith("/upload")
    || location.pathname.startsWith("/cognitive")
    || location.pathname.startsWith("/result");

  return (
    <div className="dashboardPage">
      <div className="dashboardShell">
        <aside className="dashboardSidebar">
          <div className="dashboardBrand">
            <img src={logoImage} alt="NeuroFusion AI Logo" className="sidebarBrandLogo" />
            <div className="dashboardBrandText">NeuroFusion AI</div>
          </div>
          <nav className="dashboardNav">
            <button type="button" className={`dashNavItem ${isOverview ? "active" : ""}`} onClick={() => navigate("/dashboard")}>Overview</button>
            <button type="button" className={`dashNavItem ${isPatients ? "active" : ""}`} onClick={() => navigate("/reports")}>Patients</button>
            <button
              type="button"
              className={`dashNavItem ${isNewAssessment ? "active" : ""}`}
              onClick={() => navigate("/patients/new")}
              disabled={!isDoctor}
            >
              New Assessment
            </button>
            <button type="button" className={`dashNavItem ${isHistory ? "active" : ""}`} onClick={() => navigate("/history")}>History</button>
            <button type="button" className={`dashNavItem ${isSettings ? "active" : ""}`} onClick={() => navigate("/settings")}>Settings</button>
          </nav>
          <button
            type="button"
            className="dashLogout"
            onClick={() => {
              logout();
              navigate("/login");
            }}
          >
            Logout
          </button>
        </aside>

        <main className="dashboardMain">
          <header className="dashTopBar">
            <div className="dashSearch">Search patient reports...</div>
            <div className="dashUser">{isDoctor ? "Doctor" : "Admin"}</div>
          </header>
          <section className="dashRouteContent">
            <Outlet />
          </section>
        </main>
      </div>
    </div>
  );
}

export default ClinicalLayout;
