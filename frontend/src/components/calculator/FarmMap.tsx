import { useMemo } from "react";
import { MapContainer, TileLayer, GeoJSON, Polyline } from "react-leaflet";
import L from "leaflet";
import type { GeoJsonObject } from "geojson";
import "leaflet/dist/leaflet.css";

interface Props {
  boundary: GeoJsonObject | null;
  grid: GeoJsonObject | null;
  optimalAngle: number | null;
  spacingY?: number;
}

export default function FarmMap({
  boundary,
  grid,
  optimalAngle,
  spacingY = 3,
}: Props) {
  const bounds = useMemo(() => {
    if (!boundary) return null;
    try {
      return L.geoJSON(boundary).getBounds();
    } catch {
      return null;
    }
  }, [boundary]);

  const gridLines = useMemo(() => {
    if (!bounds || optimalAngle === null) return [];

    const center = bounds.getCenter();
    const latExtent = bounds.getNorth() - bounds.getSouth();
    const lngExtent = bounds.getEast() - bounds.getWest();
    const diagDeg = Math.sqrt(latExtent * latExtent + lngExtent * lngExtent);

    const rad = (optimalAngle * Math.PI) / 180;
    const rowDirLat = Math.sin(rad);
    const rowDirLng = Math.cos(rad);
    const perpDirLat = Math.cos(rad);
    const perpDirLng = -Math.sin(rad);

    const spacingDeg = spacingY / 111000;
    const numLines = Math.ceil(diagDeg / spacingDeg) + 2;
    const halfLen = diagDeg / 2;

    const lines: [number, number][][] = [];
    for (let i = -Math.floor(numLines / 2); i <= Math.ceil(numLines / 2); i++) {
      const baseLat = center.lat + perpDirLat * i * spacingDeg;
      const baseLng = center.lng + perpDirLng * i * spacingDeg;
      lines.push([
        [baseLat - rowDirLat * halfLen, baseLng - rowDirLng * halfLen],
        [baseLat + rowDirLat * halfLen, baseLng + rowDirLng * halfLen],
      ]);
    }
    return lines;
  }, [bounds, optimalAngle, spacingY]);

  if (!bounds) return null;

  return (
    <div className="calc-map-container">
      <h3>Planting Map</h3>
      <MapContainer
        bounds={bounds}
        style={{ height: "450px", width: "100%" }}
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
        {gridLines.map((line, index) => (
          <Polyline
            key={index}
            positions={line}
            pathOptions={{
              color: "#ffff00",
              weight: 1,
              dashArray: "4 4",
              opacity: 0.55,
            }}
          />
        ))}
        {grid && (
          <GeoJSON
            data={grid}
            pointToLayer={(_feature, latlng) =>
              L.circleMarker(latlng, {
                radius: 1.5,
                fillColor: "#00ff88",
                color: "#00ff88",
                weight: 0,
                fillOpacity: 0.9,
              })
            }
          />
        )}
      </MapContainer>
    </div>
  );
}
