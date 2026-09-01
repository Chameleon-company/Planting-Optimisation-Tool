import { useEffect, useState } from "react";
import { Helmet } from "react-helmet-async";
import { useSearchParams } from "react-router-dom";

import ProfileHeader from "@/components/profile/profileHeader";
import FarmList from "@/components/profile/profileFarms";
import FarmSearchPanel from "@/components/profile/profileSearchPanel";
import EditFarmModal from "@/components/farmManagement/farmsEditModal";
import FarmBoundaryMap from "@/components/map/FarmBoundaryMap";

import { useAuth } from "@/contexts/AuthContext";
import { Farm, useUserProfiles } from "@/hooks/useUserProfiles";
import { useSearchProfiles } from "@/hooks/useSearchProfiles";
import { FarmUpdatePayload, useFarms } from "@/hooks/useFarms";
import { useProfileActions } from "@/hooks/useProfileActions";
import { useFarmBoundary } from "@/hooks/useFarmBoundary";

import "./profile.css";
import "./farmManagement.css";

function ProfilePage() {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();

  const [query, setQuery] = useState(searchParams.get("farmId") ?? "");
  const [debouncedQuery, setDebouncedQuery] = useState(
    searchParams.get("farmId") ?? ""
  );
  const [editingFarm, setEditingFarm] = useState<Farm | null>(null);
  const [editMessage, setEditMessage] = useState<string | null>(null);

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
    refetch,
    replaceProfile,
  } = useSearchProfiles(debouncedQuery);

  const { updateFarm } = useFarms();

  const {
    regenerateProfile,
    isRegenerating,
    actionError,
    actionMessage,
    clearActionFeedback,
  } = useProfileActions();

  const {
    boundary,
    isLoading: mapLoading,
    error: mapError,
  } = useFarmBoundary(profile?.id ?? null);

  useEffect(() => {
    clearActionFeedback();
    setEditMessage(null);
  }, [query, clearActionFeedback]);

  const handleEdit = () => {
    if (!profile) return;

    clearActionFeedback();
    setEditMessage(null);
    setEditingFarm(profile);
  };

  const handleEditSuccess = async (
    farmId: number,
    payload: FarmUpdatePayload
  ) => {
    const updated = await updateFarm(farmId, payload);

    if (!updated) {
      throw new Error("Failed to update farm.");
    }

    setEditingFarm(null);
    await refetch();
    setEditMessage("Environmental profile updated successfully.");
  };

  const handleRegenerate = async () => {
    if (!profile) return;

    setEditMessage(null);

    try {
      const regenerated = await regenerateProfile(profile.id);

      replaceProfile({
        ...profile,
        id: regenerated.id ?? profile.id,
        rainfall_mm: regenerated.rainfall_mm ?? profile.rainfall_mm,
        temperature_celsius:
          regenerated.temperature_celsius ?? profile.temperature_celsius,
        elevation_m: regenerated.elevation_m ?? profile.elevation_m,
        ph: regenerated.ph ?? profile.ph,
        slope: regenerated.slope ?? profile.slope,
        area_ha: regenerated.area_ha ?? profile.area_ha,
        latitude: regenerated.latitude ?? profile.latitude,
        longitude: regenerated.longitude ?? profile.longitude,
        coastal: regenerated.coastal ?? profile.coastal,
        riparian: regenerated.riparian ?? profile.riparian,
        nitrogen_fixing: regenerated.nitrogen_fixing ?? profile.nitrogen_fixing,
        shade_tolerant: regenerated.shade_tolerant ?? profile.shade_tolerant,
        bank_stabilising:
          regenerated.bank_stabilising ?? profile.bank_stabilising,
        soil_texture: regenerated.soil_texture?.trim()
          ? { name: regenerated.soil_texture }
          : profile.soil_texture,
      });
    } catch {
      // useProfileActions exposes the error through actionError.
    }
  };

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
        onEdit={handleEdit}
        onRegenerate={handleRegenerate}
        isRegenerating={isRegenerating}
        actionError={actionError}
        actionMessage={actionMessage ?? editMessage}
      />

      {profile && (
        <div className="farm-map-wrapper">
          <FarmBoundaryMap
            boundary={boundary}
            isLoading={mapLoading}
            error={mapError}
          />
        </div>
      )}

      {!isSearching && (
        <FarmList
          farms={farms}
          isLoading={isLoading}
          page={page}
          totalPages={totalPages}
          setPage={setPage}
        />
      )}

      {editingFarm && (
        <EditFarmModal
          farm={editingFarm}
          onClose={() => setEditingFarm(null)}
          onSuccess={handleEditSuccess}
        />
      )}
    </div>
  );
}

export default ProfilePage;
