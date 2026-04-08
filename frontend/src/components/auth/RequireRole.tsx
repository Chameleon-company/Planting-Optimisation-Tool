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
  const { user } = useAuth();

  // Not logged in → redirect home (or later login page)
  if (!user) {
    return <Navigate to="/" replace />;
  }

  // Role not allowed → redirect home
  if (!allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}
