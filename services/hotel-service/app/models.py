from uuid import uuid4
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
class Hotel(Base):
    __tablename__ = "hotels"
    title: Mapped[str]
    description: Mapped[str]
    rating: Mapped[float]
    rooms: Mapped[list["Room"]] = relationship(back_populates="hotel")
class Room(Base):
    __tablename__ = "rooms"
    hotel_id: Mapped[str] = mapped_column(ForeignKey("hotels.id"))
    title: Mapped[str]
    description: Mapped[str]
    price: Mapped[float]
    hotel: Mapped["Hotel"] = relationship(back_populates="rooms")

