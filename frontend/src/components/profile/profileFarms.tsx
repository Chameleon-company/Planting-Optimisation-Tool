import FarmCard from "./profileCard";
import FarmPageNav from "./profilePageNav";

import { useAuth } from "@/contexts/AuthContext";
import { Farm } from "@/hooks/useUserProfiles";
import { useNavigate } from "react-router-dom";

interface FarmListProps {
  farms: Farm[];
  isLoading: boolean;
  page: number;
  totalPages: number;
  setPage: (page: number) => void;
}

export default function FarmList({
  farms,
  isLoading,
  page,
  totalPages,
  setPage,
}: FarmListProps) {
  const navigate = useNavigate();
  const { user } = useAuth();
  const canEdit = user?.role === "supervisor" || user?.role === "admin";

  if (isLoading) {
    return <p className="farmListEmpty">Loading farms...</p>;
  }

  // Not logged in
  if (!user) {
    return (
      <p className="farmListEmpty">
        You need to be logged in to see your farms.
      </p>
    );
  }

  // Logged in but no farms still displays editing actions dependent on role
  if (farms.length === 0) {
    return (
      <>
        <p className="farmListEmpty">No farms found.</p>
        <div className="farmBottomRow">
          <div className="farmBottomRow">
            {canEdit && (
              <button
                className="farmActionBtn"
                onClick={() => navigate("/farms")}
              >
                Manage
              </button>
            )}
          </div>
        </div>
      </>
    );
  }

  // Logged in with farms displays all data
  return (
    <div>
      <div className="farmList">
        {farms.map(farm => (
          <FarmCard isSearched={false} key={farm.id} farm={farm} />
        ))}
      </div>

      <div className="farmBottomRow">
        <FarmPageNav page={page} totalPages={totalPages} setPage={setPage} />

        {canEdit && (
          <button className="farmActionBtn" onClick={() => navigate("/farms")}>
            (put Emoji here) Manage
          </button>
        )}
      </div>
    </div>
  );
}
