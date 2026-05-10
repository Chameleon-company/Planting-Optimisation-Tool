# Bulk Sapling Batch Estimation Workflow

## Overview

This document describes the currently implemented backend workflow for batch sapling estimation.

The workflow allows authenticated requests to run sapling estimation across farms associated with the authenticated user through the batch estimation API endpoint.

This implementation is defined across:

- `backend/src/routers/batch_estimation.py`
- `backend/src/schemas/batch_estimation.py`
- `backend/src/services/batch_estimation.py`

## Scope

Frontend/UI integration described in US-047 is not currently implemented in the application.

This document describes the backend/API processing workflow currently implemented in the codebase.

---

## Workflow Diagram

```text
Client Request
      ↓
batch_estimation router
      ↓
SaplingBatchEstimationService.run_batch_estimation()
      ↓
farm_service.list_farms_by_user()
      ↓
Cache lookup
      ↓
SaplingEstimationService.run_estimation()
      ↓
Batch response returned
```

---

# 1. Batch Estimation Router

File:

```text
backend/src/routers/batch_estimation.py
```

Endpoint:

```http
POST /sapling_estimation/batch_calculate
```

The endpoint uses the following dependencies:

- `get_db_session`
- `require_role(Role.OFFICER)`
- `SaplingBatchEstimationService.run_batch_estimation()`

Rate limiting is applied using:

```python
@limiter.limit("10/minute", key_func=get_user_id)
```

The authenticated user ID is passed into the batch estimation service using:

```python
current_user.id
```

---

# 2. Request Schema

File:

```text
backend/src/schemas/batch_estimation.py
```

Request model:

```python
SaplingBatchEstimationRequest
```

Example request:

```http
POST /sapling_estimation/batch_calculate
Authorization: Bearer <JWT>
Content-Type: application/json
```

Example request body:

```json
{
  "spacing_x": 10,
  "spacing_y": 10,
  "max_slope": 15
}
```

Request fields:

- `spacing_x`
- `spacing_y`
- `max_slope`

---

# 3. Batch Estimation Service

File:

```text
backend/src/services/batch_estimation.py
```

Main service function:

```python
SaplingBatchEstimationService.run_batch_estimation()
```

The batch estimation service retrieves farms associated with the authenticated user using:

```python
farm_service.list_farms_by_user(db, user_id)
```

If no farms are found, the service returns:

```json
{
  "status": "success",
  "farm_count": 0,
  "results": []
}
```

The service processes farms sequentially using:

```python
for farm in farms:
```

For each farm:

1. A cache key is generated:

```python
sapling:{farm.id}:{spacing_x}:{spacing_y}:{max_slope}
```

2. Cached estimation data is checked using:

```python
cache.get(cache_key)
```

3. If cached data is not available, the service runs:

```python
SaplingEstimationService().run_estimation()
```

4. Successful estimation results are stored using:

```python
cache.set(cache_key, json.dumps(data))
```

The batch service appends the following fields for each farm result:

- `status`
- `farm_id`
- `pre_slope_count`
- `aligned_count`
- `optimal_angle`
- `rotation_average`
- `rotation_std_dev`

---

# 4. Response Schema

File:

```text
backend/src/schemas/batch_estimation.py
```

Response model:

```python
SaplingBatchEstimationResponse
```

The response contains:

- `status`
- `farm_count`
- `results`

Each result item contains:

- `status`
- `farm_id`
- `pre_slope_count`
- `aligned_count`
- `optimal_angle`
- `rotation_average`
- `rotation_std_dev`

Example response:

```json
{
  "status": "success",
  "farm_count": 2,
  "results": [
    {
      "farm_id": 1,
      "status": "success",
      "pre_slope_count": 100,
      "aligned_count": 80,
      "optimal_angle": 10,
      "rotation_average": 5.0,
      "rotation_std_dev": 1.0
    }
  ]
}
```

---

# 5. Cache Behaviour

The batch estimation service checks for cached estimation results before running sapling estimation processing.

Cache keys are generated using:

```python
sapling:{farm.id}:{spacing_x}:{spacing_y}:{max_slope}
```

If cached data exists, the cached estimation result is returned.

If cached data does not exist, the batch service runs:

```python
SaplingEstimationService().run_estimation()
```

Estimation results are written to cache when the returned status is not `"failed"`.

---

# 6. Test Coverage

The implementation includes tests for:

- router request handling
- batch estimation service execution
- cache hit behaviour
- cache miss behaviour

Test files:

```text
backend/tests/test_batch_router.py
backend/tests/test_batch_service.py
```

The tests verify:

- authenticated requests
- batch estimation response structure
- cache usage
- service execution count
- multi-farm batch estimation behaviour

---

# End-to-End Processing Flow

```text
Client sends POST request
        ↓
batch_estimation router receives request
        ↓
Role validation using require_role(Role.OFFICER)
        ↓
SaplingBatchEstimationService.run_batch_estimation()
        ↓
farm_service.list_farms_by_user()
        ↓
Cache lookup for each farm
        ↓
SaplingEstimationService.run_estimation()
        ↓
Batch results returned
```