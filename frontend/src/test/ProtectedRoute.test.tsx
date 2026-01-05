import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import { App } from "../App";
import { AuthProvider } from "../auth/AuthContext";

describe("ProtectedRoute", () => {
  it("redirects to login when unauthenticated", async () => {
    localStorage.removeItem("jwt");
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={["/submit"]}>
          <App />
        </MemoryRouter>
      </AuthProvider>
    );
    expect(await screen.findByText("Archaeologist Login")).toBeInTheDocument();
  });
});
