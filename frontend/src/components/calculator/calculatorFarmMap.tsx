import { useMemo } from "react";
import { MapContainer, TileLayer } from "react-leaflet";
import L from "leaflet";
import type { GeoJsonObject } from "geojson";
import { computeGridLines } from "@/utils/calculatorGridLines";
import FarmLayers from "@/components/calculator/calculatorFarmLayers";
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
  // Set bounds to rerun each time prop: boundary is changed
  const bounds = useMemo(() => {
    // If no boundary return Null
    if (!boundary) return null;
    // Wrap the GeoJSON in a temporary Leaflet layer getBounds returns the smallest rectangle containing the whole shape
    try {
      return L.geoJSON(boundary).getBounds();
    } catch {
      return null;
    }
  }, [boundary]);

  // Rerun grid lines computation if bounds, angle or spacing changes,
  // calling compute function handing props
  const gridLines = useMemo(() => {
    if (!bounds || optimalAngle === null) return [];
    return computeGridLines(bounds, optimalAngle, spacingY);
  }, [bounds, optimalAngle, spacingY]);

  // If no boundary was returned, return null on the map
  if (!bounds) return null;

  return (
    <div className="calc-map-container">
      <h3>Planting Map</h3>
      {/* Map container, bounds autozooms to field */}
      <MapContainer
        bounds={bounds}
        style={{ height: "450px", width: "100%" }}
        scrollWheelZoom={false}
        maxZoom={22}
      >
        {/* Tile layer, using world image map */}
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          attribution="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
          maxZoom={22}
          maxNativeZoom={18}
        />
        {/* Boundary, planting rows and tree dots (shared with the combined map) */}
        <FarmLayers boundary={boundary} lines={gridLines} grid={grid} />
      </MapContainer>
    </div>
  );
}
