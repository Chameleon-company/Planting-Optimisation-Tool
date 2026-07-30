import FarmSearchInput from "./profileSearchInput";
import FarmCard from "./profileCard";
import { Farm } from "@/hooks/useUserProfiles";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

interface FarmSearchPanelProps {
  query: string;
  setQuery: (q: string) => void;
  profile: Farm | null;
  isLoading: boolean;
  error: string | null;
}

function hasEnvironmentalProfile(profile: Farm): boolean {
  return (
    profile.rainfall_mm != null &&
    profile.temperature_celsius != null &&
    profile.elevation_m != null &&
    profile.ph != null &&
    profile.slope != null &&
    Boolean(profile.soil_texture?.name?.trim())
  );
}

export default function FarmSearchPanel({
  query,
  setQuery,
  profile,
  isLoading,
  error,
}: FarmSearchPanelProps) {
  const navigate = useNavigate();
  const { user } = useAuth();
  const canEdit = user?.role === "supervisor" || user?.role === "admin";

  const handleClear = () => setQuery("");

  const isSearching = query.trim().length > 0;

  const isProfileReady = profile ? hasEnvironmentalProfile(profile) : false;

  return (
    <>
      <FarmSearchInput
        value={query}
        onChange={setQuery}
        onClear={handleClear}
        isLoading={isLoading}
      />

      {error && <p className="farm-list-empty">{error}</p>}

      {isSearching && isLoading && (
        <div className="profile-status-card" role="status" aria-live="polite">
          <h2 className="profile-status-title">Loading profile...</h2>
          <p className="profile-status-message">
            Retrieving environmental data for this farm.
          </p>
        </div>
      )}

      {isSearching && !isLoading && profile && isProfileReady && (
        <div className="farm-search-result">
          <FarmCard isSearched={true} farm={profile} />

          <div className="farm-bottom-row">
            {canEdit && (
              <button
                className="btn-primary"
                onClick={() => navigate("/farms")}
              >
                Manage
              </button>
            )}
          </div>
        </div>
      )}

      {isSearching && !isLoading && profile && !isProfileReady && !error && (
        <div
          className="profile-status-card profile-status-pending"
          role="status"
          aria-live="polite"
        >
          <h2 className="profile-status-title">
            Environmental profile not ready
          </h2>

          <p className="profile-status-message">
            This farm is registered, but its environmental data is not available
            yet. Processing may still be in progress. Please check again later.
          </p>
        </div>
      )}

      {isSearching && !isLoading && !profile && !error && (
        <>
          {!user && (
            <p className="farm-list-empty">You must be logged in to search.</p>
          )}
          {user && <p className="farm-list-empty">No profile found.</p>}
        </>
      )}
    </>
  );
}
