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
        <p className="farm-list-empty">Loading profile...</p>
      )}

      {isSearching && !isLoading && profile && (
        <div>
          <FarmCard isSearched={true} farm={profile} />

          <div className="farm-bottom-row">
            {canEdit && (
              <button
                className="farm-action-btn"
                onClick={() => navigate("/farms")}
              >
                Manage
              </button>
            )}
          </div>
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
