// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import { client } from "../src/utils/contentfulClient";

// Mock the Contentful Client without real API calls
vi.mock("../src/utils/contentfulClient", () => ({
  client: {
    getEntries: vi.fn(),
  },
}));

// Mock CSS import to prevent errors
vi.mock("./style.css", () => ({}));

describe("Species Page Logic", () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <main>
        <input id="speciesSearch" type="search" />
        <button id="speciesSearchBtn">Search</button>
        <div id="speciesArticles" class="species-grid"></div>
        <div id="speciesEmpty" hidden>No species match your search.</div>
      </main>
    `;

    vi.clearAllMocks();
    vi.resetModules();
  });

  it("shows empty message when no results are found", async () => {
    // Mock the API to return an empty list
    (client.getEntries as Mock).mockResolvedValue({ items: [] });

    await import("../src/species");

    // Simulate User Input
    const input = document.getElementById("speciesSearch") as HTMLInputElement;
    const btn = document.getElementById(
      "speciesSearchBtn"
    ) as HTMLButtonElement;

    input.value = "NonExistentTree";
    btn.click();

    await new Promise(process.nextTick);

    const emptyMsg = document.getElementById("speciesEmpty");
    expect(emptyMsg?.hidden).toBe(false);
    expect(emptyMsg?.textContent).toContain("No species found");
  });

  it("renders species cards when data is returned", async () => {
    // Mock the API to return one species
    const mockSpecies = {
      items: [
        {
          fields: {
            name: "Eucalyptus alba",
            image: {
              fields: {
                file: { url: "//images.ctfassets.net/eucalyptus.jpg" },
              },
            },
            description: { content: [] },
          },
        },
      ],
    };
    (client.getEntries as Mock).mockResolvedValue(mockSpecies);

    await import("../src/species");

    // Simulate Search
    const input = document.getElementById("speciesSearch") as HTMLInputElement;
    const btn = document.getElementById(
      "speciesSearchBtn"
    ) as HTMLButtonElement;

    input.value = "Eucalyptus alba";
    btn.click();

    await new Promise(process.nextTick);

    const grid = document.getElementById("speciesArticles");
    const cards = grid?.querySelectorAll(".article-card");
    const title = grid?.querySelector(".article-title");

    expect(client.getEntries).toHaveBeenCalledWith(
      expect.objectContaining({ query: "Eucalyptus alba" })
    );
    expect(cards?.length).toBe(1);
    expect(title?.textContent).toBe("Eucalyptus alba");
  });

  it("opens modal when View Details is clicked", async () => {
    (client.getEntries as Mock).mockResolvedValue({
      items: [
        {
          fields: {
            name: "Falcataria falcata",
            description: { content: [] },
          },
        },
      ],
    });

    await import("../src/species");

    // Trigger Search & Render
    const btn = document.getElementById(
      "speciesSearchBtn"
    ) as HTMLButtonElement;
    (document.getElementById("speciesSearch") as HTMLInputElement).value =
      "Falcataria falcata";
    btn.click();
    await new Promise(process.nextTick);

    // Find the rendered "View Details" button and click it
    const viewBtn = document.querySelector(
      ".view-details-btn"
    ) as HTMLButtonElement;
    viewBtn.click();

    // Check if modal was added and made active
    const modal = document.getElementById("speciesModal");
    expect(modal).not.toBeNull();
    expect(modal?.classList.contains("active")).toBe(true);
    expect(modal?.innerHTML).toContain("Falcataria falcata");
  });
});
