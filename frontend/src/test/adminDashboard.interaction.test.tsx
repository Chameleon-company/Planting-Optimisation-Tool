// @vitest-environment jsdom
// test 1 : species management card click navigates to species management page
// test 2 : farm management card click navigates to farm management page
// test 3 : weighting methods card click navigates to weighting methods page
// test 4 : exclusion rules card click navigates to exclusion rules page

import { render, screen } from "@testing-library/react"; // use to render the react component inside the test environment and to query the DOM for elements
import userEvent from "@testing-library/user-event"; // simulates real user actions like clicking, typing, etc.
import { MemoryRouter, Route, Routes } from "react-router-dom"; // provides a router context for testing components that use routing, without needing a real browser environment
import { HelmetProvider } from "react-helmet-async"; // provides a context for managing changes to the document head, such as title and meta tags, in a React application
import AdminDashboard from "@/pages/admin/AdminDashboard"; // imports the AdminDashboard component to be tested

// Helper function to render the AdminDashboard component with necessary providers and routing context
// This function sets up the test environment for the AdminDashboard component, including routing and head management.
function renderDashboard() {
  return render(
    <HelmetProvider>
      <MemoryRouter initialEntries={["/admin"]}>
        <Routes>
          <Route path="/admin" element={<AdminDashboard />} />
          <Route
            path="/admin/species"
            element={<div>Species Management Page</div>}
          />
          <Route path="/farms" element={<div>Farm Management Page</div>} />
          <Route
            path="/admin/settings/weighting"
            element={<div>Weighting Methods Page</div>}
          />
          <Route
            path="/admin/settings/exclusions"
            element={<div>Exclusion Rules Page</div>}
          />
        </Routes>
      </MemoryRouter>
    </HelmetProvider>
  );
}

// Test suite for AdminDashboard UI interactions
// This suite contains tests that simulate user interactions with the AdminDashboard component and verify that the correct navigation occurs when specific cards are clicked.
// Each test uses the renderDashboard helper function to set up the component and then simulates a user click on a specific card, checking that the expected page content is displayed afterward.
// The tests ensure that the navigation functionality of the AdminDashboard component works as intended, providing a reliable user experience.
//
describe("AdminDashboard UI interactions", () => {
  // Test case 1: Navigates to Species Management page when the corresponding card is clicked
  it("navigates to Species Management when its card is clicked", async () => {
    const user = userEvent.setup(); // sets up a user event simulation environment
    renderDashboard(); // renders the AdminDashboard component with routing context

    await user.click(
      // simulates a user click on the Species Management card
      screen.getByRole("link", { name: /species management/i })
    );

    expect(screen.getByText("Species Management Page")).toBeInTheDocument();
  });
  // Test case 2: Navigates to Farm Management page when the corresponding card is clicked
  it("navigates to Farm Management when its card is clicked", async () => {
    const user = userEvent.setup();
    renderDashboard();

    await user.click(
      // simulates a user click on the Farm Management card
      screen.getByRole("link", { name: /farm management/i })
    );

    expect(screen.getByText("Farm Management Page")).toBeInTheDocument();
  });

  // Test case 3: Navigates to Weighting Methods page when the corresponding card is clicked
  it("navigates to Weighting Methods when its card is clicked", async () => {
    const user = userEvent.setup();
    renderDashboard();

    await user.click(screen.getByRole("link", { name: /weighting methods/i }));

    expect(screen.getByText("Weighting Methods Page")).toBeInTheDocument();
  });

  // Test case 4: Navigates to Exclusion Rules page when the corresponding card is clicked
  it("navigates to Exclusion Rules when its card is clicked", async () => {
    const user = userEvent.setup();
    renderDashboard();

    await user.click(screen.getByRole("link", { name: /exclusion rules/i }));

    expect(screen.getByText("Exclusion Rules Page")).toBeInTheDocument();
  });
});
