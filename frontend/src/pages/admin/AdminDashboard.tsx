import { Helmet } from "react-helmet-async";
import { NavLink } from "react-router-dom";

function AdminDashboard() {
  return (
    <>
      <Helmet>
        <title>Admin Dashboard | Planting Optimisation Tool</title>
      </Helmet>
      <section className="admin-page-card">
        <h2>Dashboard Overview</h2>
        <p>
          This is the core dashboard shell for admin and manager management
          pages.
        </p>
        <NavLink
          to="/admin/species"
          className={({ isActive }) =>
            `admin-nav-link ${isActive ? "active" : ""}`
          }
        >
          Species Management
        </NavLink>
      </section>
    </>
  );
}

export default AdminDashboard;
