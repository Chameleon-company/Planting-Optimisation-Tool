// @vitest-environment jsdom

import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import HomePage from "../pages/HomePage";

describe("HomePage Snapshot", () => {
  it("matches snapshot", () => {
    const { container } = render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>
    );

    expect(container).toMatchSnapshot();
  });
});
