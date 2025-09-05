from pydantic import BaseModel
from typing import Any, Dict, Optional

class AgentRequest(BaseModel):
    task: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    status: str
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PropertyDetails(BaseModel):
    location: str
    size_sqft: float
    bedrooms: int
    bathrooms: int
    year_built: Optional[int] = None

class SellerDetails(BaseModel):
    seller_id: str
    name: str
    contact: str
    property: PropertyDetails
