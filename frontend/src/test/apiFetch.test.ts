import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  apiFetch,
  AUTH_UNAUTHORIZED_EVENT,
} from "../utils/apiFetch";

describe("apiFetch", () => {
  const mockFetch = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();

    Object.defineProperty(globalThis, "fetch", {
      value: mockFetch,
      writable: true,
    });
  });

  it("adds the access token as a Bearer Authorization header", async () => {
    localStorage.setItem("access_token", "test-token");

    mockFetch.mockResolvedValueOnce(
      new Response(JSON.stringify({ success: true }), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
        },
      })
    );

    await apiFetch("/test");

    expect(mockFetch).toHaveBeenCalledTimes(1);

    const [, options] = mockFetch.mock.calls[0];

    expect(options.headers.get("Authorization")).toBe("Bearer test-token");
  });

  it("preserves existing request headers", async () => {
    localStorage.setItem("access_token", "test-token");

    mockFetch.mockResolvedValueOnce(
      new Response(null, {
        status: 200,
      })
    );

    await apiFetch("/test", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    });

    const [, options] = mockFetch.mock.calls[0];

    expect(options.method).toBe("POST");
    expect(options.headers.get("Content-Type")).toBe("application/json");
    expect(options.headers.get("Accept")).toBe("application/json");
    expect(options.headers.get("Authorization")).toBe("Bearer test-token");
  });

  it("does not add an Authorization header when no token exists", async () => {
    mockFetch.mockResolvedValueOnce(
      new Response(null, {
        status: 200,
      })
    );

    await apiFetch("/test");

    const [, options] = mockFetch.mock.calls[0];

    expect(options.headers.get("Authorization")).toBeNull();
  });

  it("returns successful responses normally", async () => {
    const response = new Response(JSON.stringify({ message: "success" }), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
      },
    });

    mockFetch.mockResolvedValueOnce(response);

    const result = await apiFetch("/test");

    expect(result).toBe(response);
    expect(result.ok).toBe(true);
  });

  it("dispatches the unauthorized event when the API returns 401", async () => {
    localStorage.setItem("access_token", "expired-token");

    const eventSpy = vi.fn();

    window.addEventListener(AUTH_UNAUTHORIZED_EVENT, eventSpy);

    mockFetch.mockResolvedValueOnce(
      new Response(null, {
        status: 401,
      })
    );

    // Prevent the test from actually navigating.
    const originalLocation = window.location;

    Object.defineProperty(window, "location", {
      configurable: true,
      value: {
        ...originalLocation,
        href: "/",
      },
    });

    await apiFetch("/test");

    expect(eventSpy).toHaveBeenCalledTimes(1);
    expect(window.location.href).toBe("/login");

    window.removeEventListener(AUTH_UNAUTHORIZED_EVENT, eventSpy);
  });

  it("does not dispatch the unauthorized event for non-401 errors", async () => {
    const eventSpy = vi.fn();

    window.addEventListener(AUTH_UNAUTHORIZED_EVENT, eventSpy);

    mockFetch.mockResolvedValueOnce(
      new Response(null, {
        status: 500,
      })
    );

    await apiFetch("/test");

    expect(eventSpy).not.toHaveBeenCalled();

    window.removeEventListener(AUTH_UNAUTHORIZED_EVENT, eventSpy);
  });

});
