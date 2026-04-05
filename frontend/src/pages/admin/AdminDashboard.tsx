import { Helmet } from "react-helmet-async";

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
      </section>
    </>
  );
}

export default AdminDashboard;
