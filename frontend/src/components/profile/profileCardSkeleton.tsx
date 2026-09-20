export default function ProfileCardSkeleton() {
  return (
    <div
      className="farm-card farm-card-skeleton"
      role="status"
      aria-label="Loading farm"
    >
      <div className="skeleton-line skeleton-title" />

      <div className="farm-card-grid">
        {Array.from({ length: 6 }).map((_, index) => (
          <div className="farm-card-stat" key={index}>
            <div className="skeleton-line skeleton-label" />
            <div className="skeleton-line skeleton-value" />
          </div>
        ))}
      </div>

      <div className="skeleton-line skeleton-coords" />
    </div>
  );
}
