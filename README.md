# TRACE Farm Registration API

A FastAPI-based implementation of the TRACE farm data ingestion challenge.

This project simulates part of a compliance-focused agricultural data pipeline where field agents across West Africa submit GPS-anchored farm registration data from mobile devices. The API validates, stores, and safeguards compliance data integrity while handling unreliable field-network conditions and duplicate submissions.

---

# Features

* FastAPI REST API
* Comprehensive request validation
* Custom validation error responses
* Duplicate farmer detection
* UUID-based farm registration IDs
* Compliance-oriented status workflow
* In-memory persistence layer
* Pytest test coverage
* OpenAPI/Swagger documentation
* Data integrity and audit considerations

---

# Tech Stack

* Python 3.12+
* FastAPI
* Pydantic v2
* Pytest
* Uvicorn

---

# Project Structure

```text
.
├── .gitignore
├── python-version
├── README.md
├── debug.py
├── main.py
├── part_c.txt
├── pyproject.toml
├── test_main.py
└── uv.lock
```

---

# API Endpoint

## Register Farm

```http
POST /api/v1/farms/register
```

---

# Request Body

```json
{
  "farmer_name": "John Doe",
  "farmer_id": "NG-1234567890",
  "latitude": 6.5244,
  "longitude": 3.3792,
  "farm_size_hectares": 12.5,
  "commodity": "cocoa",
  "agent_id": "AGENT-001",
  "submitted_at": "2026-05-26T15:02:23.641Z"
}
```

---

# Validation Rules

| Field              | Rules                                       |
| ------------------ | ------------------------------------------- |
| farmer_name        | Required, 2–100 chars                       |
| farmer_id          | Required, format: `NG-XXXXXXXXXX`           |
| latitude           | Between -90 and 90                          |
| longitude          | Between -180 and 180                        |
| farm_size_hectares | Greater than 0 and less than 10000          |
| commodity          | One of: cocoa, cashew, coffee, shea, sesame |
| agent_id           | Non-empty string                            |
| submitted_at       | Valid ISO 8601 datetime                     |

---

# Successful Response

## 201 Created

```json
{
  "farm_id": "550e8400-e29b-41d4-a716-446655440000",
  "farmer_name": "John Doe",
  "farmer_id": "NG-1234567890",
  "latitude": 6.5244,
  "longitude": 3.3792,
  "farm_size_hectares": 12.5,
  "commodity": "cocoa",
  "agent_id": "AGENT-001",
  "submitted_at": "2026-05-26T15:02:23.641Z",
  "passport_status": "PENDING",
  "created_at": "2026-05-26T15:05:00.000Z"
}
```

---

# Validation Error Response

## 422 Unprocessable Entity

```json
{
  "error": "Validation failed",
  "details": [
    {
      "field": "latitude",
      "message": "latitude must be between -90 and 90"
    }
  ]
}
```

---

# Duplicate Submission Handling

## 409 Conflict

```json
{
  "detail": "Farmer with ID NG-1234567890 already exists"
}
```

---

# Running the Project

## 1. Clone Repository

```bash
git clone <repository-url>
cd trace_backend_task
```

---

## 2. Install Dependencies

```bash
uv sync
```

---

## 3. Activate environment

#### Windows
```bash
.venv/source/activate
```

#### Linux
```bash
source venv/source/activate
```

---

## 4. Run Development Server

```bash
# To run Part A.
fastapi dev main.py

# To run Part B
fastapi dev debug.py
```

Server runs at:

```text
http://127.0.0.1:8000
```

---

# API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# Running Tests

```bash
pytest
```

---

# Test Coverage

The project includes tests for:

* Successful registration
* Duplicate farmer detection
* Invalid GPS coordinates
* Invalid commodity values
* Missing required fields
* Validation error formatting

---

# Design Considerations

## Idempotency

The project discusses strategies for making duplicate submissions safe under unstable network conditions using:

* idempotency keys
* atomic writes
* unique constraints
* distributed request coordination

---

## Timestamp Integrity

The implementation distinguishes between:

* client-supplied `submitted_at`
* trusted server-generated timestamps

This prevents compliance and audit issues caused by manipulated or inaccurate device clocks.

---

# Notes

This implementation intentionally uses an in-memory datastore to satisfy the assessment requirement and avoid unnecessary infrastructure setup. In production, this would be replaced with a persistent database and transactional guarantees.

---

# Author

Enemchukwu Chukwuemeka
