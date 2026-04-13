import FarmCard from "./profileCard";
import { Farm } from "@/hooks/useProfiles";

interface FarmListProps {
  farms: Farm[];
  isLoading: boolean;
  user: { name: string } | null;
  page: number;
  totalPages: number;
  setPage: (updater: (p: number) => number) => void;
}

export default function FarmList({
  farms,
  isLoading,
  user,
  page,
  totalPages,
  setPage,
}: FarmListProps) {
  if (isLoading) {
    return <p className="farmListEmpty">Loading farms...</p>;
  }

  if (!user) {
    return (
      <p className="farmListEmpty">
        You need to be logged in to see your farms.
      </p>
    );
  }

  if (farms.length === 0) {
    return <p className="farmListEmpty">No farms found.</p>;
  }

  return (
    <div>
      <div className="farmList">
        {farms.map(farm => (
          <FarmCard key={farm.id} farm={farm} />
        ))}
      </div>

      <div className="farmPageNav">
        <button
          className="farmPageNavBtn"
          disabled={page === 0}
          onClick={() => setPage(p => p - 1)}
        >
          ← Previous
        </button>
        <span className="farmPageNavInfo">
          Page {page + 1} of {totalPages}
        </span>
        <button
          className="farmPageNavBtn"
          disabled={page >= totalPages - 1}
          onClick={() => setPage(p => p + 1)}
        >
          Next →
        </button>
      </div>
    </div>
  );
}
