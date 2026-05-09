# Bulk Sapling Calculation Workflow

## Overview

This document explains the backend workflow for the bulk sapling estimation process.

The workflow describes how authenticated users can request batch sapling estimation processing through the bulk estimation API endpoint.

The workflow spans multiple layers of the application:

- API Layer
- Backend Services
- GIS Batch Processing


---

## Workflow Diagram

```text
API Client
     ↓
Bulk Estimate API
     ↓
Backend Service
     ↓
GIS Batch Processor
     ↓
Unified Response Payload
```

---


# 1. API Layer

The backend exposes a secure endpoint for bulk sapling calculations.

Endpoint:

```http
POST /api/saplings/bulk-estimate
```

Example request:

```http
POST /api/saplings/bulk-estimate
Authorization: Bearer <JWT>
Content-Type: application/json
```

Example request body:

```json
{}
```

## Authorization

The endpoint requires an authenticated user session.

Supported roles include:

- admin
- supervisor
- officer

Responsibilities of the API layer:

- Validate authentication token
- Extract authenticated user information
- Forward processing to backend services
- Return unified batch results to the requesting client

Security is enforced server-side using the authenticated session.

The system must NEVER accept or process farm IDs provided by the requesting client.

All farm selection and ownership validation must be derived exclusively from the authenticated user token/session.

---

# 2. Backend Service

The backend service retrieves all farms associated with the authenticated user.

The workflow coordinates user farm retrieval, batch estimation processing, GIS execution, and response aggregation services.

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

# 3. GIS Batch Processing

The GIS processing layer performs sapling estimation calculations for all validated farms.

Responsibilities include:

- Area analysis
- Vegetation calculations
- Sapling estimation logic
- Batch processing across multiple farms


The GIS processor performs calculations independently for each farm in the batch request.

Batch processing allows multiple farm estimations to be executed within a single request while ensuring failures for one farm do not block processing for remaining farms.

The GIS service returns a unified dataset containing sapling estimates for each farm.

Failures for individual farms do not block processing for the remaining farms in the batch.

---

# 4. Unified Response Payload

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

Possible status values include:

- SUCCESS — estimation completed successfully
- FAILURE — estimation failed for the specified farm

The unified payload is returned to the requesting API client.

---

# 5. Error Handling

Possible error responses include:

- 401 Unauthorized — missing or invalid authentication token
- 403 Forbidden — unauthorized farm access
- 500 Internal Server Error — processing failure during estimation

Failures for individual farms do not stop processing for remaining farms in the batch.

---


# End-to-End Sequence

```text
Client sends POST request
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
Unified response returned to client
```

---

# Summary

The bulk sapling workflow provides a secure and scalable way to calculate sapling estimates across all farms associated with an authenticated user.

The workflow connects:

- Secure backend API
- Backend services
- GIS batch processing
- Unified response generation
