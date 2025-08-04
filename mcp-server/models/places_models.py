from pydantic import BaseModel
from typing import List, Dict, Optional, Literal, Any


class Properties(BaseModel):
    address_line1: str
    address_line2: str
    categories: List[str]
    city: str
    country: str
    country_code: str
    datasource: Optional[Any]
    details: List[str]
    district: str
    formatted: str
    iso3166_2: str
    lat: float
    lon: float
    name: Optional[str] = None
    name_international: Optional[Dict[str, str]] = None
    place_id: str
    suburb: str
    street: Optional[str] = None
    postcode: Optional[str] = None
    distance: Optional[float] = None
    historic: Optional[Any] = None
    artwork: Optional[Any] = None
    wiki_and_media: Optional[Any] = None
    neighbourhood: Optional[str] = None

class PlaceFeature(BaseModel):
    geometry: Optional[Any]
    properties: Properties
    type: Literal["Feature"]

class Places(BaseModel):
    features: List[PlaceFeature]
