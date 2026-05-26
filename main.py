import re
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

app = FastAPI()

# In-memory database
DB = {}


ALLOWED_COMMODITIES = [
    "cocoa",
    "cashew",
    "coffee",
    "shea",
    "sesame",
]


class FarmerRequest(BaseModel):
    farmer_name: str = Field(..., min_length=2, max_length=100)
    farmer_id: str
    latitude: float
    longitude: float
    farm_size_hectares: float
    commodity: Literal["cocoa", "cashew", "coffee", "shea", "sesame"]
    agent_id: str
    submitted_at: datetime

    @field_validator("farmer_id")
    @classmethod
    def validate_farmer_id(cls, value):
        pattern = r"^NG-\d{10}$"

        if not re.match(pattern, value):
            raise ValueError("farmer_id must follow format NG-XXXXXXXXXX")

        return value

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, value):
        if not -90 <= value <= 90:
            raise ValueError("latitude must be between -90 and 90")
        return value

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, value):
        if not -180 <= value <= 180:
            raise ValueError("longitude must be between -180 and 180")
        return value

    @field_validator("farm_size_hectares")
    @classmethod
    def validate_farm_size(cls, value):
        if not 0 < value < 10000:
            raise ValueError(
                "farm_size_hectares must be greater than 0 and less than 10000"
            )
        return value

    @field_validator("agent_id")
    @classmethod
    def validate_agent_id(cls, value):
        if not value.strip():
            raise ValueError("agent_id cannot be empty")

        return value


class FarmerResponse(FarmerRequest):
    farm_id: UUID
    passport_status: str
    created_at: datetime


class ValidationDetail(BaseModel):
    field: str
    message: str


class CustomValidationError(BaseModel):
    error: str
    details: list[ValidationDetail]


class HTTPExceptionSchema(BaseModel):
    detail: str


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = []

    for error in exc.errors():
        field = error["loc"][-1]
        message = error["msg"]

        errors.append({"field": field, "message": message})

    return JSONResponse(
        status_code=422, content={"error": "Validation failed", "details": errors}
    )


@app.post(
    "/api/v1/farms/register",
    status_code=status.HTTP_201_CREATED,
    response_model=FarmerResponse,
    responses={
        422: {
            "model": CustomValidationError,
            "description": "Validation Error",
        },
        409: {
            "model": HTTPExceptionSchema,
            "description": "HTTP Exception Conflict",
        },
    },
)
def register_farm(data: FarmerRequest):

    # Duplicate check BEFORE saving
    if data.farmer_id in DB:
        raise HTTPException(
            status_code=409, detail=f"Farmer with ID {data.farmer_id} already exists"
        )

    farm_record = FarmerResponse(
        farm_id=uuid4(),
        passport_status="PENDING",
        created_at=datetime.now(timezone.utc),
        **data.model_dump(),
    )

    # Store using farmer_id as unique key
    DB[data.farmer_id] = farm_record.model_dump()

    return farm_record
