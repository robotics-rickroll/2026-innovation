import { Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { ArtifactDetailPage } from "./pages/ArtifactDetailPage";
import { ArtifactInputPage } from "./pages/ArtifactInputPage";
import { ArtifactListPage } from "./pages/ArtifactListPage";
import { EditArtifactPage } from "./pages/EditArtifactPage";
import { LoginPage } from "./pages/LoginPage";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<ArtifactListPage />} />
        <Route path="artifacts/:id" element={<ArtifactDetailPage />} />
        <Route
          path="submit"
          element={
            <ProtectedRoute>
              <ArtifactInputPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="artifacts/:id/edit"
          element={
            <ProtectedRoute>
              <EditArtifactPage />
            </ProtectedRoute>
          }
        />
        <Route path="login" element={<LoginPage />} />
      </Route>
    </Routes>
  );
}
