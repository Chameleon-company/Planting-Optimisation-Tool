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
      className={`farmStatusPill ${value ? "farmStatusActive" : "farmStatusInactive"}`}
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
      className={`farmsTableRow ${isSelected ? "farmsTableRowSelected" : ""}`}
      onClick={() => onRowClick(farm)}
      title="View farm dashboard"
    >
      {/* Farm ID and row selector */}
      <td className="farmsTableTd farmsTableTdName">
        <div className="farmsTableNameCell">
          <span
            className={`farmsTableSelector ${isSelected ? "farmsTableSelectorActive" : ""}`}
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
          <span className="farmsTableFarmName">Farm #{farm.id}</span>
        </div>
      </td>

      {/* Rows for consildated data on farms */}
      <td className="farmsTableTd farmsTableTdCoords">
        {Number(farm.latitude).toFixed(4)}, {Number(farm.longitude).toFixed(4)}
      </td>
      <td className="farmsTableTd">{farm.area_ha} ha</td>
      <td className="farmsTableTd">{farm.rainfall_mm} mm</td>
      <td className="farmsTableTd">{farm.soil_texture.name}</td>
      <td className="farmsTableTd">{farm.temperature_celsius}°C</td>

      <td className="farmsTableTd">
        <BoolCoastal value={farm.coastal} />
      </td>
    </tr>
  );
}
