from pydantic import BaseModel, ConfigDict


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
    name: str | None = None
    city: str | None = None
    address: str | None = None
    description: str | None = None
    rating: float | None = None