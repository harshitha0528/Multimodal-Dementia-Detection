import { useEffect, useState } from "react";

function normalize(value) {
  return String(value || "").trim().toLowerCase();
}

function stageLabel(rawStage) {
  const value = String(rawStage || "").trim();
  if (!value) return "Unknown";
  return value
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace("Demented", "Dementia")
    .replace("Non Dementia", "No Dementia");
}

function severityLabel(rawStage) {
  const value = normalize(rawStage);
  if (value.includes("nondemented")) return "None";
  if (value.includes("verymild")) return "Low";
  if (value.includes("mild")) return "Moderate";
  if (value.includes("moderate")) return "High";
  return "Unknown";
}

function dateTimeParts(rawDate) {
  const value = String(rawDate || "").trim();
  if (!value) return { date: "-", time: "-" };

  const parsed = new Date(value);
  if (!Number.isNaN(parsed.getTime())) {
    return {
      date: parsed.toLocaleDateString(),
      time: parsed.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
  }

  const parts = value.split(" ");
  if (parts.length >= 2) {
    return { date: parts.slice(0, -1).join(" "), time: parts[parts.length - 1] };
  }
  return { date: value, time: "-" };
}

function timestamp(rawDate, fallbackId) {
  const parsed = new Date(String(rawDate || ""));
  if (!Number.isNaN(parsed.getTime())) return parsed.getTime();
  return Number(fallbackId || 0);
}

function ReportHistory({ useAuth }) {
  const { user } = useAuth();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadReports = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8010/reports");
        const data = await response.json();

        if (!response.ok) {
          throw new Error("Failed to load report history");
        }

        setReports(Array.isArray(data.reports) ? data.reports : []);
      } catch (err) {
        setError(err.message || "Failed to load report history");
      } finally {
        setLoading(false);
      }
    };

    loadReports();
  }, []);

  const isAdmin = user?.role === "admin";
  const filterName = isAdmin ? user?.reportPatientName : "";
  const filteredReports = isAdmin
    ? reports.filter((item) => normalize(item.patient_name) === normalize(filterName))
    : reports;
  const latestByPatient = new Map();
  for (const item of filteredReports) {
    const key = `${normalize(item.patient_name)}|${normalize(item.mobile_number)}`;
    const prev = latestByPatient.get(key);
    if (!prev) {
      latestByPatient.set(key, item);
      continue;
    }
    const prevTs = timestamp(prev.date, prev.id);
    const currentTs = timestamp(item.date, item.id);
    if (currentTs > prevTs) {
      latestByPatient.set(key, item);
    }
  }
  const displayReports = Array.from(latestByPatient.values()).sort(
    (a, b) => timestamp(b.date, b.id) - timestamp(a.date, a.id)
  );

  if (loading) return <h2 style={{ padding: "30px" }}>Loading report history...</h2>;
  if (error) return <h2 style={{ padding: "30px" }}>Error: {error}</h2>;

  return (
    <div className="patientsPage">
      <h1>{isAdmin ? "Patients (Latest Records, Filtered)" : "Patients (Latest Records)"}</h1>

      {isAdmin ? (
        <p style={{ marginTop: 0, color: "#4d638c" }}>
          Showing patients only for name: <strong>{filterName}</strong>
        </p>
      ) : null}

      {displayReports.length === 0 ? (
        <p>{isAdmin ? "No reports found for this patient name." : "No reports found yet."}</p>
      ) : (
        <div className="patientsTableWrap">
          <table className="patientsTable">
            <thead>
              <tr>
                <th>Name</th>
                <th>Phone Number</th>
                <th>Age</th>
                <th>Gender</th>
                <th>Current Stage</th>
                <th>Current Severity</th>
                <th>Last Assessment Date</th>
                <th>Last Assessment Time</th>
              </tr>
            </thead>
            <tbody>
              {displayReports.map((item) => {
                const when = dateTimeParts(item.date);
                return (
                  <tr key={item.id}>
                    <td>{item.patient_name || "-"}</td>
                    <td>{item.mobile_number || "-"}</td>
                    <td>{item.age ?? "-"}</td>
                    <td>{item.gender || "-"}</td>
                    <td>{stageLabel(item.final_prediction)}</td>
                    <td>{severityLabel(item.final_prediction)}</td>
                    <td>{when.date}</td>
                    <td>{when.time}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default ReportHistory;
