import { Farm } from "@/contexts/SessionContext";

interface FarmCardProps {
  farm: Farm;
}

export default function FarmCard({ farm }: FarmCardProps) {
  const tags = [
    farm.coastal && "Coastal",
    farm.riparian && "Riparian",
    farm.nitrogen_fixing && "Nitrogen Fixing",
    farm.shade_tolerant && "Shade Tolerant",
    farm.bank_stabilising && "Bank Stabilising",
  ].filter(Boolean) as string[];

  return (
    <div className="farmCard">
      <div className="farmCardHeader">
        <span className="farmCardId">Farm #{farm.id}</span>
        <span className="farmCardArea">{farm.area_ha.toFixed(3)} ha</span>
      </div>

      <div className="farmCardGrid">
        <div className="farmCardStat">
          <span className="farmCardStatLabel">Rainfall</span>
          <span className="farmCardStatValue">{farm.rainfall_mm} mm</span>
        </div>
        <div className="farmCardStat">
          <span className="farmCardStatLabel">Temperature</span>
          <span className="farmCardStatValue">
            {farm.temperature_celsius}°C
          </span>
        </div>
        <div className="farmCardStat">
          <span className="farmCardStatLabel">Elevation</span>
          <span className="farmCardStatValue">{farm.elevation_m} m</span>
        </div>
        <div className="farmCardStat">
          <span className="farmCardStatLabel">Soil pH</span>
          <span className="farmCardStatValue">{farm.ph.toFixed(1)}</span>
        </div>
        <div className="farmCardStat">
          <span className="farmCardStatLabel">Slope</span>
          <span className="farmCardStatValue">{farm.slope.toFixed(2)}°</span>
        </div>
        <div className="farmCardStat">
          <span className="farmCardStatLabel">Soil Type</span>
          <span className="farmCardStatValue">{farm.soil_texture.name}</span>
        </div>
      </div>

      <div className="farmCardCoords">
        📍 {farm.latitude.toFixed(5)}, {farm.longitude.toFixed(5)}
      </div>

      {farm.agroforestry_type.length > 0 && (
        <div className="farmCardTags">
          {farm.agroforestry_type.map(type => (
            <span key={type.name} className="farmTag farmTagAgroforestry">
              {type.name}
            </span>
          ))}
        </div>
      )}

      {tags.length > 0 && (
        <div className="farmCardTags">
          {tags.map(tag => (
            <span key={tag} className="farmTag farmTagTrait">
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
