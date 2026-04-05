import FarmCard from "./profileCard";
import { useSession } from "@/contexts/SessionContext";
import { useAuth } from "@/contexts/AuthContext";

export default function FarmList() {
  const { user } = useAuth();
  const { farms, isLoading } = useSession();

  if (isLoading) {
    return <p className="farmListEmpty">Loading farms...</p>;
  }

  if (!user) {
    return (
      <p className="farmListEmpty">
        You need to be logged in to see your farms.
      </p>
    );
  } else if (farms.length === 0) {
    return <p className="farmListEmpty">No farms found.</p>;
  }

  return (
    <div className="farmList">
      {farms.map(farm => (
        <FarmCard key={farm.id} farm={farm} />
      ))}
    </div>
  );
}
