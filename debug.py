"""
ORIGINAL DEPRECATED CODE

farmers = {}

class StatusUpdate(BaseModel):
    farmer_id: str
    status: str

@app.put("/farmers/status")
    def update_status(update: StatusUpdate):
    farmer = farmers[update.farmer_id]
    farmer["status"] = update.status
    farmers[update.farmer_id] = farmer
    return {"message": "Status updated"}
"""

from typing import Literal

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

farmers = {
    "NG-1234567890": {"status": "PENDING"}
}  # Sample data to demonstrate the KeyError and status update

ALLOWED_TRANSITIONS = {
    "PENDING": ["VERIFIED", "FLAGGED"],
    "VERIFIED": [],
    "FLAGGED": [],
}


class StatusUpdate(BaseModel):
    farmer_id: str
    status: Literal["PENDING", "VERIFIED", "FLAGGED"]


class StatusUpdateResponse(BaseModel):
    message: str


class HttpExceptionSchema(BaseModel):
    detail: str


@app.put(
    "/farmers/status",
    response_model=StatusUpdateResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "model": HttpExceptionSchema,
            "description": "Http Exception",
        },
        400: {
            "model": HttpExceptionSchema,
            "description": "Http Exception",
        },
    },
)
def update_status(update: StatusUpdate):
    if update.farmer_id not in farmers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Farmer Id not found."
        )

    farmer = farmers[update.farmer_id]

    current_status = farmer["status"]

    if update.status not in ALLOWED_TRANSITIONS[current_status]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {current_status} to {update.status}",
        )

    farmer["status"] = update.status
    farmers[update.farmer_id] = farmer
    return StatusUpdateResponse(message="Status updated")


"""
1. KeyError: This is an error that is caused by try to get a non-existing key in a dictionary. This bug is due to non conditional/clause check, and is an important (data clause) standard to implement in systems that the existing data cannot be assured before an action or transaction is performed. The fix will to check is the request key exists first, and if not return a friendly error message.

2. Arbitary status state: The status field accepts any string. In compliance systems status values are usually regulated workflow states, e.g PENDING, VERIFIED, etc. The fix is to use an Enum or Literal type to restrict the status field to only accept valid states.

3. Lack of response model and status code: The endpoint does not specify a response model or status code, which can lead to inconsistent API responses and make it harder for clients to understand the expected output. The fix is to define a response model and use appropriate status codes for success and error cases.

4. No Protection Against Invalid State Transitions: The API allows any status to overwrite any other status, e.g: VERIFIED → PENDING → FLAGGED → VERIFIED with no business rules. This matters because compliance systems usually require immutable audit flows, approval chains, and restricted transitions, i.e, once a farmer is VERIFIED,
they may require re-review before becoming FLAGGED, or a FLAGGED farmer may require supervisor approval before VERIFIED. Without these rules data can be tampered with, fraud becomes easier, etc. The Fix is to define a Tree like structures that dictates transition flow, and then they can vary among users, admins, etc.
"""
