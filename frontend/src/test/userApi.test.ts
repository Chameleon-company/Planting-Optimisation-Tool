// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, Mock } from "vitest";
import {
  listUsers,
  listPending,
  getUser,
  createUser,
  updateUser,
  deleteUser,
  approveUser,
  rejectUser,
} from "@/utils/usersAPI";
import type { UserRead, UserCreate, UserUpdate } from "@/utils/usersAPI";

const TOKEN = "test-token";

const alice: UserRead = {
  id: 1,
  email: "alice@example.com",
  name: "Alice",
  role: "admin",
  is_approved: true,
  requested_role: null,
};

const bob: UserRead = {
  id: 2,
  email: "bob@example.com",
  name: "Bob",
  role: "officer",
  is_approved: false,
  requested_role: "supervisor",
};

function callArgs(index = 0): [string, RequestInit] {
  return (global.fetch as Mock).mock.calls[index] as [string, RequestInit];
}

describe("usersAPI", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  describe("listUsers", () => {
    it("GETs the users collection with default paging and an auth header", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: true,
        json: async () => [alice, bob],
      });

      const result = await listUsers(TOKEN);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/users/?skip=0&limit=100"),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: `Bearer ${TOKEN}`,
            Accept: "application/json",
          }),
        })
      );
      expect(result).toEqual([alice, bob]);
    });
  });

  describe("listPending", () => {
    it("GETs the pending endpoint", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: true,
        json: async () => [bob],
      });

      const result = await listPending(TOKEN);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/users/pending"),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: `Bearer ${TOKEN}`,
          }),
        })
      );
      expect(result).toEqual([bob]);
    });
  });

  describe("getUser", () => {
    it("GETs a single user by id", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: true,
        json: async () => alice,
      });

      const result = await getUser(TOKEN, 1);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/users/1"),
        expect.any(Object)
      );
      expect(result).toEqual(alice);
    });
  });

  describe("createUser", () => {
    it("POSTs the payload with a JSON Content-Type", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: true,
        json: async () => alice,
      });

      const payload: UserCreate = {
        email: "new@example.com",
        name: "New User",
        password: "hunter2",
        role: "officer",
      };

      await createUser(TOKEN, payload);

      const [url, options] = callArgs();
      expect(url).toContain("/users/");
      expect(options.method).toBe("POST");
      expect((options.headers as Record<string, string>)["Content-Type"]).toBe(
        "application/json"
      );
      expect(JSON.parse(options.body as string)).toEqual(payload);
    });
  });

  describe("updateUser", () => {
    it("PUTs to the user id with the changed fields", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ ...alice, name: "Renamed" }),
      });

      const payload: UserUpdate = { name: "Renamed" };
      await updateUser(TOKEN, 1, payload);

      const [url, options] = callArgs();
      expect(url).toContain("/users/1");
      expect(options.method).toBe("PUT");
      expect(JSON.parse(options.body as string)).toEqual(payload);
    });
  });

  describe("deleteUser", () => {
    it("DELETEs the user id and resolves on a 204", async () => {
      (global.fetch as Mock).mockResolvedValue({ ok: true });

      await expect(deleteUser(TOKEN, 2)).resolves.toBeUndefined();

      const [url, options] = callArgs();
      expect(url).toContain("/users/2");
      expect(options.method).toBe("DELETE");
    });

    it("throws on a non-ok response", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: false,
        status: 403,
        json: async () => ({ detail: "Not allowed" }),
      });

      await expect(deleteUser(TOKEN, 2)).rejects.toThrow("Not allowed");
    });
  });

  describe("approveUser", () => {
    it("POSTs the effective role to the approve endpoint", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ ...bob, is_approved: true, role: "supervisor" }),
      });

      await approveUser(TOKEN, 2, "supervisor");

      const [url, options] = callArgs();
      expect(url).toContain("/users/2/approve");
      expect(options.method).toBe("POST");
      expect(JSON.parse(options.body as string)).toEqual({
        role: "supervisor",
      });
    });
  });

  describe("rejectUser", () => {
    it("POSTs to the reject endpoint and resolves void", async () => {
      (global.fetch as Mock).mockResolvedValue({ ok: true });

      await expect(rejectUser(TOKEN, 2)).resolves.toBeUndefined();

      const [url, options] = callArgs();
      expect(url).toContain("/users/2/reject");
      expect(options.method).toBe("POST");
    });
  });

  describe("error extraction", () => {
    it("uses a string detail as the message", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({ detail: "User not found" }),
      });

      await expect(listUsers(TOKEN)).rejects.toThrow("User not found");
    });

    it("joins an array detail into one message", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: false,
        status: 422,
        json: async () => ({
          detail: [{ msg: "Field required" }, { msg: "Invalid email" }],
        }),
      });

      await expect(createUser(TOKEN, {} as UserCreate)).rejects.toThrow(
        "Field required, Invalid email"
      );
    });

    it("falls back to 'Invalid input' for array entries missing msg", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: false,
        status: 422,
        json: async () => ({ detail: [{}, { msg: "Too short" }] }),
      });

      await expect(createUser(TOKEN, {} as UserCreate)).rejects.toThrow(
        "Invalid input, Too short"
      );
    });

    it("uses the fallback message when the body has no detail", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({}),
      });

      await expect(listUsers(TOKEN)).rejects.toThrow(
        "Failed to fetch users (500)"
      );
    });

    it("uses the fallback message when the body is not JSON", async () => {
      (global.fetch as Mock).mockResolvedValue({
        ok: false,
        status: 502,
        json: async () => {
          throw new Error("not json");
        },
      });

      await expect(listUsers(TOKEN)).rejects.toThrow(
        "Failed to fetch users (502)"
      );
    });
  });
});
