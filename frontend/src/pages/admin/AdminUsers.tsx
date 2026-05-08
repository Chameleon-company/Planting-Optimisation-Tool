import { Helmet } from "react-helmet-async";

function AdminUsers() {
  return (
    <>
      <Helmet>
        <title>User Management | Planting Optimisation Tool</title>
      </Helmet>

      <section className="admin-page-card">
        <h2>User Management</h2>
        <p>
          This placeholder page is part of the management shell and will later
          display user-related information and controls.
        </p>
      </section>
    </>
  );
}

export default AdminUsers;
