import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";

import { ArtifactListPage } from "../pages/ArtifactListPage";

const mockArtifacts = [
  {
    id: "1",
    artifact_id: "ART-000001",
    timestamp: new Date().toISOString(),
    location_approx: "34.05, -118.25",
    latest_classification: { status: "CLASSIFIED" }
  }
];

function mockFetch(data: unknown) {
  vi.stubGlobal("fetch", vi.fn(async () => ({
    ok: true,
    json: async () => data
  })) as any);
}

describe("ArtifactListPage", () => {
  it("renders list from API", async () => {
    mockFetch(mockArtifacts);
    render(
      <MemoryRouter>
        <ArtifactListPage />
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByText("ART-000001")).toBeInTheDocument();
    });
  });
});
