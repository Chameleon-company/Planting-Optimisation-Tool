import { Helmet } from "react-helmet-async";
import { useAuth } from "@/contexts/AuthContext";
import { useSession } from "@/contexts/SessionContext";
import FarmProfileHeader from "@/components/profile/profileHeader";
import FarmList from "@/components/profile/profileFarms";

function ProfilePage() {
  const { user, login, isLoading: authLoading } = useAuth();
  const { farms, isLoading: sessionLoading } = useSession();

  // Temp login mock function
  const handleLogin = async () => {
    try {
      await login({
        email: "john@example.com",
        password: "password123",
      });
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  const isLoading = authLoading || sessionLoading;

  return (
    <div>
      <Helmet>
        <title>Environmental Profile | Planting Optimisation Tool</title>
      </Helmet>

      <FarmProfileHeader
        farmerName={user?.name ?? "..."}
        farmCount={farms.length}
      />

      {/* Temp Login Button */}
      {!user && (
        <button
          onClick={handleLogin}
          disabled={isLoading}
          className="loginButton"
        >
          {isLoading ? "Logging in..." : "Login (Demo)"}
        </button>
      )}

      {/* List of farms */}
      <FarmList />
    </div>
  );
}

export default ProfilePage;
