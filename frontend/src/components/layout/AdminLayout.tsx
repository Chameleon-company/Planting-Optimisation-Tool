import { NavLink, Outlet, useNavigate } from "react-router-dom";
import "../../style.css";
import { useAuth } from "../../contexts/AuthContext";

export default function AdminLayout() {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <div className="admin-sidebar-brand">
          <img
            src="/assets/images/logo2.svg"
            alt="Logo"
            className="admin-sidebar-logo"
          />
          <div>
            <h2>Management Panel</h2>
            <p>Admin and Manager workspace</p>
          </div>
        </div>

        <nav className="admin-nav">
          <NavLink
            to="/admin"
            end
            className={({ isActive }) =>
              `admin-nav-link ${isActive ? "active" : ""}`
            }
          >
            Dashboard
          </NavLink>

          <NavLink
            to="/admin/settings"
            className={({ isActive }) =>
              `admin-nav-link ${isActive ? "active" : ""}`
            }
          >
            Settings
          </NavLink>

          <NavLink
            to="/admin/logs"
            className={({ isActive }) =>
              `admin-nav-link ${isActive ? "active" : ""}`
            }
          >
            Audit Logs
          </NavLink>
        </nav>
      </aside>

      <div className="admin-main">
        <header className="admin-header">
          <div className="admin-header-left">
            <h1>Admin Dashboard</h1>
            <span className="admin-breadcrumb">Admin / Dashboard</span>
          </div>

          <div className="admin-header-right">
            <span className="admin-role">
              {user
                ? user.role.charAt(0).toUpperCase() + user.role.slice(1)
                : "User"}
            </span>
            <button
              type="button"
              className="admin-logout-btn"
              onClick={handleLogout}
            >
              Logout
            </button>
          </div>
        </header>

        <main className="admin-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
