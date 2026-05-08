# Bulk Sapling Calculation Workflow

## Overview

This document explains the end-to-end workflow for the bulk sapling calculation feature.

The workflow allows Managers or Farmers to calculate sapling estimates for all farms linked to their account using a single UI action without requiring spreadsheet uploads or manual farm selection.

The workflow spans multiple layers of the application:

- Frontend UI
- API Layer
- Backend Services
- GIS Batch Processing
- Results Rendering

---

## Workflow Diagram

```text
Frontend UI
     ↓
Bulk Estimate API
     ↓
Backend Service
     ↓
GIS Batch Processor
     ↓
Unified Response Payload
     ↓
Frontend Results Table
```

---

# 1. Frontend UI Trigger

The frontend provides a "Run Portfolio Calculation" button that allows the user to start bulk sapling calculations across all owned farms.

When the button is clicked:

1. A loading spinner is displayed
2. A POST request is sent to the backend API
3. The user's authentication token is attached automatically
4. The UI waits for the calculation results
5. Returned results are rendered in a sortable table

Example request:

```http
POST /api/saplings/bulk-estimate
Authorization: Bearer <JWT>
```


The backend determines ownership exclusively using the authenticated session token.

---

# 2. API Layer

The backend exposes a secure endpoint for bulk sapling calculations.

Endpoint:

```http
POST /api/saplings/bulk-estimate
```

Responsibilities of the API layer:

- Validate authentication token
- Extract authenticated user information
- Forward processing to backend services
- Return unified batch results to the frontend

Security is enforced server-side using the authenticated session.

The system must NEVER accept or process farm IDs from the frontend request body.

All farm selection and ownership validation must be derived exclusively from the authenticated user token/session.

---

# 3. Backend Service

The backend service retrieves all farms associated with the authenticated user.

Example backend process:

1. Extract authenticated user ID
2. Query database for owned farms
3. Validate farm ownership
4. Build validated farm list
5. Pass farm IDs to GIS batch processing
6. Aggregate GIS results
7. Return unified response payload

This ensures users can only process farms they are authorized to access.

---

# 4. GIS Batch Processing

The GIS processing layer performs sapling estimation calculations for all validated farms.

Responsibilities include:

- Area analysis
- Vegetation calculations
- Sapling estimation logic
- Batch processing across multiple farms


The GIS service returns a unified dataset containing sapling estimates for each farm.

Failures for individual farms do not block processing for the remaining farms in the batch.

---

# 5. Unified Response Payload

The backend aggregates all GIS calculation results into a single response payload.

Example response:

```json
{
  "results": [
    {
      "farmId": "farm-101",
      "recommendedSaplings": 1240,
      "status": "SUCCESS"
    }
  ]
}
```

The unified payload is returned directly to the frontend bulk calculator UI.

---

# 6. Frontend Results Rendering

The frontend displays the returned calculation results in a clear and sortable table.

The results table supports sorting by:

- Farm Name
- Recommended Saplings
- Status

The UI also handles:

- Loading states
- Empty states
- API error messages
- Partial batch failures

Example empty state:

```text
No farms found for this account.
```

---

# End-to-End Sequence

```text
User clicks "Run Portfolio Calculation"
        ↓
Frontend sends POST request
        ↓
Backend validates JWT token
        ↓
Backend retrieves owned farms
        ↓
Validated farm list sent to GIS batch processor
        ↓
GIS calculates sapling estimates
        ↓
Backend aggregates results
        ↓
Unified response returned to frontend
        ↓
UI renders sortable results table
```

---

# Summary

The bulk sapling workflow provides a secure and scalable way to calculate sapling estimates across all farms owned by an authenticated user.

The workflow connects:

- Angular frontend UI
- Secure backend API
- Backend services
- GIS batch processing
- Unified results rendering
