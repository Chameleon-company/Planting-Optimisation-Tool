import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  ReactNode,
} from "react";
// API base URL (adjust if needed)
const API_BASE = import.meta.env.VITE_API_URL;

// Create interface for User that maps to User model in backend, excluding password
interface User {
  id: number;
  name: string;
  email: string;
  role: "officer" | "supervisor" | "admin";
}

// Create interface for AuthContextType, user of interface User type or null, isLoading as Boolean,
// Login as a function taking credentials which has two parts, email and password, promising void when complete.
// Logout is a function promising void when complete
interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (credentials: { email: string; password: string }) => Promise<void>;
  logout: () => void;
}

// Set AuthContext as a context with AuthContextType or null as it's type, default is null
const AuthContext = createContext<AuthContextType | null>(null);

// Create function AuthProvider with children of ReactNode type
export function AuthProvider({ children }: { children: ReactNode }) {
  // Set user and isLoading as a useState of interfacetype User or null, defaults are null/false
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(
    () => !!localStorage.getItem("access_token")
  );

  const fetchCurrentUser = useCallback(async (token: string) => {
    const userResponse = await fetch(`${API_BASE}/auth/users/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!userResponse.ok) {
      throw new Error("Failed to fetch user details");
    }

    const userData = await userResponse.json();

    const realUser: User = {
      id: userData.id,
      name: userData.name || userData.email,
      email: userData.email,
      role: userData.role,
    };

    setUser(realUser);
  }, []);

  const login = useCallback(
    async (credentials: { email: string; password: string }) => {
      setIsLoading(true);

      try {
      } finally {
        setIsLoading(false);
      }
    },
    [fetchCurrentUser]
  );

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    setUser(null);
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      return;
    }

    const restoreUser = async () => {
      setIsLoading(true);

      try {
        await fetchCurrentUser(token);
      } catch (error) {
        console.error("Failed to restore user session:", error);
        localStorage.removeItem("access_token");
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    restoreUser();
  }, [fetchCurrentUser]);

  // Calling AuthContext with its provider will provide values (variables and functions), user, isLoading, login, logout
  // To all children wrapped by the Provider
  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// UseAuth Function is what is used in code, if context can be found, return it to caller, if called outside provider
// Range then return "useAuth must be used inside <AuthProvider>", the entire app is wrapped by AuthProvider
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside <AuthProvider>");
  return context;
}
