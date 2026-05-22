from pydantic import BaseModel
from typing import Optional, List

class PointResJSON(BaseModel):
    pointId: str
    providerName: str
    status: str
    lat: str
    lon: str
