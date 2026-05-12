import { useState, useEffect } from "react";
import { Helmet } from "react-helmet-async";
import "./profile.css";
import ProfileHeader from "@/components/profile/profileHeader";
import FarmList from "@/components/profile/profileFarms";
import FarmSearchPanel from "@/components/profile/profileSearchPanel";

import { useUserProfiles } from "../hooks/useUserProfiles";
import { useSearchProfiles } from "../hooks/useSearchProfiles";
import { useAuth } from "@/contexts/AuthContext";
import { useSearchParams } from "react-router-dom";

function ProfilePage() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get("farmId") ?? "");
  const [debouncedQuery, setDebouncedQuery] = useState(
    searchParams.get("farmId") ?? ""
  );

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, 800);

    return () => clearTimeout(timer);
  }, [query]);

  const { farms, isLoading, page, setPage, totalFarms, totalPages } =
    useUserProfiles();

  const {
    profile,
    isLoading: isProfileLoading,
    error,
  } = useSearchProfiles(debouncedQuery);

  const isSearching = query.trim().length > 0;

  return (
    <div className="profile-page">
      <Helmet>
        <title>Environmental Profile | Planting Optimisation Tool</title>
      </Helmet>

      <ProfileHeader userName={user?.name} farmCount={totalFarms} />

      <FarmSearchPanel
        query={query}
        setQuery={setQuery}
        profile={profile}
        isLoading={isProfileLoading}
        error={error}
      />

      {!isSearching && (
        <FarmList
          farms={farms}
          isLoading={isLoading}
          page={page}
          totalPages={totalPages}
          setPage={setPage}
        />
      )}
    </div>
  );
}

export default ProfilePage;
