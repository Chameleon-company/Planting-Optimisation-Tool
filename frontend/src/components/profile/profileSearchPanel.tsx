import FarmSearchInput from "./profileSearchInput";
import EnvironmentalProfileCard from "./profileSearchedCard";
import ProfileEditActions from "./profileEditButtons";
import { EnvironmentalProfile } from "@/hooks/useSearchProfiles";

interface FarmSearchPanelProps {
  query: string;
  setQuery: (q: string) => void;
  profile: EnvironmentalProfile | null;
  isLoading: boolean;
  error: string | null;
  user: { name: string } | null;
}

export default function FarmSearchPanel({
  query,
  setQuery,
  profile,
  isLoading,
  error,
  user,
}: FarmSearchPanelProps) {
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
          <EnvironmentalProfileCard profile={profile} />

          <div className="farmBottomRow">
            <ProfileEditActions />
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
