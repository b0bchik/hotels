from pydantic import BaseModel, ConfigDict
class HotelCreate(BaseModel):
    title: str
    description: str
    rating: float

class HotelRead(HotelCreate):
    id: str
    model_config = ConfigDict(from_attributes=True)

class HotelUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str | None = None
    city: str | None = None
    address: str | None = None
    description: str | None = None
    rating: float | None = None

class RoomCreate(BaseModel):
    title: str
    description: str
    price: float

class RoomRead(RoomCreate):
    id: str
    hotel_id: str
    model_config = ConfigDict(from_attributes=True)

class RoomUpdate(BaseModel):
    capacity: int | None = None
    base_price: Decimal | None = None
