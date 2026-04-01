// @vitest-environment jsdom
import { it, expect, describe, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import UserEvent from "@testing-library/user-event";

import { Species } from "../utils/contentfulClient";
import SpeciesGrid from "../components/species/speciesGrid";
import SpeciesModal from "../components/species/speciesModal";
import SpeciesSearch from "../components/species/speciesSearch";
import SpeciesCard from "@/components/species/speciesCard";
import SpeciesHeader from "@/components/species/speciesHeader";

// Helpers
// Create mock item template from Contentful species base
const mockSpeciesItem = (name: string, id: string): Species => ({
  sys: { id },
  fields: {
    name,
    scientificName: name,
    description: { content: [] },
    image: {
      fields: {
        file: { url: "//image.fakeasset.net/test.jpg" },
      },
    },
  },
});

// SpeciesGrid
describe("SpeciesGrid", () => {
  it("should show empty message when no species are returned", () => {
    // Render SpeciesGrid with no cards, and mock onCardClick function
    render(<SpeciesGrid species={[]} onCardClick={vi.fn()} />);

    // Expect 'no species found matching your criteria' to be within the page HTML
    expect(
      screen.getByText(/no species found matching your criteria/i)
    ).toBeInTheDocument();
  });

  it("should render a card for each species returned", () => {
    // Create mock species array
    const species = [
      mockSpeciesItem("Eucalyptus alba", "1"),
      mockSpeciesItem("Falcataria falcata", "2"),
    ];

    // Render mock species array with mock onCardClick function
    render(<SpeciesGrid species={species} onCardClick={vi.fn()} />);

    // Collate all .article-cards in HTML to const cards
    const cards = document.querySelectorAll(".article-card");
    // Expect cards length to match mock species array, and for mock species name to be in document
    expect(cards.length).toBe(2);
    expect(screen.getByText("Eucalyptus alba")).toBeInTheDocument();
    expect(screen.getByText("Falcataria falcata")).toBeInTheDocument();
  });

  it("should call onCardClick with the correct species when View Details is clicked", async () => {
    // Create fake user, species array and onCardClick function
    const user = UserEvent.setup();
    const onCardClick = vi.fn();
    const item = mockSpeciesItem("Eucalyptus alba", "1");

    render(<SpeciesGrid species={[item]} onCardClick={onCardClick} />);

    // Wait for fake user to click 'view details' button
    await user.click(screen.getByRole("button", { name: /view details/i }));

    // Expect fake onCardClick function to have been called with mock species array
    expect(onCardClick).toHaveBeenCalledWith(item);
  });
});

// SpeciesSearch
describe("SpeciesSearch", () => {
  it("should call onSearch with the input value when Search is clicked", async () => {
    // Create fake user and onSearch as mock function
    const user = UserEvent.setup();
    const onSearch = vi.fn();

    // Render SpeciesSearch
    render(<SpeciesSearch onSearch={onSearch} isLoading={false} />);

    // Await fake user to type "Eucalyptus alba" into the search box, and press search button
    await user.type(screen.getByRole("textbox"), "Eucalyptus alba");
    await user.click(screen.getByRole("button", { name: /search/i }));

    // Expect onSearch function to have been called with searched for item when button is clicked
    expect(onSearch).toHaveBeenCalledWith("Eucalyptus alba");
  });

  it("should call onSearch when Enter is pressed", async () => {
    // Create fake user and onSearch as mock function
    const user = UserEvent.setup();
    const onSearch = vi.fn();

    // Render SpeciesSearch
    render(<SpeciesSearch onSearch={onSearch} isLoading={false} />);

    // Await fake user to type "Eucalyptus alba" into the search box, and type Enter
    await user.type(screen.getByRole("textbox"), "Falcataria falcata{Enter}");

    // Expect onSearch function to have been called with searched for item when Enter is pressed
    expect(onSearch).toHaveBeenCalledWith("Falcataria falcata");
  });

  it("should not call onSearch when input is empty or whitespace", async () => {
    // Create fake user and onSearch as mock function
    const user = UserEvent.setup();
    const onSearch = vi.fn();

    // Render SpeciesSearch
    render(<SpeciesSearch onSearch={onSearch} isLoading={false} />);

    // Await fake user to click search button while textbox is empty
    await user.click(screen.getByRole("button", { name: /search/i }));

    // Expect onSearch to have not been called when no parameter is handed to Contentful
    expect(onSearch).not.toHaveBeenCalled();
  });

  it("should show loading indicator while search is in progress", () => {
    render(<SpeciesSearch onSearch={vi.fn()} isLoading={true} />);

    expect(screen.getByText("...")).toBeInTheDocument();
  });
});

// SpeciesModal
describe("SpeciesModal", () => {
  it("should render nothing when item is null", () => {
    // When SpeciesModal is rendered with null item
    const { container } = render(
      <SpeciesModal item={null} onClose={vi.fn()} />
    );

    // The container should remain null as well
    expect(container.firstChild).toBeNull();
  });

  it("should render the species name and is active when an item is provided", () => {
    // Create fake SpeciesItem and hand it to rendered SpeciesModal
    const item = mockSpeciesItem("Falcataria falcata", "2");

    render(<SpeciesModal item={item} onClose={vi.fn()} />);

    // Set constant modal to include all HTML within .side-modal
    const modal = document.querySelector(".side-modal");
    // Expect modal to exist, and class is set to active
    expect(modal).toBeInTheDocument();
    expect(modal).toHaveClass("active");
    // Expect modal to contain heading, of mock species item, and its ID
    expect(
      screen.getByRole("heading", { name: "Falcataria falcata", level: 2 })
    ).toBeInTheDocument();
  });

  it("should call onClose when the close button is clicked", async () => {
    // Create fake user, mock onClose function, and mock species item
    const user = UserEvent.setup();
    const onClose = vi.fn();
    const item = mockSpeciesItem("Eucalyptus alba", "1");

    render(<SpeciesModal item={item} onClose={onClose} />);

    // Await fake user to click button x, or the close button
    await user.click(screen.getByRole("button", { name: /×/i }));

    // Expect onClose function to have been called by user click
    expect(onClose).toHaveBeenCalled();
  });

  it("should call onClose when the overlay is clicked", async () => {
    // Create fake user, mock onClose function, and mock species item
    const user = UserEvent.setup();
    const onClose = vi.fn();
    const item = mockSpeciesItem("Eucalyptus alba", "1");

    render(<SpeciesModal item={item} onClose={onClose} />);

    // Await fake user to click the left, unrendered modal side of the screen
    await user.click(document.querySelector(".modal-overlay")!);

    // Expect onClose to have been called by that click
    expect(onClose).toHaveBeenCalled();
  });

  it("should render the species image when a url is provided", () => {
    // Create mock species item
    const item = mockSpeciesItem("Eucalyptus alba", "1");

    render(<SpeciesModal item={item} onClose={vi.fn()} />);

    // Create const img that is from the HTML labelled 'img'
    const img = screen.getByRole("img");
    // Expect img to have link to fake image
    expect(img).toHaveAttribute("src", "https://image.fakeasset.net/test.jpg");
  });

  it("should render rich text description content", () => {
    // Create mock species item that contains description matching w/ Contentful Util
    const item: Species = {
      sys: { id: "1" },
      fields: {
        name: "Eucalyptus alba",
        description: {
          content: [
            {
              nodeType: "paragraph",
              content: [{ nodeType: "text", value: "A tall native tree." }],
            },
          ],
        },
      },
    };

    // When SpeciesModal is rendered
    render(<SpeciesModal item={item} onClose={vi.fn()} />);

    // Expect screen to display text within the description of the mock species item
    expect(screen.getByText("A tall native tree.")).toBeInTheDocument();
  });
});

// SpeciesCard
describe("SpeciesCard", () => {
  it("should render the species name", () => {
    // Render SpeciesCard with mock item and onClick function
    const item = mockSpeciesItem("Eucalyptus alba", "1");
    render(<SpeciesCard item={item} onClick={vi.fn()} />);

    // Expect species name to be present
    expect(screen.getByText("Eucalyptus alba")).toBeInTheDocument();
  });

  it("should render the species image with correct src", () => {
    // Render SpeciesCard with mock item that has an image
    const item = mockSpeciesItem("Eucalyptus alba", "1");
    render(<SpeciesCard item={item} onClick={vi.fn()} />);

    // Expect image to have the correct src built from the url
    const img = screen.getByRole("img");
    expect(img).toHaveAttribute("src", "https://image.fakeasset.net/test.jpg");
  });

  it("should render a fallback image when no image is provided", () => {
    // Render SpeciesCard with mock item that has no image
    const item: Species = {
      sys: { id: "2" },
      fields: {
        name: "Unknown Tree",
        description: { content: [] },
        // image intentionally omitted
      },
    };
    render(<SpeciesCard item={item} onClick={vi.fn()} />);

    // Expect fallback placeholder image to be used
    const img = screen.getByRole("img");
    expect(img).toHaveAttribute(
      "src",
      "https://placehold.co/600x400?text=No+Image"
    );
  });

  it("should render the View Details button", () => {
    // Render SpeciesCard with mock item and onClick function
    const item = mockSpeciesItem("Eucalyptus alba", "1");
    render(<SpeciesCard item={item} onClick={vi.fn()} />);

    // Expect View Details button to be present
    expect(
      screen.getByRole("button", { name: /view details/i })
    ).toBeInTheDocument();
  });

  it("should call onClick when View Details button is clicked", async () => {
    // Create fake user and mock onClick function
    const user = UserEvent.setup();
    const onClick = vi.fn();
    const item = mockSpeciesItem("Eucalyptus alba", "1");

    render(<SpeciesCard item={item} onClick={onClick} />);

    // Await fake user to click View Details button
    await user.click(screen.getByRole("button", { name: /view details/i }));

    // Expect onClick to have been called
    expect(onClick).toHaveBeenCalled();
  });
});

// SpeciesHeader
describe("SpeciesHeader", () => {
  it("should render the Species Information heading", () => {
    // Render SpeciesHeader component
    render(<SpeciesHeader />);

    // Expect main heading to be present
    expect(screen.getByText("Species Information")).toBeInTheDocument();
  });

  it("should render the subtitle text", () => {
    // Render SpeciesHeader component
    render(<SpeciesHeader />);

    // Expect subtitle to be present
    expect(screen.getByText("Understanding Your Species")).toBeInTheDocument();
  });
});
