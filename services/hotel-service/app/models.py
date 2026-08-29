from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )


class Hotel(Base):
    __tablename__ = "hotels"
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str]
    city: Mapped[str]
    address: Mapped[str]
    description: Mapped[str]
    rating: Mapped[float]

class Room(Base):
    __tablename__ = "rooms"
    hotel_id: Mapped[str] = mapped_column(ForeignKey("hotels.id"), nullable=False)
    type: Mapped[str]
    capacity: Mapped[int]
    base_price: Mapped[float]
    amenities: Mapped[list[str]]

  



