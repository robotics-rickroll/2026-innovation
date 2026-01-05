import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ArtifactListItem, getArtifacts } from "../api/client";

export function ArtifactListPage() {
  const [items, setItems] = useState<ArtifactListItem[]>([]);
  const [query, setQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [civilizationFilter, setCivilizationFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    getArtifacts({
      q: query,
      type: typeFilter,
      civilization: civilizationFilter,
      status: statusFilter
    })
      .then((data) => {
        if (active) {
          setItems(data);
          setError(null);
        }
      })
      .catch((err) => {
        if (active) {
          setError(err.message || "Failed to load");
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, [query, typeFilter, civilizationFilter, statusFilter]);

  return (
    <section className="page">
      <div className="page-header">
        <h1>Artifact Catalog</h1>
        <p>Browse AI-assisted classifications from field collections.</p>
      </div>
      <div className="filters">
        <input
          placeholder="Search artifact id..."
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <input
          placeholder="Type"
          value={typeFilter}
          onChange={(event) => setTypeFilter(event.target.value)}
        />
        <input
          placeholder="Civilization"
          value={civilizationFilter}
          onChange={(event) => setCivilizationFilter(event.target.value)}
        />
        <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
          <option value="">Status</option>
          <option value="CLASSIFIED">CLASSIFIED</option>
          <option value="NOT_CLASSIFIABLE">NOT_CLASSIFIABLE</option>
          <option value="PENDING">PENDING</option>
          <option value="ERROR">ERROR</option>
        </select>
      </div>
      {loading && <p>Loading artifacts...</p>}
      {error && <p className="error">{error}</p>}
      <div className="card-grid">
        {items.map((item) => (
          <Link className="card" key={item.id} to={`/artifacts/${item.id}`}>
            <div className="card-title">{item.artifact_id}</div>
            <div className="card-meta">
              <span>{new Date(item.timestamp).toLocaleString()}</span>
              <span>{item.location_approx || "Location hidden"}</span>
            </div>
            <div className="card-chip">
              {item.latest_classification?.status ?? "UNCLASSIFIED"}
            </div>
            {item.latest_classification?.artifact_type && (
              <div className="card-detail">{item.latest_classification.artifact_type}</div>
            )}
          </Link>
        ))}
      </div>
    </section>
  );
}
