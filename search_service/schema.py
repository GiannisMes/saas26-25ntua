from pydantic import BaseModel
from typing import Optional, List

class SearchReqJSON(BaseModel):
    area: str  # search area

class PointResJSON(BaseModel):
    pointId: str
    providerName: str
    status: str
    lat: str
    lon: str
