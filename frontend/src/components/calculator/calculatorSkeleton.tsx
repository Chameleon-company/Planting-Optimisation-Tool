export default function CalculatorSkeleton() {
  return (
    <div
      className="calc-skeleton-wrapper"
      role="status"
      aria-busy="true"
      aria-live="polite"
    >
      <div className="calc-skeleton-tabs">
        {Array.from({ length: 3 }).map((_, index) => (
          <div className="calc-skeleton-line calc-skeleton-tab" key={index} />
        ))}
      </div>

      <div className="calc-skeleton-panel">
        <div className="calc-skeleton-result">
          <div className="calc-skeleton-line calc-skeleton-title" />

          {Array.from({ length: 4 }).map((_, index) => (
            <div
              className="calc-skeleton-line calc-skeleton-stat"
              key={index}
            />
          ))}
        </div>

        <div className="calc-skeleton-map">
          <div className="calc-skeleton-line calc-skeleton-map-fill" />
        </div>
      </div>
    </div>
  );
}
