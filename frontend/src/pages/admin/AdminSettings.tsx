import { Helmet } from "react-helmet-async";

function AdminSettings() {
  return (
    <>
      <Helmet>
        <title>Admin Settings | Planting Optimisation Tool</title>
      </Helmet>

      <section className="admin-page-card">
        <h2>Settings</h2>
        <p>
          This placeholder page is part of the management shell and will later
          support configuration controls.
        </p>
      </section>
    </>
  );
}

export default AdminSettings;
