import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { getArtifact, overrideClassification, updateArtifact } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export function EditArtifactPage() {
  const { id } = useParams();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    measure_length_cm: "",
    measure_width_cm: "",
    measure_height_cm: "",
    timestamp: "",
    additional_info: "",
    status: "",
    summary: "",
    artifact_type: "",
    civilization: "",
    age_range: "",
    confidence: ""
  });

  useEffect(() => {
    if (!id) return;
    getArtifact(id)
      .then((data) => {
        setForm({
          measure_length_cm: String(data.measure_length_cm),
          measure_width_cm: String(data.measure_width_cm),
          measure_height_cm: String(data.measure_height_cm),
          timestamp: data.timestamp.slice(0, 16),
          additional_info: JSON.stringify(data.additional_info || {}, null, 2),
          status: data.latest_classification?.status || "",
          summary: data.latest_classification?.summary || "",
          artifact_type: data.latest_classification?.artifact_type || "",
          civilization: data.latest_classification?.civilization || "",
          age_range: data.latest_classification?.age_range || "",
          confidence: data.latest_classification?.confidence?.toString() || ""
        });
      })
      .catch((err) => setError(err.message || "Failed to load"));
  }, [id]);

  if (!token) {
    return <p className="error">Login required</p>;
  }

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      let additionalInfo = {};
      if (form.additional_info) {
        additionalInfo = JSON.parse(form.additional_info);
      }
      await updateArtifact(
        id,
        {
          timestamp: form.timestamp ? new Date(form.timestamp).toISOString() : undefined,
          measure_length_cm: Number(form.measure_length_cm),
          measure_width_cm: Number(form.measure_width_cm),
          measure_height_cm: Number(form.measure_height_cm),
          additional_info: additionalInfo
        },
        token
      );
      await overrideClassification(
        id,
        {
          status: form.status || undefined,
          summary: form.summary || undefined,
          artifact_type: form.artifact_type || undefined,
          civilization: form.civilization || undefined,
          age_range: form.age_range || undefined,
          confidence: form.confidence ? Number(form.confidence) : undefined
        },
        token
      );
      navigate(`/artifacts/${id}`);
    } catch (err: any) {
      setError(err.message || "Failed to save");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="page">
      <div className="page-header">
        <h1>Edit Artifact</h1>
      </div>
      <form className="form" onSubmit={onSubmit}>
        <div className="form-row">
          <label>
            Length (cm)
            <input
              type="number"
              value={form.measure_length_cm}
              onChange={(event) => setForm({ ...form, measure_length_cm: event.target.value })}
            />
          </label>
          <label>
            Width (cm)
            <input
              type="number"
              value={form.measure_width_cm}
              onChange={(event) => setForm({ ...form, measure_width_cm: event.target.value })}
            />
          </label>
          <label>
            Height (cm)
            <input
              type="number"
              value={form.measure_height_cm}
              onChange={(event) => setForm({ ...form, measure_height_cm: event.target.value })}
            />
          </label>
        </div>
        <label>
          Timestamp
          <input
            type="datetime-local"
            value={form.timestamp}
            onChange={(event) => setForm({ ...form, timestamp: event.target.value })}
          />
        </label>
        <label>
          Additional Info JSON
          <textarea
            rows={4}
            value={form.additional_info}
            onChange={(event) => setForm({ ...form, additional_info: event.target.value })}
          />
        </label>
        <h2>Override Classification</h2>
        <label>
          Status
          <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })}>
            <option value="">Unchanged</option>
            <option value="CLASSIFIED">CLASSIFIED</option>
            <option value="NOT_CLASSIFIABLE">NOT_CLASSIFIABLE</option>
            <option value="PENDING">PENDING</option>
            <option value="ERROR">ERROR</option>
          </select>
        </label>
        <label>
          Summary
          <textarea value={form.summary} onChange={(event) => setForm({ ...form, summary: event.target.value })} />
        </label>
        <label>
          Type
          <input value={form.artifact_type} onChange={(event) => setForm({ ...form, artifact_type: event.target.value })} />
        </label>
        <label>
          Civilization
          <input value={form.civilization} onChange={(event) => setForm({ ...form, civilization: event.target.value })} />
        </label>
        <label>
          Age Range
          <input value={form.age_range} onChange={(event) => setForm({ ...form, age_range: event.target.value })} />
        </label>
        <label>
          Confidence
          <input
            type="number"
            step="0.01"
            value={form.confidence}
            onChange={(event) => setForm({ ...form, confidence: event.target.value })}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? "Saving..." : "Save"}
        </button>
      </form>
    </section>
  );
}
