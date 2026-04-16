import { Helmet } from "react-helmet-async";
import FarmProfileHeader from "@/components/profile/profileHeader";
import FarmList from "@/components/profile/profileFarms";
import { useProfiles } from "../hooks/useProfiles";
import { useAuth } from "@/contexts/AuthContext";

function ProfilePage() {
  // Call relevant data from contexts/hooks for page
  const { user } = useAuth();
  const { farms, isLoading, page, setPage, totalPages, totalFarms } =
    useProfiles();

  return (
    <div>
      {/* Title of web page */}
      <Helmet>
        <title>Environmental Profile | Planting Optimisation Tool</title>
      </Helmet>

      {/* Display header */}
      <FarmProfileHeader farmerName={user?.name ?? ""} farmCount={totalFarms} />

      {/* Display map of farms as cards, as well as page nav and editing buttons */}
      <FarmList
        farms={farms}
        isLoading={isLoading}
        user={user}
        page={page}
        totalPages={totalPages}
        setPage={setPage}
      />
    </div>
  );
}

export default ProfilePage;
