import { Helmet } from "react-helmet-async";

function AdminLogs() {
  return (
    <>
      <Helmet>
        <title>Audit Logs | Planting Optimisation Tool</title>
      </Helmet>

      <section className="admin-page-card">
        <h2>Audit Logs</h2>
        <p>
          This placeholder page is part of the management shell and will later
          display system audit activity.
        </p>
      </section>
    </>
  );
}

export default AdminLogs;
