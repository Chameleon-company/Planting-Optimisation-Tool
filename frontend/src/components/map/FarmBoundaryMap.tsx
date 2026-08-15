import { useMemo } from "react";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import L from "leaflet";
import type { GeoJsonObject } from "geojson";
import "leaflet/dist/leaflet.css";

interface Props {
  boundary: GeoJsonObject | null;
  isLoading: boolean;
  error: string | null;
}

export default function FarmBoundaryMap({ boundary, isLoading, error }: Props) {
  const bounds = useMemo(() => {
    if (!boundary) return null;
    try {
      return L.geoJSON(boundary).getBounds();
    } catch {
      return null;
    }
  }, [boundary]);

  if (isLoading) {
    return (
      <div className="farm-map-section">
        <p className="farm-map-status">Loading map...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="farm-map-section">
        <p className="farm-map-status farm-map-error">{error}</p>
      </div>
    );
  }

  if (!bounds) return null;

  return (
    <div className="farm-map-section">
      <h3 className="farm-map-title">Farm Boundary</h3>
      <MapContainer
        bounds={bounds}
        style={{ height: "350px", width: "100%" }}
        scrollWheelZoom={false}
        maxZoom={22}
      >
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          attribution="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
          maxZoom={22}
          maxNativeZoom={18}
        />
        {boundary && (
          <GeoJSON
            data={boundary}
            style={{
              color: "#ffffff",
              weight: 2,
              fillOpacity: 0.3,
              fillColor: "#ff4444",
            }}
          />
        )}
      </MapContainer>
    </div>
  );
}
