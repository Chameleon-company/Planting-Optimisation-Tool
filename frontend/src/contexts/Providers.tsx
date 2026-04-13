import { ReactNode } from "react";
import { AuthProvider } from "./AuthContext";

// Create Providers function with children set as ReactNode type
// All providers will be set in here, and just the Providers function will wrap the App
export function Providers({ children }: { children: ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>;
}
