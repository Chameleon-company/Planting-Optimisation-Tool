import {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
} from "react";

// Create interface for User that maps to User model in backend, excluding password
interface User {
  id: number;
  name: string;
  email: string;
  role: "officer" | "supervisor" | "admin";
  farms: string[];
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
  const [user, setUser] = useState<User | null>({
    id: 1,
    name: "John Doe",
    email: "admin@test.com",
    role: "admin",
    farms: [],
  });
  const [isLoading, setIsLoading] = useState(false);

  // Create function login, using callback which creates a new function for each call
  const login = useCallback(
    async (credentials: { email: string; password: string }) => {
      setIsLoading(true);
      try {
        // TODO: replace with real API call
        // e.g const response = await api.post('/auth/login', credentials);
        // then setUser(response.data);
        const fakeUser: User = {
          id: 1,
          name: "John Doe",
          email: credentials.email,
          role: "admin",
          farms: ["Unknown Farm 1", "Unknown Farm 2"],
        };
        setUser(fakeUser);
      } finally {
        setIsLoading(false);
      }
      // Empty dependency array means this function is only created on mount
    },
    []
  );

  // Create function logout, using callback set user to null and exit
  const logout = useCallback(() => {
    setUser(null);
  }, []);

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
