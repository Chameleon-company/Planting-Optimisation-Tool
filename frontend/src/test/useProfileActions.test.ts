// @vitest-environment jsdom
import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useProfileActions } from "@/hooks/useProfileActions";

const { mockGetAccessToken } = vi.hoisted(() => ({
  mockGetAccessToken: vi.fn(),
}));

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: () => ({
    getAccessToken: mockGetAccessToken,
  }),
}));

const fetchMock = vi.fn();

function createResponse(
  ok: boolean,
  status: number,
  body?: unknown,
  rejectJson = false
): Response {
  return {
    ok,
    status,
    json: rejectJson
      ? vi.fn().mockRejectedValue(new Error("Invalid JSON"))
      : vi.fn().mockResolvedValue(body),
  } as unknown as Response;
}

describe("useProfileActions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetAccessToken.mockReturnValue("test-token");
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("regenerates a profile successfully", async () => {
    const regeneratedProfile = {
      id: 42,
      status: "success",
      rainfall_mm: 1500,
      temperature_celsius: 24,
      elevation_m: 300,
      ph: 6.5,
      slope: 4.5,
      soil_texture: "clay",
    };

    fetchMock.mockResolvedValue(createResponse(true, 200, regeneratedProfile));

    const { result } = renderHook(() => useProfileActions());

    let returnedProfile: unknown;

    await act(async () => {
      returnedProfile = await result.current.regenerateProfile(42);
    });

    expect(returnedProfile).toEqual(regeneratedProfile);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/profile/42/regenerate"),
      expect.objectContaining({
        method: "POST",
        headers: {
          Authorization: "Bearer test-token",
          Accept: "application/json",
        },
      })
    );

    expect(result.current.isRegenerating).toBe(false);
    expect(result.current.actionError).toBeNull();
    expect(result.current.actionMessage).toBe(
      "Environmental profile regenerated successfully."
    );
  });

  it("shows the regenerating state while the request is pending", async () => {
    let resolveFetch: ((response: Response) => void) | undefined;

    fetchMock.mockImplementation(
      () =>
        new Promise<Response>(resolve => {
          resolveFetch = resolve;
        })
    );

    const { result } = renderHook(() => useProfileActions());

    let pendingRequest: Promise<unknown>;

    act(() => {
      pendingRequest = result.current.regenerateProfile(42);
    });

    await waitFor(() => {
      expect(result.current.isRegenerating).toBe(true);
    });

    await act(async () => {
      resolveFetch?.(
        createResponse(true, 200, {
          id: 42,
          status: "success",
        })
      );

      await pendingRequest;
    });

    expect(result.current.isRegenerating).toBe(false);
  });

  it("uses the backend detail when regeneration fails", async () => {
    fetchMock.mockResolvedValue(
      createResponse(false, 403, {
        detail: "The user does not have adequate permissions.",
      })
    );

    const { result } = renderHook(() => useProfileActions());

    await act(async () => {
      await expect(result.current.regenerateProfile(42)).rejects.toThrow(
        "The user does not have adequate permissions."
      );
    });

    expect(result.current.actionError).toBe(
      "The user does not have adequate permissions."
    );
    expect(result.current.actionMessage).toBeNull();
    expect(result.current.isRegenerating).toBe(false);
  });

  it("uses the response status when the error response is not JSON", async () => {
    fetchMock.mockResolvedValue(createResponse(false, 503, undefined, true));

    const { result } = renderHook(() => useProfileActions());

    await act(async () => {
      await expect(result.current.regenerateProfile(42)).rejects.toThrow(
        "Request failed (503)"
      );
    });

    expect(result.current.actionError).toBe("Request failed (503)");
  });

  it("uses the fallback error for a non-Error rejection", async () => {
    fetchMock.mockRejectedValue("network failure");

    const { result } = renderHook(() => useProfileActions());

    await act(async () => {
      await expect(result.current.regenerateProfile(42)).rejects.toThrow(
        "Failed to regenerate the environmental profile."
      );
    });

    expect(result.current.actionError).toBe(
      "Failed to regenerate the environmental profile."
    );
    expect(result.current.isRegenerating).toBe(false);
  });

  it("rejects regeneration when no access token exists", async () => {
    mockGetAccessToken.mockReturnValue(null);

    const { result } = renderHook(() => useProfileActions());

    await act(async () => {
      await expect(result.current.regenerateProfile(42)).rejects.toThrow(
        "You must be logged in."
      );
    });

    expect(fetchMock).not.toHaveBeenCalled();
    expect(result.current.actionError).toBe("You must be logged in.");
  });

  it("clears success and error feedback", async () => {
    fetchMock.mockResolvedValue(
      createResponse(true, 200, {
        id: 42,
        status: "success",
      })
    );

    const { result } = renderHook(() => useProfileActions());

    await act(async () => {
      await result.current.regenerateProfile(42);
    });

    expect(result.current.actionMessage).not.toBeNull();

    act(() => {
      result.current.clearActionFeedback();
    });

    expect(result.current.actionMessage).toBeNull();
    expect(result.current.actionError).toBeNull();
  });
});
