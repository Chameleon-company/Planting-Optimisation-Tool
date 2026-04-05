import {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
  useEffect,
} from "react";
import { useAuth } from "./AuthContext";

// Create interface for farms that match with backend, later fed into frontend
export interface SoilTexture {
  name: string;
}
export interface AgroforestryType {
  name: string;
}
export interface Farm {
  id: number;
  rainfall_mm: number;
  temperature_celsius: number;
  elevation_m: number;
  ph: number;
  soil_texture: SoilTexture;
  area_ha: number;
  latitude: number;
  longitude: number;
  coastal: boolean;
  riparian: boolean;
  nitrogen_fixing: boolean;
  shade_tolerant: boolean;
  bank_stabilising: boolean;
  slope: number;
  agroforestry_type: AgroforestryType[];
}

// Create interface for SessionContextType
interface SessionContextType {
  farms: Farm[];
  isLoading: boolean;
  refreshFarms: () => Promise<void>;
}

// Set SessionContext with SessionContextType or null as type
const SessionContext = createContext<SessionContextType | null>(null);

// Create function SessionProvider with children of ReactNode type
export function SessionProvider({ children }: { children: ReactNode }) {
  // Set farms as a useState of Farm interface, with empty array as default
  const [farms, setFarms] = useState<Farm[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Get the authenticated user from AuthContext
  const { user } = useAuth();

  // Create function fetchFarms, using callback to get farms for the current user
  const fetchFarms = useCallback(async () => {
    // Only fetch if we have a user
    if (!user?.id) {
      setFarms([]);
      return;
    }

    setIsLoading(true);
    try {
      // TODO: replace with real API calls
      // const response = await api.get('/users/user.id/farms');
      // setFarms(response.data);

      // Mock data for now
      const fakeFarms: Farm[] = [
        {
          id: 1,
          rainfall_mm: 800,
          temperature_celsius: 18,
          elevation_m: 120,
          ph: 6.5,
          soil_texture: { name: "Loam" },
          area_ha: 4.321,
          latitude: -37.81234,
          longitude: 144.96345,
          coastal: false,
          riparian: true,
          nitrogen_fixing: true,
          shade_tolerant: false,
          bank_stabilising: false,
          slope: 3.45,
          agroforestry_type: [{ name: "Silvopasture" }],
        },
      ];
      setFarms(fakeFarms);
    } catch (error) {
      console.error("Failed to fetch farms:", error);
      setFarms([]);
    } finally {
      setIsLoading(false);
    }
  }, [user?.id]); // Recreate when user ID changes

  // Create function refreshFarms to manually trigger a refresh
  const refreshFarms = useCallback(async () => {
    await fetchFarms();
  }, [fetchFarms]);

  // Effect to fetch farms when user logs in or user ID changes
  useEffect(() => {
    fetchFarms();
  }, [fetchFarms]); // fetchFarms will change when user ID changes

  // Calling SessionContext with its provider will provide values (variables and functions), farms, isLoading, refreshFarms
  // To all children wrapped by the Provider
  return (
    <SessionContext.Provider value={{ farms, isLoading, refreshFarms }}>
      {children}
    </SessionContext.Provider>
  );
}

// UseSession Function is what is used in code, if context can be found, return it to caller, if called outside provider
// Range then return "useSession must be used inside <SessionProvider>", the entire app is wrapped by SessionProvider
export function useSession() {
  const context = useContext(SessionContext);
  if (!context)
    throw new Error("useSession must be used inside <SessionProvider>");
  return context;
}
