from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class HotelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    city: str
    address: str
    description: str
    rating: float

class HotelCreate(HotelRead):
    pass

class HotelUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str | None = None
    city: str | None = None
    address: str | None = None
    description: str | None = None
    rating: float | None = None

class RoomBase(BaseModel):
    capacity: int
    base_price: Decimal

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    capacity: int | None = None
    base_price: Decimal | None = None

class RoomRead(RoomBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hotel_id: int