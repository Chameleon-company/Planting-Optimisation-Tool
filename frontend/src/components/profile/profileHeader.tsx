// Create interface to set types for ProfileHeaderProps
interface FarmProfileHeaderProps {
  farmerName?: string;
  farmCount: number;
}

// Display ProfileHeader as a page header for the farmer's environmental profile
export default function ProfileHeader({
  farmerName,
  farmCount,
}: FarmProfileHeaderProps) {
  return (
    <header className="farmProfileHeader">
      <h1 className="farmProfileTitle">Environmental Profile</h1>
      <p className="farmProfileSubtitle">
        {farmerName
          ? `${farmerName} · ${farmCount} ${farmCount === 1 ? "Farm" : "Farms"}`
          : ""}
      </p>
    </header>
  );
}
