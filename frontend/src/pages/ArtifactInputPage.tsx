import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { classifyArtifact, createArtifact } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export function ArtifactInputPage() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [files, setFiles] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    artifact_id: "",
    timestamp: "",
    location_lat: "",
    location_lng: "",
    measure_length_cm: "",
    measure_width_cm: "",
    measure_height_cm: "",
    hollow: "",
    material_guess: "",
    shape: "",
    additional_json: ""
  });

  if (!token) {
    return <p className="error">Login required</p>;
  }

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    let additionalInfo: Record<string, unknown> = {};
    if (form.hollow) additionalInfo.hollow = form.hollow === "true";
    if (form.material_guess) additionalInfo.material_guess = form.material_guess;
    if (form.shape) additionalInfo.shape = form.shape;
    if (form.additional_json) {
      try {
        const parsed = JSON.parse(form.additional_json);
        additionalInfo = { ...additionalInfo, ...parsed };
      } catch (err) {
        setError("Invalid additional JSON");
        setLoading(false);
        return;
      }
    }
    try {
      const payload = {
        artifact_id: form.artifact_id,
        timestamp: form.timestamp || undefined,
        location_lat: form.location_lat ? Number(form.location_lat) : undefined,
        location_lng: form.location_lng ? Number(form.location_lng) : undefined,
        measure_length_cm: Number(form.measure_length_cm),
        measure_width_cm: Number(form.measure_width_cm),
        measure_height_cm: Number(form.measure_height_cm),
        additional_info: additionalInfo,
        image_urls: []
      };
      const created = await createArtifact(payload, token, files);
      await classifyArtifact(created.id, token);
      navigate(`/artifacts/${created.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to submit");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="page">
      <div className="page-header">
        <h1>Submit Artifact</h1>
        <p>Exact coordinates are never displayed publicly. We round location for privacy.</p>
      </div>
      <form className="form" onSubmit={onSubmit}>
        <label>
          Artifact ID
          <input
            value={form.artifact_id}
            onChange={(event) => setForm({ ...form, artifact_id: event.target.value })}
            required
          />
        </label>
        <label>
          Timestamp
          <input
            type="datetime-local"
            value={form.timestamp}
            onChange={(event) => setForm({ ...form, timestamp: event.target.value })}
          />
        </label>
        <div className="form-row">
          <label>
            Latitude
            <input
              value={form.location_lat}
              onChange={(event) => setForm({ ...form, location_lat: event.target.value })}
            />
          </label>
          <label>
            Longitude
            <input
              value={form.location_lng}
              onChange={(event) => setForm({ ...form, location_lng: event.target.value })}
            />
          </label>
        </div>
        <div className="form-row">
          <label>
            Length (cm)
            <input
              type="number"
              value={form.measure_length_cm}
              onChange={(event) => setForm({ ...form, measure_length_cm: event.target.value })}
              required
            />
          </label>
          <label>
            Width (cm)
            <input
              type="number"
              value={form.measure_width_cm}
              onChange={(event) => setForm({ ...form, measure_width_cm: event.target.value })}
              required
            />
          </label>
          <label>
            Height (cm)
            <input
              type="number"
              value={form.measure_height_cm}
              onChange={(event) => setForm({ ...form, measure_height_cm: event.target.value })}
              required
            />
          </label>
        </div>
        <div className="form-row">
          <label>
            Hollow
            <select
              value={form.hollow}
              onChange={(event) => setForm({ ...form, hollow: event.target.value })}
            >
              <option value="">Unknown</option>
              <option value="true">Yes</option>
              <option value="false">No</option>
            </select>
          </label>
          <label>
            Material Guess
            <input
              value={form.material_guess}
              onChange={(event) => setForm({ ...form, material_guess: event.target.value })}
            />
          </label>
          <label>
            Shape
            <input value={form.shape} onChange={(event) => setForm({ ...form, shape: event.target.value })} />
          </label>
        </div>
        <label>
          Additional JSON
          <textarea
            rows={4}
            value={form.additional_json}
            onChange={(event) => setForm({ ...form, additional_json: event.target.value })}
          />
        </label>
        <label>
          Images (min 5 recommended)
          <input
            type="file"
            multiple
            onChange={(event) => setFiles(Array.from(event.target.files || []))}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? "Submitting..." : "Submit"}
        </button>
      </form>
    </section>
  );
}
