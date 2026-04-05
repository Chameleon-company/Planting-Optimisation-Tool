import { ReactNode } from "react";
import { AuthProvider } from "./AuthContext";
import { SessionProvider } from "./SessionContext";

// Create Providers function with children set as ReactNode type
// All providers will be set in here, and just the Providers function will wrap the App
export function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <SessionProvider>{children}</SessionProvider>
    </AuthProvider>
  );
}
