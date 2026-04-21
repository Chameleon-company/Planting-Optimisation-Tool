import { EnvironmentalProfile } from "@/hooks/useSearchProfiles";

interface Props {
  profile: EnvironmentalProfile;
}

export default function EnvironmentalProfileCard({ profile }: Props) {
  const toNumber = (value: unknown) =>
    value !== null && value !== undefined ? Number(value) : null;

  return (
    <div className="profileCard">
      <div className="farmCardHeader">
        <span className="farmCardId">Farm #{profile.id}</span>
        {profile.area_ha != null && (
          <span className="farmCardArea">
            {Number(profile.area_ha).toFixed(3)} ha
          </span>
        )}
      </div>

      <div className="farmCardGrid">
        <div className="farmCardStat">
          <span className="farmCardStatLabel">Elevation</span>
          <span className="farmCardStatValue">
            {profile.elevation_m ?? "N/A"} m
          </span>
        </div>

        <div className="farmCardStat">
          <span className="farmCardStatLabel">Soil pH</span>
          <span className="farmCardStatValue">
            {profile.ph != null ? toNumber(profile.ph)?.toFixed(1) : "N/A"}
          </span>
        </div>

        <div className="farmCardStat">
          <span className="farmCardStatLabel">Slope</span>
          <span className="farmCardStatValue">
            {profile.slope != null
              ? toNumber(profile.slope)?.toFixed(2)
              : "N/A"}
            °
          </span>
        </div>
      </div>

      <div className="farmCardCoords">
        📍{" "}
        {profile.latitude != null
          ? toNumber(profile.latitude)?.toFixed(5)
          : "N/A"}
        ,{" "}
        {profile.longitude != null
          ? toNumber(profile.longitude)?.toFixed(5)
          : "N/A"}
      </div>

      {profile.coastal && (
        <div className="farmCardTags">
          <span className="farmTag farmTagTrait">Coastal</span>
        </div>
      )}
    </div>
  );
}
