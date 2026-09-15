export default function SpeciesCardSkeleton() {
  return (
    <article
      className="article-card species-card-skeleton"
      role="status"
      aria-label="Loading species"
    >
      <div className="article-media species-skeleton-media" />

      <div className="article-body">
        <div className="species-skeleton-line species-skeleton-title" />

        <div className="article-actions">
          <div className="species-skeleton-line species-skeleton-button" />
        </div>
      </div>
    </article>
  );
}
