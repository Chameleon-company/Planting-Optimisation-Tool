// @vitest-environment jsdom

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";

// Components to test
import AboutSection from "../components/home/aboutsection";
import FeatureCard from "../components/home/featurecards";
import FeaturesSection from "../components/home/features";
import Landing from "../components/home/landing";
import NotFoundContent from "../components/notfound/notfoundcontent";

describe("AboutSection", () => {
  it("renders title and description correctly", () => {
    // Render AboutSection with mock props
    render(
      <AboutSection
        logoSrc="/logo.svg"
        logoAlt="Test Logo"
        tagline="A tool by xpandFoundation"
        title="About Us"
        description="We help farmers discover the best tree species."
      />
    );

    // Expect title and description to be present
    expect(screen.getByText("About Us")).toBeInTheDocument();
    expect(
      screen.getByText("We help farmers discover the best tree species.")
    ).toBeInTheDocument();
  });

  it("renders logo with correct src and alt", () => {
    // Render AboutSection with mock props
    render(
      <AboutSection
        logoSrc="/logo.svg"
        logoAlt="Test Logo"
        tagline="A tool by xpandFoundation"
        title="About Us"
        description="We help farmers discover the best tree species."
      />
    );

    // Expect logo to have correct attributes
    const img = screen.getByRole("img");
    expect(img).toHaveAttribute("src", "/logo.svg");
    expect(img).toHaveAttribute("alt", "Test Logo");
  });

  it("renders tagline text", () => {
    // Render AboutSection with mock props
    render(
      <AboutSection
        logoSrc="/logo.svg"
        logoAlt="Test Logo"
        tagline="A tool by xpandFoundation"
        title="About Us"
        description="We help farmers discover the best tree species."
      />
    );

    // Expect tagline to be present
    expect(screen.getByText("A tool by xpandFoundation")).toBeInTheDocument();
  });
});

describe("FeatureCard", () => {
  it("renders icon, title and text correctly", () => {
    // Render FeatureCard inside MemoryRouter as it uses Link
    render(
      <MemoryRouter>
        <FeatureCard
          icon="📍"
          title="Generate environmental profile"
          text="Provide your farm's boundaries."
          href="/profile"
        />
      </MemoryRouter>
    );

    // Expect all content to be present (icon and title appear twice: default + hover)
    expect(screen.getAllByText("📍").length).toBeGreaterThan(0);
    expect(
      screen.getAllByText("Generate environmental profile").length
    ).toBeGreaterThan(0);
    expect(
      screen.getByText("Provide your farm's boundaries.")
    ).toBeInTheDocument();
  });

  it("renders as a link pointing to the correct href", () => {
    // Render FeatureCard inside MemoryRouter as it uses Link
    render(
      <MemoryRouter>
        <FeatureCard
          icon="📍"
          title="Generate environmental profile"
          text="Provide your farm's boundaries."
          href="/profile"
        />
      </MemoryRouter>
    );

    // Expect link to point to correct page
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/profile");
  });

  it("renders the title in both default and hover content", () => {
    // Render FeatureCard inside MemoryRouter as it uses Link
    render(
      <MemoryRouter>
        <FeatureCard
          icon="📍"
          title="Generate environmental profile"
          text="Provide your farm's boundaries."
          href="/profile"
        />
      </MemoryRouter>
    );

    // Title appears in both defaultContent (featureTitle) and hoverContent (featureTitleLarge)
    const titles = screen.getAllByText("Generate environmental profile");
    expect(titles.length).toBe(2);
  });
});

describe("FeaturesSection", () => {
  it("renders all four feature cards", () => {
    // Render FeaturesSection inside MemoryRouter as cards use Link
    render(
      <MemoryRouter>
        <FeaturesSection />
      </MemoryRouter>
    );

    // Each title appears twice (defaultContent + hoverContent), so use getAllByText
    expect(
      screen.getAllByText("Agroforestry Recommendations").length
    ).toBeGreaterThan(0);
    expect(
      screen.getAllByText("Sapling Estimation Calculator").length
    ).toBeGreaterThan(0);
    expect(
      screen.getAllByText("Generate Environmental Profile").length
    ).toBeGreaterThan(0);
    expect(screen.getAllByText("Species Information").length).toBeGreaterThan(
      0
    );
  });

  it("renders three links with correct hrefs", () => {
    // Render FeaturesSection inside MemoryRouter as cards use Link
    render(
      <MemoryRouter>
        <FeaturesSection />
      </MemoryRouter>
    );

    // Expect all three links to point to correct pages
    const links = screen.getAllByRole("link");
    const hrefs = links.map(l => l.getAttribute("href"));
    expect(hrefs).toContain("/profile");
    expect(hrefs).toContain("/calculator");
    expect(hrefs).toContain("/species");
  });

  it("renders four feature card links", () => {
    // Render FeaturesSection inside MemoryRouter as cards use Link
    render(
      <MemoryRouter>
        <FeaturesSection />
      </MemoryRouter>
    );

    // Expect four links, one per feature card
    const links = screen.getAllByRole("link");
    expect(links.length).toBe(4);
  });
});

describe("Landing", () => {
  it("renders tagline and subtitle correctly", () => {
    // Render Landing inside MemoryRouter as it uses useNavigate
    render(
      <MemoryRouter>
        <Landing
          tagline="Planting Optimisation Tool"
          subtitle="Generate your environmental profile!"
          exploreButton="Generate"
        />
      </MemoryRouter>
    );

    // Expect tagline and subtitle to be present
    expect(screen.getByText("Planting Optimisation Tool")).toBeInTheDocument();
    expect(
      screen.getByText("Generate your environmental profile!")
    ).toBeInTheDocument();
  });

  it("renders the explore button with correct label", () => {
    // Render Landing inside MemoryRouter as it uses useNavigate
    render(
      <MemoryRouter>
        <Landing
          tagline="Planting Optimisation Tool"
          subtitle="Generate your environmental profile!"
          exploreButton="Generate"
        />
      </MemoryRouter>
    );

    // Expect explore button to be present with correct label
    expect(
      screen.getByRole("button", { name: "Generate" })
    ).toBeInTheDocument();
  });

  it("navigates to /recommendation when explore button is clicked", async () => {
    const user = userEvent.setup();

    // Render Landing inside MemoryRouter with recommendation route defined
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route
            path="/"
            element={
              <Landing
                tagline="Planting Optimisation Tool"
                subtitle="Generate your environmental profile!"
                exploreButton="Generate"
              />
            }
          />
          <Route
            path="/recommendation"
            element={<div>Recommendation Page</div>}
          />
        </Routes>
      </MemoryRouter>
    );

    // Click explore button and expect navigation to recommendation
    await user.click(screen.getByRole("button", { name: "Generate" }));
    expect(screen.getByText("Recommendation Page")).toBeInTheDocument();
  });
});

describe("NotFoundContent", () => {
  it("renders 404 code and title", () => {
    // Render NotFoundContent inside MemoryRouter as it uses useNavigate
    render(
      <MemoryRouter>
        <NotFoundContent />
      </MemoryRouter>
    );

    // Expect 404 code and page not found title to be present
    expect(screen.getByText("404")).toBeInTheDocument();
    expect(screen.getByText("Page not found")).toBeInTheDocument();
  });

  it("renders description message", () => {
    // Render NotFoundContent inside MemoryRouter as it uses useNavigate
    render(
      <MemoryRouter>
        <NotFoundContent />
      </MemoryRouter>
    );

    // Expect description to be present
    expect(
      screen.getByText(/doesn't exist or has been moved/i)
    ).toBeInTheDocument();
  });

  it("renders 'Back to Home' button", () => {
    // Render NotFoundContent inside MemoryRouter as it uses useNavigate
    render(
      <MemoryRouter>
        <NotFoundContent />
      </MemoryRouter>
    );

    // Expect back to home button to be present
    expect(
      screen.getByRole("button", { name: /back to home/i })
    ).toBeInTheDocument();
  });

  it("navigates to / when Back to Home is clicked", async () => {
    const user = userEvent.setup();

    // Render NotFoundContent inside MemoryRouter with home route defined
    render(
      <MemoryRouter initialEntries={["/404"]}>
        <Routes>
          <Route path="/404" element={<NotFoundContent />} />
          <Route path="/" element={<div>Home Page</div>} />
        </Routes>
      </MemoryRouter>
    );

    // Click back to home button and expect navigation to home
    await user.click(screen.getByRole("button", { name: /back to home/i }));
    expect(screen.getByText("Home Page")).toBeInTheDocument();
  });
});
