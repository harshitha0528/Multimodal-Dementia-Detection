import { useEffect, useMemo, useState } from "react";

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

function HistoryPage({ useAuth }) {
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
          throw new Error("Failed to load history");
        }

        setReports(Array.isArray(data.reports) ? data.reports : []);
      } catch (err) {
        setError(err.message || "Failed to load history");
      } finally {
        setLoading(false);
      }
    };

    loadReports();
  }, []);

  const isAdmin = user?.role === "admin";
  const filterName = isAdmin ? user?.reportPatientName : "";

  const displayReports = useMemo(() => {
    const base = isAdmin
      ? reports.filter((item) => normalize(item.patient_name) === normalize(filterName))
      : reports;
    return [...base].sort((a, b) => Number(b.id || 0) - Number(a.id || 0));
  }, [reports, isAdmin, filterName]);

  if (loading) return <h2 style={{ padding: "30px" }}>Loading history...</h2>;
  if (error) return <h2 style={{ padding: "30px" }}>Error: {error}</h2>;

  return (
    <div className="patientsPage">
      <h1>{isAdmin ? "Assessment History (Filtered)" : "Assessment History"}</h1>

      {isAdmin ? (
        <p style={{ marginTop: 0, color: "#4d638c" }}>
          Showing history only for patient name: <strong>{filterName}</strong>
        </p>
      ) : null}

      {displayReports.length === 0 ? (
        <p>{isAdmin ? "No history found for this patient name." : "No history found yet."}</p>
      ) : (
        <div className="patientsTableWrap">
          <table className="patientsTable">
            <thead>
              <tr>
                <th>Assessment ID</th>
                <th>Name</th>
                <th>Phone Number</th>
                <th>Dementia Stage</th>
                <th>Severity</th>
                <th>Dementia Confidence</th>
                <th>Date</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {displayReports.map((item) => {
                const when = dateTimeParts(item.date);
                return (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.patient_name || "-"}</td>
                    <td>{item.mobile_number || "-"}</td>
                    <td>{stageLabel(item.final_prediction)}</td>
                    <td>{severityLabel(item.final_prediction)}</td>
                    <td>{`${(Number(item.confidence) * 100).toFixed(2)}%`}</td>
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

export default HistoryPage;
