export default function RecommendationSkeleton() {
  return (
    <div
      className="rec-skeleton-wrapper"
      role="status"
      aria-busy="true"
      aria-live="polite"
    >
      {Array.from({ length: 3 }).map((_, cardIndex) => (
        <div className="rec-results-card rec-skeleton-card" key={cardIndex}>
          <div className="rec-skeleton-line rec-skeleton-title" />

          {Array.from({ length: 4 }).map((_, rowIndex) => (
            <div className="rec-skeleton-row" key={rowIndex}>
              <div className="rec-skeleton-line rec-skeleton-rank" />
              <div className="rec-skeleton-line rec-skeleton-name" />
              <div className="rec-skeleton-line rec-skeleton-score" />
              <div className="rec-skeleton-line rec-skeleton-action" />
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
