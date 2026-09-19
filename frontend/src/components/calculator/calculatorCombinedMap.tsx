import { useState, useEffect, useMemo, useCallback } from "react";
import { MapContainer, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import { useFarmMap } from "@/hooks/useFarmMap";
import { computeGridLines } from "@/utils/calculatorGridLines";
import type { FarmEstimationResult } from "@/hooks/useCalculator";
import FarmLayers from "@/components/calculator/calculatorFarmLayers";

// Function takes a list of rectangles, one per farm in the aggregate
function FitBounds({ boundsList }: { boundsList: L.LatLngBounds[] }) {
  const map = useMap();
  useEffect(() => {
    // If no boundries bail out
    if (boundsList.length === 0) return;
    // Set new variable, all, to create a rectangle from the edges of the first farm
    const all = L.latLngBounds(
      boundsList[0].getSouthWest(),
      boundsList[0].getNorthEast()
    );
    // For each farm in the list, extend all one by one so that by the end all farms are enclosed
    boundsList.forEach(b => all.extend(b));
    // using UseMap, call fitBounds function using all, with a padding of 40px on all sides
    map.fitBounds(all, { padding: [40, 40] });
    // Rererunning if boundslist's length or the useMap changes
  }, [boundsList, map]);
  return null;
}

function CombinedFarmLayers({
  farmId,
  optimalAngle,
  spacingY,
  onBounds,
}: {
  farmId: number;
  optimalAngle: number | null;
  spacingY: number;
  onBounds: (farmId: number, bounds: L.LatLngBounds) => void;
}) {
  // Get boundary and grid for called farmID
  const { boundary, grid } = useFarmMap(farmId);

  useEffect(() => {
    // If no boundary return
    if (!boundary) return;
    try {
      // Get smallest rectangle containing the boundary of the farm
      const b = L.geoJSON(boundary).getBounds();
      // If the rectangle is valid, then call onBounds, handing farmId and
      // new rectangle back to parent
      if (b.isValid()) onBounds(farmId, b);
    } catch {
      // ignore boundaries we can't parse
    }
  }, [boundary, farmId, onBounds]);

  const lines = useMemo(() => {
    if (!boundary || optimalAngle === null) return [];
    try {
      // Get smallest rectangle containing the boundary of the farm
      const b = L.geoJSON(boundary).getBounds();
      // Hand back list of coordinates and lines from computeGridLines function
      return computeGridLines(b, optimalAngle, spacingY);
    } catch {
      return [];
    }
  }, [boundary, optimalAngle, spacingY]);

  // Boundary, rows and dots for this farm — same shared component as the single map.
  // keyPrefix={farmId} keeps line keys unique when several farms share one map.
  return (
    <FarmLayers
      boundary={boundary}
      lines={lines}
      grid={grid}
      keyPrefix={farmId}
    />
  );
}

interface Props {
  results: FarmEstimationResult[];
  spacingY?: number;
}
export default function CombinedFarmMap({ results, spacingY = 3 }: Props) {
  // Create array filtering only farms where the farm  call succeeded
  const successful = results.filter(r => r.status === "success");
  // Create string, IdSig(nature) including only the IDs of successful farms seperating Ids by ','
  const idSig = successful.map(r => r.farm_id).join(",");

  // Create useState for farmbounds, using a record whose key is a number, and values are
  // the rectangles mentioned
  const [farmBounds, setFarmBounds] = useState<Record<number, L.LatLngBounds>>(
    {}
  );

  // Reset farmBoundaries if successful farms changes
  useEffect(() => {
    setFarmBounds({});
  }, [idSig]);

  // This gets passed to onBounds, we then setFarmBounds by copying the existing farmBounds object
  // and then adding or overwriting the data for this farmID, using useCallback to retain just one function
  // across all calls
  const handleBounds = useCallback((farmId: number, b: L.LatLngBounds) => {
    setFarmBounds(prev => ({ ...prev, [farmId]: b }));
  }, []);

  // creat boundsList array containing all the values from farmBounds
  // so instead of 1: A, 2: B, its now, A, B, C, etc
  const boundsList = useMemo(() => Object.values(farmBounds), [farmBounds]);

  return (
    <div className="calc-map-container">
      <h3>Combined Planting Map</h3>
      <MapContainer
        center={[0, 0]}
        zoom={2}
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
        {successful.map(r => (
          // Render successful farm layers one at a time, mapping out the successful array
          // Using the CombinedFarmLayers function
          <CombinedFarmLayers
            key={r.farm_id}
            farmId={r.farm_id}
            optimalAngle={r.optimal_angle ?? null}
            spacingY={spacingY}
            onBounds={handleBounds}
          />
        ))}
        {/* Then call FitBounds function, handing the boundaries of all successful farms */}
        <FitBounds boundsList={boundsList} />
      </MapContainer>
    </div>
  );
}
