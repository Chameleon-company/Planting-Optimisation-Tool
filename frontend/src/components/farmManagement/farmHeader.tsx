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
    <div>
      <h1>Farm Management</h1>
      <p>
        {isLoading ? "-" : `${totalFarms} farm${totalFarms !== 1 ? "s" : ""}`}
      </p>
    </div>
  );
}
