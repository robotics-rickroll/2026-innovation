import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { vi } from "vitest";

import { ArtifactDetailPage } from "../pages/ArtifactDetailPage";
import { AuthProvider } from "../auth/AuthContext";

const mockArtifact = {
  id: "1",
  artifact_id: "ART-000002",
  timestamp: new Date().toISOString(),
  location_approx: "34.05, -118.25",
  location_lat: 34.05,
  location_lng: -118.25,
  measure_length_cm: 10,
  measure_width_cm: 5,
  measure_height_cm: 2,
  additional_info: { material_guess: "stone" },
  images: [{ id: "img1", url: "https://example.com/1.jpg" }],
  latest_classification: { status: "CLASSIFIED" }
};

function mockFetch(data: unknown) {
  vi.stubGlobal("fetch", vi.fn(async () => ({
    ok: true,
    json: async () => data
  })) as any);
}

describe("ArtifactDetailPage", () => {
  it("does not rely on raw lat/lng fields", async () => {
    mockFetch(mockArtifact);
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={["/artifacts/1"]}>
          <Routes>
            <Route path="/artifacts/:id" element={<ArtifactDetailPage />} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );
    await waitFor(() => {
      expect(screen.getByText("ART-000002")).toBeInTheDocument();
    });
    expect(screen.getByText(/Location \(approx\)/)).toBeInTheDocument();
    expect(screen.queryByText(/location_lat/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/location_lng/i)).not.toBeInTheDocument();
  });
});
