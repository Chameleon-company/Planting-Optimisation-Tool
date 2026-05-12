interface FarmPageNavProps {
  page: number;
  totalPages: number;
  setPage: (page: number) => void;
}

export default function FarmPageNav({
  page,
  totalPages,
  setPage,
}: FarmPageNavProps) {
  return (
    <div>
      <div className="farm-page-nav">
        {/* Create buttons for setting current page to next or before current page */}
        <button
          className="btn-primary"
          disabled={page === 0}
          onClick={() => setPage(page - 1)}
        >
          ← Previous
        </button>
        <span className="farm-page-nav-info">
          Page {page + 1} of {totalPages}
        </span>
        <button
          className="btn-primary"
          disabled={page >= totalPages - 1}
          onClick={() => setPage(page + 1)}
        >
          Next →
        </button>
      </div>
    </div>
  );
}
