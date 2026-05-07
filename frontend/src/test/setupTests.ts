// Vitest DOM matchers
import "@testing-library/jest-dom/vitest";

//Env variables
import { vi } from "vitest";

vi.stubEnv("VITE_SPACE_ID", "test-space-id");
vi.stubEnv("VITE_ACCESS_TOKEN", "test-access-token");
vi.stubEnv("VITE_API_URL", "http://127.0.0.1:8080");
