import { useNavigate } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";

const STAGE_META = [
  { key: "NonDemented", label: "No Dementia", color: "#2f7de1" },
  { key: "VeryMildDemented", label: "Very Mild", color: "#43b581" },
  { key: "MildDemented", label: "Mild", color: "#f5b700" },
  { key: "ModerateDemented", label: "Dementia", color: "#e44747" },
];

function normalizeStage(raw) {
  const value = String(raw || "").trim();
  if (!value) return "ModerateDemented";
  if (value === "NonDemented") return "NonDemented";
  if (value === "VeryMildDemented") return "VeryMildDemented";
  if (value === "MildDemented") return "MildDemented";
  return "ModerateDemented";
}

function severityScore(stage) {
  const normalized = normalizeStage(stage);
  if (normalized === "NonDemented") return 0;
  if (normalized === "VeryMildDemented") return 1;
  if (normalized === "MildDemented") return 2;
  return 3;
}

function toDate(value) {
  const parsed = new Date(String(value || ""));
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function linePoints(series, chartWidth, chartHeight, yMax) {
  return series.map((v, i) => {
    const x = (i / Math.max(1, series.length - 1)) * chartWidth;
    const y = chartHeight - (v / yMax) * chartHeight;
    return `${x},${y}`;
  }).join(" ");
}

function donutGradient(entries) {
  const total = entries.reduce((sum, item) => sum + item.value, 0);
  if (!total) return "conic-gradient(#dfe6f5 0 100%)";

  let current = 0;
  const parts = entries.map((item) => {
    const next = current + (item.value / total) * 100;
    const stop = `${item.color} ${current.toFixed(2)}% ${next.toFixed(2)}%`;
    current = next;
    return stop;
  });
  return `conic-gradient(${parts.join(", ")})`;
}

function DashboardPage({ useAuth }) {
  const navigate = useNavigate();
  const { user } = useAuth();

  const isDoctor = user?.role === "doctor";
  const dashboardTitle = isDoctor ? "Doctor Dashboard" : "Admin Dashboard";
  const [metrics, setMetrics] = useState({
    total_patients: 0,
    today_screenings: 0,
    high_risk_alerts: 0,
  });
  const [reports, setReports] = useState([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [metricsRes, reportsRes] = await Promise.all([
          fetch("http://127.0.0.1:8010/dashboard-metrics"),
          fetch("http://127.0.0.1:8010/reports"),
        ]);

        const metricsData = await metricsRes.json();
        const reportsData = await reportsRes.json();

        if (!metricsRes.ok) return;
        setMetrics({
          total_patients: Number(metricsData.total_patients || 0),
          today_screenings: Number(metricsData.today_screenings || 0),
          high_risk_alerts: Number(metricsData.high_risk_alerts || 0),
        });

        if (reportsRes.ok && Array.isArray(reportsData.reports)) {
          setReports(reportsData.reports);
        }
      } catch {
        // Keep fallback zeros if metrics API is unavailable.
      }
    };

    loadData();
  }, []);

  const latestPatients = useMemo(() => {
    const map = new Map();
    for (const item of reports) {
      const key = `${String(item.patient_name || "").toLowerCase()}|${String(item.mobile_number || "").toLowerCase()}`;
      if (!map.has(key)) map.set(key, item);
    }
    return Array.from(map.values());
  }, [reports]);

  const stageDonutEntries = useMemo(() => {
    const counts = STAGE_META.map((stage) => ({ ...stage, value: 0 }));
    for (const item of latestPatients) {
      const stage = normalizeStage(item.final_prediction);
      const target = counts.find((c) => c.key === stage);
      if (target) target.value += 1;
    }
    return counts;
  }, [latestPatients]);

  const genderDonutEntries = useMemo(() => {
    const out = [
      { key: "male", label: "Male", color: "#2f69d8", value: 0 },
      { key: "female", label: "Female", color: "#34b57a", value: 0 },
    ];
    for (const item of latestPatients) {
      const g = String(item.gender || "").toLowerCase();
      if (g === "male") out[0].value += 1;
      if (g === "female") out[1].value += 1;
    }
    return out;
  }, [latestPatients]);

  const adminTrend = useMemo(() => {
    if (isDoctor) return { records: [], points: "", labels: [] };

    const filterName = String(user?.reportPatientName || "").trim().toLowerCase();
    const base = reports.filter((item) => {
      if (!filterName) return true;
      return String(item.patient_name || "").trim().toLowerCase() === filterName;
    });

    const sorted = [...base].sort((a, b) => {
      const at = toDate(a.date)?.getTime() ?? Number(a.id || 0);
      const bt = toDate(b.date)?.getTime() ?? Number(b.id || 0);
      return at - bt;
    });

    const severities = sorted.map((item) => severityScore(item.final_prediction));
    const labels = sorted.map((item, index) => {
      const d = toDate(item.date);
      if (!d) return `Checkup ${index + 1}`;
      return d.toLocaleDateString([], { month: "short", day: "numeric" });
    });

    return {
      records: sorted,
      points: linePoints(severities, 620, 220, 3),
      labels,
      severities,
    };
  }, [isDoctor, reports, user?.reportPatientName]);

  if (!isDoctor) {
    return (
      <>
        <section className="dashHeader">
          <h1>{dashboardTitle}</h1>
          <p>Signed in as {user?.role}</p>
        </section>

        <section className="dashPanels">
          <div className="dashPanel wide">
            <h3>Admin Details</h3>
            <p><strong>Name:</strong> {user?.name || "Admin"}</p>
            <p><strong>Role:</strong> {user?.role || "admin"}</p>
            <p><strong>Email:</strong> {user?.email || "-"}</p>
            <p><strong>Patient Filter Name:</strong> {user?.reportPatientName || "-"}</p>
          </div>
          <div className="dashPanel wide">
            <h3>Dementia Progress Trend</h3>
            <p className="adminTrendNote">
              Stage scale: 0 = No Dementia, 1 = Very Mild, 2 = Mild, 3 = Dementia.
            </p>
            {adminTrend.records.length < 2 ? (
              <p>Add at least 2 checkups to visualize progression trend.</p>
            ) : (
              <>
                <div className="trendChartWrap">
                  <svg viewBox="0 0 620 220" className="trendSvg" preserveAspectRatio="none">
                    <line x1="0" y1="220" x2="620" y2="220" className="trendAxis" />
                    <polyline
                      points={adminTrend.points}
                      fill="none"
                      stroke="#2f69d8"
                      strokeWidth="3"
                    />
                  </svg>
                </div>
                <div className="trendLabels">
                  {adminTrend.labels.map((label, idx) => (
                    <span key={`${label}-${idx}`}>{label}</span>
                  ))}
                </div>
              </>
            )}
          </div>
          <div className="dashPanel">
            <h3>Patients</h3>
            <p>Open filtered patient records.</p>
            <button type="button" onClick={() => navigate("/reports")}>Open Records</button>
          </div>
          <div className="dashPanel">
            <h3>History</h3>
            <p>Open filtered assessment history.</p>
            <button type="button" onClick={() => navigate("/history")}>View History</button>
          </div>
          <div className="dashPanel wide">
            <h3>Account Settings</h3>
            <p>Manage profile and password.</p>
            <button type="button" onClick={() => navigate("/settings")}>Open Settings</button>
          </div>
        </section>
      </>
    );
  }

  return (
    <>
      <section className="dashHeader">
        <h1>{dashboardTitle}</h1>
        <p>Signed in as {user?.role}</p>
      </section>

      <section className="dashStats">
        <article className="dashCard">
          <h3>Total Patients</h3>
          <strong>{metrics.total_patients}</strong>
        </article>
        <article className="dashCard">
          <h3>Today Screenings</h3>
          <strong>{metrics.today_screenings}</strong>
        </article>
        <article className="dashCard">
          <h3>High Risk Alerts</h3>
          <strong>{metrics.high_risk_alerts}</strong>
        </article>
      </section>

      <section className="dashPanels">
        <div className="dashPanel wide overviewCharts">
          <div className="dashPanel chartSmall">
            <h3>Dementia Stages</h3>
            <div
              className="donutRing"
              style={{ background: donutGradient(stageDonutEntries) }}
            />
            <div className="chartLegend vertical">
              {stageDonutEntries.map((item) => (
                <span key={item.key}><i style={{ background: item.color }} />{item.label}: {item.value}</span>
              ))}
            </div>
          </div>

          <div className="dashPanel chartSmall">
            <h3>Gender Distribution</h3>
            <div
              className="donutRing"
              style={{ background: donutGradient(genderDonutEntries) }}
            />
            <div className="chartLegend vertical">
              {genderDonutEntries.map((item) => (
                <span key={item.key}><i style={{ background: item.color }} />{item.label}: {item.value}</span>
              ))}
            </div>
          </div>
        </div>
        <div className="dashPanel">
          <h3>Patients</h3>
          <p>Open patient records and report status.</p>
          <button type="button" onClick={() => navigate("/reports")}>Open Records</button>
        </div>
        <div className="dashPanel">
          <h3>History</h3>
          <p>Assessment history and previous outcomes.</p>
          <button type="button" onClick={() => navigate("/history")}>View History</button>
        </div>
        <div className="dashPanel wide">
          <h3>Settings</h3>
          <p>Role controls and system preferences section.</p>
        </div>
      </section>
    </>
  );
}

export default DashboardPage;
