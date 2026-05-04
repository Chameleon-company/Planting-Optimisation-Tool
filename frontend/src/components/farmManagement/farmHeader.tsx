// Create interface to set types for ProfileHeaderProps
interface FarmManagmentHeaderProps {
  isLoading: boolean;
  totalFarms?: number;
}

// Display ProfileHeader as a page header for the user's environmental profile
export default function FarmsHeader({
  isLoading,
  totalFarms,
}: FarmManagmentHeaderProps) {
  return (
    <div className="farms-page-heading">
      <h1 className="farms-page-title">Farm Management</h1>
      <span className="farms-total-badge">
        {isLoading ? "-" : `${totalFarms} farm${totalFarms !== 1 ? "s" : ""}`}
      </span>
    </div>
  );
}
