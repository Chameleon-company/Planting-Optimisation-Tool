import type { LatLngBounds } from "leaflet";

// Compute the planting-row lines for a field. Takes the field's bounding box
// the optimal angle from the backend and the row spacing returns a list of lines
// each a pair of [lat, lng] points
export function computeGridLines(
  bounds: LatLngBounds,
  optimalAngle: number,
  spacingY: number
): [number, number][][] {
  // Create a rectangle using the centre of the farm and the far edges as limits
  const center = bounds.getCenter();
  const latExtent = bounds.getNorth() - bounds.getSouth();
  const lngExtent = bounds.getEast() - bounds.getWest();
  const diagDeg = Math.sqrt(latExtent * latExtent + lngExtent * lngExtent);

  // Convert angle to radians, then use sin/cos to build two unit direction vectors:
  // one pointing along each row, one pointing to the step between rows
  const rad = (optimalAngle * Math.PI) / 180;
  const rowDirLat = Math.sin(rad);
  const rowDirLng = Math.cos(rad);
  const perpDirLat = Math.cos(rad);
  const perpDirLng = -Math.sin(rad);

  // Convert spacing into degrees, find number of lines by dividing the diagonal
  // length by the spacing needed per line
  const spacingDeg = spacingY / 111000;
  const numLines = Math.ceil(diagDeg / spacingDeg) + 2;
  const halfLen = diagDeg / 2;

  // Create empty array containing a list of lines with lat/lng as said earlier
  const lines: [number, number][][] = [];
  // Starting from the first line, negative as its below the middle starting line
  // until the furthest line, e.g. going from -3 to +3, instead of 0 to 6
  for (let i = -Math.floor(numLines / 2); i <= Math.ceil(numLines / 2); i++) {
    // Start at the center line and step out perpendicularly either - or + direction depending on i
    const baseLat = center.lat + perpDirLat * i * spacingDeg;
    const baseLng = center.lng + perpDirLng * i * spacingDeg;
    // Go back and forward across the line starting from the center, going half the length of the bounding box
    // then push that result to lines, which has the structure for the array of lines with coordinates
    lines.push([
      [baseLat - rowDirLat * halfLen, baseLng - rowDirLng * halfLen],
      [baseLat + rowDirLat * halfLen, baseLng + rowDirLng * halfLen],
    ]);
  }
  return lines;
}
