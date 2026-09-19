import { GeoJSON, Polyline } from "react-leaflet";
import L from "leaflet";
import type { GeoJsonObject } from "geojson";

interface Props {
  boundary: GeoJsonObject | null;
  // List of lat, lng points
  lines: [number, number][][];
  grid: GeoJsonObject | null;
  // Optional prefix so line keys stay unique when several of these render on one map
  keyPrefix?: string | number;
}

// Renders no map or tiles of its own used only inside MapContainer to display fill, outline, lines
export default function FarmLayers({
  boundary,
  lines,
  grid,
  keyPrefix,
}: Props) {
  return (
    <>
      {/* If boundary exists, draw its outline in white and fill with red */}
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
      {/* Draw a polyline for every line in lines */}
      {lines.map((line, i) => (
        <Polyline
          key={keyPrefix !== undefined ? `${keyPrefix}-line-${i}` : i}
          positions={line}
          pathOptions={{
            color: "#ffff00",
            weight: 1,
            dashArray: "4 4",
            opacity: 0.55,
          }}
        />
      ))}
      {/* If grid exists, draw a small green point at each tree's lat/lng location */}
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
    </>
  );
}
