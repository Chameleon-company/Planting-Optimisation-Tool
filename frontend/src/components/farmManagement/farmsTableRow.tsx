import { Farm } from "@/hooks/useUserProfiles";

// Interface for table row, on row click gives a farm to void function
// On row select gives e, as a mouse event, and the farmID
interface FarmsTableRowProps {
  farm: Farm;
  isSelected: boolean;
  onRowClick: (farm: Farm) => void;
  onRowSelect: (e: React.MouseEvent, farmId: number) => void;
}

// Simple function for changing the coastal boolean display depending on if its yes or no
function BoolCoastal({ value }: { value: boolean }) {
  return (
    <span
      className={`farm-status-pill ${value ? "farm-status-active" : "farm-status-inactive"}`}
    >
      {value ? "Yes" : "No"}
    </span>
  );
}

export default function FarmsTableRow({
  farm,
  isSelected,
  onRowClick,
  onRowSelect,
}: FarmsTableRowProps) {
  return (
    // Change .css depending on if selected, on click triggers onrowclick handing row's farm
    // title when hovered over with mouse will display 'View farm dashboard'
    <tr
      className={`farms-table-row ${isSelected ? "farms-table-row-selected" : ""}`}
      onClick={() => onRowClick(farm)}
      title="View farm dashboard"
    >
      {/* Farm ID and row selector */}
      <td className="farms-table-td farms-table-td-name">
        <div className="farms-table-name-cell">
          <span
            className={`farms-table-selector ${isSelected ? "farms-table-selector-active" : ""}`}
            // If checkbox clicked, trigger on row select
            onClick={e => onRowSelect(e, farm.id)}
            title={isSelected ? "Deselect" : "Select"}
            role="checkbox"
            // With this you can press tab and change between checkboxes
            tabIndex={0}
            // If enter is pressed while farm selected treat that as mouse click
            onKeyDown={e => {
              if (e.key === " " || e.key === "Enter")
                onRowSelect(e as unknown as React.MouseEvent, farm.id);
            }}
          />
          <span className="farms-table-farm-name">Farm #{farm.id}</span>
        </div>
      </td>

      {/* Rows for consildated data on farms */}
      <td className="farms-table-td farms-table-td-coords">
        {Number(farm.latitude).toFixed(4)}, {Number(farm.longitude).toFixed(4)}
      </td>
      <td className="farms-table-td">{farm.area_ha} ha</td>
      <td className="farms-table-td">{farm.rainfall_mm} mm</td>
      <td className="farms-table-td">{farm.soil_texture.name}</td>
      <td className="farms-table-td">{farm.temperature_celsius}°C</td>

      <td className="farms-table-td">
        <BoolCoastal value={farm.coastal} />
      </td>
    </tr>
  );
}
