import { Link, NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export function Layout() {
  const { token, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="app-header">
        <Link className="logo" to="/">
          Artifact Atlas
        </Link>
        <nav>
          <NavLink to="/" end>
            Artifacts
          </NavLink>
          {token && (
            <NavLink to="/submit" end>
              Submit Artifact
            </NavLink>
          )}
          {token ? (
            <button type="button" className="link-button" onClick={logout}>
              Logout
            </button>
          ) : (
            <NavLink to="/login">Login</NavLink>
          )}
        </nav>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
