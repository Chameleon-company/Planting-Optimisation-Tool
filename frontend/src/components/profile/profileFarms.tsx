import FarmCard from "./profileAllCards";
import FarmPageNav from "./profilePageNav";
import ProfileEditActions from "./profileEditButtons";
import { Farm } from "@/hooks/useUserProfiles";

interface FarmListProps {
  farms: Farm[];
  isLoading: boolean;
  user: { name: string } | null;
  page: number;
  totalPages: number;
  setPage: (page: number) => void;
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
          <ProfileEditActions />
        </div>
      </>
    );
  }

  // Logged in with farms displays all data
  return (
    <div>
      <div className="farmList">
        {farms.map(farm => (
          <FarmCard key={farm.id} farm={farm} />
        ))}
      </div>

      <div className="farmBottomRow">
        <FarmPageNav page={page} totalPages={totalPages} setPage={setPage} />
        <ProfileEditActions />
      </div>
    </div>
  );
}
