import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ArtifactDetail, getArtifact } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export function ArtifactDetailPage() {
  const { id } = useParams();
  const { token } = useAuth();
  const [artifact, setArtifact] = useState<ArtifactDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    getArtifact(id)
      .then((data) => {
        setArtifact(data);
        setError(null);
      })
      .catch((err) => setError(err.message || "Failed to load"));
  }, [id]);

  if (error) {
    return <p className="error">{error}</p>;
  }
  if (!artifact) {
    return <p>Loading artifact...</p>;
  }

  return (
    <section className="page">
      <div className="page-header">
        <h1>{artifact.artifact_id}</h1>
        <p>Location (approx): {artifact.location_approx || "Hidden"}</p>
        {token && (
          <Link className="button" to={`/artifacts/${artifact.id}/edit`}>
            Edit Artifact
          </Link>
        )}
      </div>
      <div className="detail-grid">
        <div className="detail-card">
          <h2>Images</h2>
          <div className="image-grid">
            {artifact.images.map((img) => (
              <img key={img.id} src={img.url} alt={artifact.artifact_id} />
            ))}
          </div>
        </div>
        <div className="detail-card">
          <h2>Measurements</h2>
          <p>Length: {artifact.measure_length_cm} cm</p>
          <p>Width: {artifact.measure_width_cm} cm</p>
          <p>Height: {artifact.measure_height_cm} cm</p>
          <h3>Additional Info</h3>
          <pre className="pre">{JSON.stringify(artifact.additional_info, null, 2)}</pre>
        </div>
        <div className="detail-card">
          <h2>AI Classification</h2>
          <p>Status: {artifact.latest_classification?.status ?? "UNCLASSIFIED"}</p>
          <p>{artifact.latest_classification?.summary}</p>
          <p>Type: {artifact.latest_classification?.artifact_type ?? "-"}</p>
          <p>Civilization: {artifact.latest_classification?.civilization ?? "-"}</p>
          <p>Age Range: {artifact.latest_classification?.age_range ?? "-"}</p>
          <p>Confidence: {artifact.latest_classification?.confidence ?? "-"}</p>
        </div>
      </div>
    </section>
  );
}
