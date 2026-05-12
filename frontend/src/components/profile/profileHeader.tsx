// Create interface to set types for ProfileHeaderProps
interface FarmProfileHeaderProps {
  userName?: string;
  farmCount: number;
}

// Display ProfileHeader as a page header for the user's environmental profile
export default function ProfileHeader({
  userName,
  farmCount,
}: FarmProfileHeaderProps) {
  return (
    <header className="page-header">
      <h1>Environmental Profile</h1>
      <p>
        {userName
          ? `${userName} · ${farmCount} ${farmCount === 1 ? "Farm" : "Farms"}`
          : ""}
      </p>
    </header>
  );
}
