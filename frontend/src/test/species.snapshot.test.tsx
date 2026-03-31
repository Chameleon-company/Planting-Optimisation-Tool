// @vitest-environment jsdom

import { describe, it, expect, vi } from "vitest";
import { render } from "@testing-library/react";

// Components to snapshot
import SpeciesGrid from "../components/species/speciesGrid";
import SpeciesModal from "../components/species/speciesModal";

// Minimal species data for consistent snapshots
const mockSpecies = [
  {
    sys: { id: "1" },
    fields: {
      name: "Test Tree",
      description: { content: [] },
    },
  },
];

describe("Snapshot Tests", () => {
  it("matches snapshot for SpeciesGrid with data", () => {
    const { container } = render(
      <SpeciesGrid species={mockSpecies} onCardClick={vi.fn()} />
    );

    // Verifies grid rendering structure
    expect(container).toMatchSnapshot();
  });

  it("matches snapshot for open SpeciesModal", () => {
    const { container } = render(
      <SpeciesModal item={mockSpecies[0]} onClose={vi.fn()} />
    );

    // Ensures modal UI structure remains stable
    expect(container).toMatchSnapshot();
  });

  it("matches snapshot for empty SpeciesModal", () => {
    const { container } = render(
      <SpeciesModal item={null} onClose={vi.fn()} />
    );

    // Edge case: modal with no data
    expect(container).toMatchSnapshot();
  });
});
