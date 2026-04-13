import { Helmet } from "react-helmet-async";
import FarmProfileHeader from "@/components/profile/profileHeader";
import FarmList from "@/components/profile/profileFarms";
import { useProfiles } from "../hooks/useProfiles";
import { useAuth } from "@/contexts/AuthContext";

function TempLoginButton() {
  const { user, login, logout } = useAuth();

  const handleLogin = () => {
    login({ email: "testuser123@test.com", password: "password123" });
  };

  if (user) {
    return (
      <div>
        <p>
          Logged in as: {user.name} ({user.role})
        </p>
        <button onClick={logout}>Logout</button>
      </div>
    );
  }

  return <button onClick={handleLogin}>Temp Login</button>;
}

function ProfilePage() {
  const { user } = useAuth();
  const { farms, isLoading, page, setPage, totalPages, totalFarms } =
    useProfiles();

  return (
    <div>
      <Helmet>
        <title>Environmental Profile | Planting Optimisation Tool</title>
      </Helmet>

      <TempLoginButton />

      {user && (
        <>
          <FarmProfileHeader farmerName={user.name} farmCount={totalFarms} />
          <FarmList
            farms={farms}
            isLoading={isLoading}
            user={user}
            page={page}
            totalPages={totalPages}
            setPage={setPage}
          />
        </>
      )}
    </div>
  );
}

export default ProfilePage;
