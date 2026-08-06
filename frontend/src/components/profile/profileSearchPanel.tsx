import FarmSearchInput from "./profileSearchInput";
import FarmCard from "./profileCard";

import { useAuth } from "@/contexts/AuthContext";
import type { Farm } from "@/hooks/useUserProfiles";

interface FarmSearchPanelProps {
  query: string;
  setQuery: (q: string) => void;
  profile: Farm | null;
  isLoading: boolean;
  error: string | null;
  onEdit?: () => void;
  onRegenerate?: () => void;
  isRegenerating?: boolean;
  actionError?: string | null;
  actionMessage?: string | null;
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
  onEdit,
  onRegenerate,
  isRegenerating = false,
  actionError = null,
  actionMessage = null,
}: FarmSearchPanelProps) {
  const { user } = useAuth();

  const canEdit = user?.role === "supervisor" || user?.role === "admin";

  const canManageProfile = canEdit && Boolean(onEdit) && Boolean(onRegenerate);

  const handleClear = () => setQuery("");

  const isSearching = query.trim().length > 0;

  const isProfileReady = profile ? hasEnvironmentalProfile(profile) : false;

  const actionControls =
    canManageProfile && profile ? (
      <div className="profile-action-row">
        <button
          type="button"
          className="btn-secondary"
          onClick={onEdit}
          disabled={isRegenerating}
        >
          Edit
        </button>

        <button
          type="button"
          className="btn-primary"
          onClick={onRegenerate}
          disabled={isRegenerating}
        >
          {isRegenerating ? "Regenerating..." : "Regenerate"}
        </button>
      </div>
    ) : null;

  return (
    <>
      <FarmSearchInput
        value={query}
        onChange={setQuery}
        onClear={handleClear}
        isLoading={isLoading}
      />

      {error && <p className="farm-list-empty">{error}</p>}

      {actionError && (
        <p className="profile-action-message profile-action-error" role="alert">
          {actionError}
        </p>
      )}

      {actionMessage && !actionError && (
        <p
          className="profile-action-message profile-action-success"
          role="status"
        >
          {actionMessage}
        </p>
      )}

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
          {actionControls}
        </div>
      )}

      {isSearching && !isLoading && profile && !isProfileReady && !error && (
        <>
          <div
            className="profile-status-card profile-status-pending"
            role="status"
            aria-live="polite"
          >
            <h2 className="profile-status-title">
              Environmental profile not ready
            </h2>

            <p className="profile-status-message">
              This farm is registered, but its environmental data is not
              available yet. Processing may still be in progress. Please check
              again later.
            </p>
          </div>

          {actionControls}
        </>
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
