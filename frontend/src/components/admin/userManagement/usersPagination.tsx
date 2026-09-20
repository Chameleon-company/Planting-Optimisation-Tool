import "./users.css";

interface Props {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function UsersPagination({
  page,
  totalPages,
  onPageChange,
}: Props) {
  if (totalPages <= 1) return null;

  return (
    <div className="users-pagination">
      <button
        type="button"
        className="users-btn-page"
        disabled={page === 0}
        onClick={() => onPageChange(page - 1)}
      >
        ← Prev
      </button>
      <span className="users-page-indicator">
        Page {page + 1} of {totalPages}
      </span>
      <button
        type="button"
        className="users-btn-page"
        disabled={page >= totalPages - 1}
        onClick={() => onPageChange(page + 1)}
      >
        Next →
      </button>
    </div>
  );
}
