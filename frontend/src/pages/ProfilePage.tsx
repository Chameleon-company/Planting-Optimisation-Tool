import { useState } from "react";
import { Helmet } from "react-helmet-async";
import ProfileHeader from "@/components/profile/profileHeader";
import FarmList from "@/components/profile/profileFarms";
import FarmSearchPanel from "@/components/profile/profileSearchPanel";

import { useUserProfiles } from "../hooks/useUserProfiles";
import { useSearchProfiles } from "../hooks/useSearchProfiles";
import { useAuth } from "@/contexts/AuthContext";

function ProfilePage() {
  const { user } = useAuth();
  const [query, setQuery] = useState("");

  const { farms, isLoading, page, setPage, totalFarms, totalPages } =
    useUserProfiles();

  const {
    profile,
    isLoading: isProfileLoading,
    error,
  } = useSearchProfiles(query);

  const isSearching = query.trim().length > 0;

  return (
    <div>
      <Helmet>
        <title>Environmental Profile | Planting Optimisation Tool</title>
      </Helmet>

      <ProfileHeader farmerName={user?.name} farmCount={totalFarms} />

      <FarmSearchPanel
        query={query}
        setQuery={setQuery}
        profile={profile}
        isLoading={isProfileLoading}
        error={error}
        user={user}
      />

      {!isSearching && (
        <FarmList
          farms={farms}
          isLoading={isLoading}
          user={user}
          page={page}
          totalPages={totalPages}
          setPage={setPage}
        />
      )}
    </div>
  );
}

export default ProfilePage;
