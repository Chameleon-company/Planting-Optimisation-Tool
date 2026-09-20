export default function CompatibilityMatrixSkeleton() {
  return (
    <div
      className="admin-table-wrapper"
      role="status"
      aria-busy="true"
      aria-live="polite"
    >
      <table className="admin-parameters-table compatibility-matrix-table">
        <thead>
          <tr>
            <th>
              <div className="admin-skeleton-line matrix-skeleton-heading" />
            </th>

            {Array.from({ length: 5 }).map((_, index) => (
              <th key={index}>
                <div className="admin-skeleton-line matrix-skeleton-heading" />
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {Array.from({ length: 6 }).map((_, rowIndex) => (
            <tr key={rowIndex}>
              <td>
                <div className="admin-skeleton-line matrix-skeleton-species" />
                <div className="admin-skeleton-line matrix-skeleton-common-name" />
              </td>

              {Array.from({ length: 5 }).map((_, cellIndex) => (
                <td key={cellIndex} className="compatibility-matrix-cell">
                  <div className="admin-skeleton-line matrix-skeleton-checkbox" />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
