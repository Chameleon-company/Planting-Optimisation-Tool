import { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

// // REQUIRE ROLE GUARD (#155 enhancement)
// // Protects admin routes from unauthorized access

type Props = {
  children: ReactNode;
  allowedRoles: string[];
};

export default function RequireRole({ children, allowedRoles }: Props) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  // Not logged in → redirect to login page
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Role not allowed → redirect home
  if (!allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}
