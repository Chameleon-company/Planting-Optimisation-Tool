import { Farm } from "@/hooks/useUserProfiles";

interface FarmCardProps {
  farm: Farm;
  isSearched: boolean;
}

// Create farm card that parses data from backend to be displayed in the frontend
export default function FarmCard({ farm, isSearched }: FarmCardProps) {
  // Convert boolean tags to strings to be displayed
  const tags = [
    farm.coastal && "Coastal",
    farm.riparian && "Riparian",
    farm.nitrogen_fixing && "Nitrogen Fixing",
    farm.shade_tolerant && "Shade Tolerant",
    farm.bank_stabilising && "Bank Stabilising",
  ].filter(Boolean) as string[];

  return (
    <div className={`farm-card ${isSearched ? "searched-card" : ""}`}>
      <div className="farm-card-header">
        <span className="farm-card-id">Farm #{farm.id}</span>
        <span className="farm-card-area">
          {Number(farm.area_ha).toFixed(3)} ha
        </span>
      </div>

      <div className="farm-card-grid">
        <div className="farm-card-stat">
          <span className="farm-card-stat-label">Rainfall</span>
          <span className="farm-card-stat-value">{farm.rainfall_mm} mm</span>
        </div>
        <div className="farm-card-stat">
          <span className="farm-card-stat-label">Temperature</span>
          <span className="farm-card-stat-value">
            {farm.temperature_celsius}°C
          </span>
        </div>
        <div className="farm-card-stat">
          <span className="farm-card-stat-label">Elevation</span>
          <span className="farm-card-stat-value">{farm.elevation_m} m</span>
        </div>
        <div className="farm-card-stat">
          <span className="farm-card-stat-label">Soil pH</span>
          <span className="farm-card-stat-value">
            {farm.ph ? Number(farm.ph).toFixed(1) : "N/A"}
          </span>
        </div>
        <div className="farm-card-stat">
          <span className="farm-card-stat-label">Slope</span>
          <span className="farm-card-stat-value">
            {farm.slope ? Number(farm.slope).toFixed(2) : "N/A"}°
          </span>
        </div>
        <div className="farm-card-stat">
          <span className="farm-card-stat-label">Soil Type</span>
          <span className="farm-card-stat-value">{farm.soil_texture.name}</span>
        </div>
      </div>

      <div className="farm-card-coords">
        📍 {Number(farm.latitude).toFixed(5)},{" "}
        {Number(farm.longitude).toFixed(5)}
      </div>

      {farm.agroforestry_type.length > 0 && (
        <div className="farm-card-tags">
          {farm.agroforestry_type.map(type => (
            <span key={type.id} className="farm-tag farm-tag-agroforestry">
              {type.type_name}
            </span>
          ))}
        </div>
      )}

      {tags.length > 0 && (
        <div className="farm-card-tags">
          {tags.map(tag => (
            <span key={tag} className="farm-tag farm-tag-trait">
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
