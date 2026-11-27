# POT Backend API Error Response Contract

**Related issues:** #623 (backend contract), #585 (parent), #622 (frontend implementation), #606 (upcoming user-management API)  
**Status:** Documented from current backend source plus Stuart's posted #606 API contract (23 Nov 2026); pending runtime confirmation of rate-limit payload and team review  
**Scope:** Existing backend error response shapes and frontend integration expectations. Documentation only; no changes to backend behaviour.

## 1. Summary

POT does not currently return a single uniform JSON schema for all errors. Frontend clients should support the shapes actually produced by the backend rather than assuming every failure has a string `detail` field. This particularly affects SlowAPI rate-limit responses, which use the top-level `error` key. In addition, the **new #606 API contract** introduces structured `detail` objects containing `code` and `message`; these are **planned for the #606 backend PRs**, not yet an observed response from the current merged backend.

## 2. Existing error response formats

| Scenario | Status | Response JSON shape | Implementation evidence |
| --- | --- | --- | --- |
| Typical FastAPI `HTTPException`, e.g. invalid credentials / missing resource / forbidden | 400, 401, 403, 404, etc. | `{"detail": "Human-readable error"}` | `backend/src/routers/auth.py`, `backend/src/routers/user.py`, `backend/src/dependencies.py` |
| Request/Pydantic validation | 422 | `{"detail": [{"field": "field_name", "message": "Validation message"}], "errors": [{"field": "field_name", "message": "Validation message"}]}` | Registered handlers in `backend/src/main.py`; password validation assertions in `backend/tests/test_auth.py` |
| Response-model validation | 422 (current handler) | `{"detail": [{"field": "...", "message": "..."}]}` | `ResponseValidationError` handler in `backend/src/main.py` |
| Domain CSV errors | 400 | `{"detail": "Error text"}` | `GlobalWeightsCSVError` / `EpiCSVError` handlers in `backend/src/main.py` |
| Exceeded rate limit (SlowAPI) | 429 | `{"error": "Rate limit exceeded: ..."}` | `backend/src/main.py` registers SlowAPI `_rate_limit_exceeded_handler`; upstream SlowAPI handler emits `error` |
| **Planned #606 errors, not yet merged** | **400, 403, 409, 410** (as specified in #606) | `{"detail":{"code":"request_pending","message":"<safe explanatory message>"}}` | Stuart's [#606 API contract comment](https://github.com/Chameleon-company/Planting-Optimisation-Tool/issues/606#issuecomment-7090965467) |

**Rate-limit verification boundary:** The upstream SlowAPI handler uses `{"error": ...}` for 429, but POT's existing tests (`backend/tests/test_rate_limiting.py`) assert the 429 *status*, not the actual response body. Confirm the payload against the version installed in POT before treating the precise message text as guaranteed. The registered handler is the current configured behaviour; no endpoint-specific override was identified during this review.

### Example: ordinary HTTP exception

```json
{"detail": "Incorrect username or password"}
```

### Example: structured 422 validation

```json
{
  "detail": [{"field": "password", "message": "Validation failed"}],
  "errors": [{"field": "password", "message": "Validation failed"}]
}
```

The example above illustrates the schema and is **not** a verbatim captured live backend response.

### Example: rate limiting (shape from registered SlowAPI handler)

```json
{"error": "Rate limit exceeded: ..."}
```

### Example: planned #606 structured error (contract only)

```json
{
  "detail": {
    "code": "request_pending",
    "message": "<safe explanatory message>"
  }
}
```

The example illustrates the schema, **not a captured runtime response**. Stuart's #606 contract lists `own_request`, `own_credentials_only`, `role_change_separate`, `already_decided`, `request_pending`, `target_changed`, `last_admin`, and `use_deactivate` as possible coded error cases. The user-management frontend under #606 must also handle **202 Accepted as a successful pending-approval response**, rather than treating it as an error; this does not change the generic #622 parsing responsibility.

## 3. Recommended frontend handling for #622

The parser should preserve a meaningful, safe error message in the following order:

1. `detail` if it is a non-empty string (existing FastAPI HTTP exceptions).
2. **`detail.message` if `detail` is an object with a non-empty string `message`** (planned #606 API contract). Preserve `detail.code` separately as a machine-readable discriminator rather than displaying arbitrary objects.
3. `detail` if it is an array: for each item, use `message` (current POT validation handler), or `msg` (FastAPI-compatible fallback). Include `field` when available; join non-empty messages.
4. `errors` if it is an array, with the same `field` / `message` / `msg` handling, when `detail` is unavailable or unhelpful.
5. `error` if it is a non-empty string (**important for HTTP 429**).
6. Top-level `message` if it is a non-empty string and safe to display.
7. Otherwise use a safe generic fallback, e.g. `Request failed (HTTP 429)`, without exposing response internals.

For `429`, preserve the rate-limit text and let the UI explain that the user should retry later. Do not invent a retry duration; use `Retry-After` only if actually present and valid. A future `detail` object without a valid `message` must also fall back safely.

For non-JSON responses, empty bodies, malformed arrays, unexpected object types and network failures, use a generic fallback rather than throwing a second parsing error. Preserve the correct HTTP status and existing field validation behaviour. Avoid echoing raw stack traces, HTML error pages, secrets or untrusted objects directly to users.

**Compatibility note:** existing frontend utilities use inconsistent shapes. In particular, `frontend/src/utils/speciesApi.ts` already handles `detail` arrays with `field`, `message` and `msg`, and top-level `error`; `frontend/src/utils/usersAPI.ts` primarily reads `detail` and expects `msg` in arrays. The client should not assume that all 422 entries use `msg`, since POT's application-wide handler emits `message`.

## 4. Contract checks / suggested test matrix

| Test case | Expected parsing behaviour |
| --- | --- |
| `400 {"detail":"Bad request"}` | Display `Bad request` |
| `401 {"detail":"Incorrect username or password"}` | Preserve meaningful authentication error |
| `403 {"detail":"The user does not have adequate permissions."}` | Preserve meaningful authorisation error |
| `422 {"detail":[{"field":"password","message":"Invalid value"}],"errors":[...]}` | Display formatted field validation; do not show `[object Object]` |
| `422 {"detail":[{"loc":["body","name"],"msg":"Field required"}]}` | Handle `msg` as a compatibility fallback |
| `429 {"error":"Rate limit exceeded: ..."}` | Display rate-limit message; do not reduce it to `API error` |
| **Planned #606:** `409 {"detail":{"code":"request_pending","message":"..."}}` | Display `detail.message` and preserve `detail.code` for error-specific UI handling; do not render `[object Object]` |
| **Planned #606:** `202` with `ApprovalRequestRead` | Treat as **successful pending approval**, not as an error (handled in #606 frontend integration) |
| `400 {"message":"Recognised message"}` | Use message if `detail` and `error` are absent |
| Unparseable/non-JSON/empty response | Use safe status-aware fallback |

These rows are **proposed automated frontend parsing tests**, not claims that tests have already passed. A backend integration test should additionally verify the configured 429 body.

## 5. Outstanding confirmation items

1. **429 payload:** assert both HTTP 429 and the JSON `error` field using the installed SlowAPI version (the existing backend test currently checks status only).
2. **Contract ownership:** confirm that #623 documents the **existing** formats and #622 implements frontend parsing; a backend schema migration/unification is outside these tasks unless separately approved.
3. **Validation format:** should the existing handler's `{field, message}` be maintained as the stable supported format? It currently duplicates the array under `detail` and `errors`.
4. **Response validation:** the current handler exposes validation errors as 422; assess separately whether exposing internal response field names/messages should be reduced for production. Do not silently alter its behaviour as part of #623.
5. **Malformed JSON location:** `RequestValidationError` currently turns numeric `loc` elements into a `field` string; #445 separately tracks improving malformed JSON messages.
6. **#606 rollout:** confirm structured `detail: {code,message}` response tests once the new user-management endpoints are merged. Do **not** assume the shape is already live. Keep #622 compatible with both current and upcoming formats.

## 6. Handoff to frontend

This document is intended as the backend contract reference for **#622**. Frontend implementation can start with the observed formats and the proposed test matrix, and should also support the **documented upcoming #606 shape** so the later user-management integration is not broken. The remaining 429 runtime assertion and policy questions should be tracked during review. No backend code changes or passing-test claims are made by this documentation-only contribution.

## 7. Source files

- [`backend/src/main.py`](../src/main.py)
- [`backend/src/routers/auth.py`](../src/routers/auth.py)
- [`backend/src/routers/user.py`](../src/routers/user.py)
- [`backend/src/dependencies.py`](../src/dependencies.py)
- [`backend/tests/test_auth.py`](../tests/test_auth.py)
- [`backend/tests/test_rate_limiting.py`](../tests/test_rate_limiting.py)
- [`frontend/src/utils/speciesApi.ts`](../../frontend/src/utils/speciesApi.ts)
- [`frontend/src/utils/usersAPI.ts`](../../frontend/src/utils/usersAPI.ts)
- [SlowAPI `_rate_limit_exceeded_handler` upstream source](https://github.com/laurentS/slowapi/blob/master/slowapi/extension.py)
- GitHub issues [#623](https://github.com/Chameleon-company/Planting-Optimisation-Tool/issues/623), [#585](https://github.com/Chameleon-company/Planting-Optimisation-Tool/issues/585), [#622](https://github.com/Chameleon-company/Planting-Optimisation-Tool/issues/622); Stuart's [#606 API contract](https://github.com/Chameleon-company/Planting-Optimisation-Tool/issues/606#issuecomment-7090965467)
