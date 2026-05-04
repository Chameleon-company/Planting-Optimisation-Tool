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

      {error && <p className="farmListEmpty">{error}</p>}

      {isSearching && isLoading && (
        <p className="farmListEmpty">Loading profile...</p>
      )}

      {isSearching && !isLoading && profile && (
        <div>
          <FarmCard isSearched={true} farm={profile} />

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
      )}

      {isSearching && !isLoading && !profile && !error && (
        <>
          {!user && (
            <p className="farmListEmpty">You must be logged in to search.</p>
          )}
          {user && <p className="farmListEmpty">No profile found.</p>}
        </>
      )}
    </>
  );
}
