import { it, expect, describe } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import UserEvent from "@testing-library/user-event";

import { AuthProvider, useAuth } from "../contexts/AuthContext";

// Create TestComponent to display all elements from AuthContext
const TestComponent = () => {
  const { user, login, logout } = useAuth();
  return (
    <div>
      <p>{user ? `Logged in as ${user.name}` : "Not logged in"}</p>
      <button
        onClick={() => login({ email: "test@test.com", password: "password" })}
      >
        Login
      </button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

describe("AuthContext", () => {
  it("should start logged out", () => {
    // Render TestComponent inside wrapper of AuthProvider
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    //Expect TestComponent to display default options
    expect(screen.getByText(/Logged in as/i)).toBeInTheDocument();
  });

  it("should set user after login", async () => {
    // Render TestComponent inside wrapper of AuthProvider
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Await fake user to click Login button
    await UserEvent.click(screen.getByText("Login"));

    // Wait for screen to display 'Logged in as' inside render, or time out
    await waitFor(() => {
      expect(screen.getByText(/Logged in as/)).toBeInTheDocument();
    });
  });

  it("clears user after logout", async () => {
    // Render TestComponent inside wrapper of AuthProvider
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Wait for fake user to click login, and await screen to display 'Logged in as'
    await UserEvent.click(screen.getByText("Login"));
    await waitFor(() => screen.getByText(/Logged in as/));

    // Wait for fake user to click logout, and await screen to display 'Not logged in'
    await UserEvent.click(screen.getByText("Logout"));
    expect(screen.getByText("Not logged in")).toBeInTheDocument();
  });

  it("should set the correct role and farms on the fake user after login", async () => {
    // Create TestRoleComponent that displays data associated with logged in user
    const TestRoleComponent = () => {
      const { user, login } = useAuth();
      return (
        <div>
          <p>{user ? `Role: ${user.role}` : "No role"}</p>
          <p>{user ? `Farms: ${user.farms.join(", ")}` : "No farms"}</p>
          <button
            onClick={() =>
              login({ email: "test@test.com", password: "password" })
            }
          >
            Login
          </button>
        </div>
      );
    };

    // Render TestRoleComponent displaying user's farms and role
    render(
      <AuthProvider>
        <TestRoleComponent />
      </AuthProvider>
    );

    // Await fake user to click login
    await UserEvent.click(screen.getByText("Login"));

    // Wait for and expect screen to display, fake user's role, and associated user's farms
    await waitFor(() => {
      expect(screen.getByText("Role: admin")).toBeInTheDocument();
      expect(
        screen.getByText("Farms: Unknown Farm 1, Unknown Farm 2")
      ).toBeInTheDocument();
    });
  });

  it("should throw if useAuth is used outside provider", () => {
    // If Context is thrown, expect correct error message to display
    expect(() => render(<TestComponent />)).toThrow(
      "useAuth must be used inside <AuthProvider>"
    );
  });
});
