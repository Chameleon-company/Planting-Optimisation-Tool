import { useNavigate } from "react-router-dom";
import FarmsTableRow from "./farmsTableRow";
import FarmPageNav from "@/components/profile/profilePageNav";
import { Farm } from "@/hooks/useUserProfiles";

interface FarmsTableProps {
  farms: Farm[];
  isLoading: boolean;
  user: { name: string; role?: string } | null;
  page: number;
  totalPages: number;
  setPage: (page: number) => void;
  selectedFarmId: number | null;
  onSelectFarm: (id: number | null) => void;
}

const COLUMNS = [
  "Farm",
  "Coordinates",
  "Area",
  "Rainfall",
  "Soil texture",
  "Temperature",
  "Coastal",
];

// Import props from page
export default function FarmsTable({
  farms,
  isLoading,
  user,
  page,
  totalPages,
  setPage,
  selectedFarmId,
  onSelectFarm,
}: FarmsTableProps) {
  const navigate = useNavigate();

  // If there is no user, then display nothing
  if (!user) {
    return (
      <div className="farms-table-empty">
        <p className="farms-table-empty-text">
          You must be logged in to view farms.
        </p>
      </div>
    );
  }

  // if loading then display empty loading array with css styling
  if (isLoading) {
    return (
      <div className="farms-table-empty">
        <div className="farms-table-skeleton">
          {Array.from({ length: 9 }).map((_, i) => (
            <div key={i} className="farms-table-skeleton-row" />
          ))}
        </div>
      </div>
    );
  }

  // If the user has no farms, display this
  if (farms.length === 0) {
    return (
      <div className="farms-table-empty">
        <p className="farms-table-empty-text">No farms registered yet.</p>
        <p className="farms-table-empty-subtext">
          Use the Register farm button to add your first property.
        </p>
      </div>
    );
  }

  // Return table
  return (
    <div className="farms-table-wrapper">
      <table className="farms-table">
        <thead>
          {/* Table header element, map columns to table */}
          <tr>
            {COLUMNS.map(col => (
              <th key={col} className="farms-table-th">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        {/* Table body element */}
        <tbody>
          {/* map farm array given by page props as a farm table row */}
          {farms.map(farm => (
            <FarmsTableRow
              key={farm.id}
              farm={farm}
              // If selected, set selected ID to that farm
              isSelected={selectedFarmId === farm.id}
              // IF row is clicked then navigate to
              onRowClick={farm => navigate(`/profile?farmId=${farm.id}`)}
              // If row is selected, then stop event's triggering, this stops the navigate
              // if selected ID is not current id selected then change selectedFarmId
              // to that ID, if ID clicked is the same then set null
              onRowSelect={(e, farmId) => {
                e.stopPropagation();
                onSelectFarm(selectedFarmId === farmId ? null : farmId);
              }}
            />
          ))}
        </tbody>
      </table>

      {/* Page navigation logic from /profile */}
      {totalPages > 1 && (
        <div className="farms-table-footer">
          <FarmPageNav page={page} totalPages={totalPages} setPage={setPage} />
        </div>
      )}
    </div>
  );
}
