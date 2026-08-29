from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import engine, get_connection
from .models import Base, Hotel, Room
from .schemas import HotelRead, HotelCreate, HotelUpdate, RoomRead, RoomCreate, RoomUpdate



@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/hotels", response_model=HotelRead)
async def create_hotel(hotel_data: HotelCreate, session: AsyncSession = Depends(get_connection)):
    new_hotel = Hotel(**hotel_data.model_dump())
    session.add(new_hotel)
    await session.commit()
    await session.refresh(new_hotel)
    return new_hotel

@app.get("/hotels/{hotel_id}", status_code=status.HTTP_200_OK, response_model=HotelRead)
async def get_hotel(hotel_id: str,
                    connection: AsyncSession = Depends(get_connection)):
    hotel = await connection.get(Hotel, hotel_id)
    if hotel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Hotel with {hotel_id} is not found")
    return hotel
    

@app.patch("/hotels/{hotel_id}", response_model=HotelRead, status_code=status.HTTP_200_OK)
async def update_hotel(hotel_id: str,
                       hotel_update: HotelUpdate,
                       connection: AsyncSession = Depends(get_connection)):
    hotel = await connection.get(Hotel, hotel_id)

    if hotel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Hotel with {hotel_id} is not found")
    update_data = hotel_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(hotel, field, value)
    await connection.commit()
    await connection.refresh(hotel)
    return hotel

@app.post("/hotels/{hotel_id}/rooms", response_model=RoomRead)
async def create_room(hotel_id: str, room_data: RoomCreate, session: AsyncSession = Depends(get_connection)):
    new_room = Room(**room_data.model_dump(), hotel_id=hotel_id)
    session.add(new_room)
    await session.commit()
    await session.refresh(new_room)
    return new_room

@app.get("/hotels/{hotel_id}/rooms", response_model=list[RoomRead])
async def get_rooms(hotel_id: str, session: AsyncSession = Depends(get_connection)):
    result = await session.execute(select(Room).where(Room.hotel_id == hotel_id))
    rooms = result.scalars().all()
    return rooms

