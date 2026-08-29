from pydantic import BaseModel, ConfigDict


class HotelCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    owner_id: str
    name: str
    city: str
    address: str
    description: str
    rating: float



