from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import engine, get_connection
from .models import Base, Hotel, Room
from .schemas import HotelRead, HotelCreate



@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/hotels", status_code=status.HTTP_201_CREATED, response_model=HotelCreate)
async def create_hotel(hotel: HotelCreate, 
                       connection: AsyncSession = Depends(get_connection),
            ):
    new_hotel = Hotel(**hotel.model_dump())
    connection.add(new_hotel)
    await connection.commit()
    await connection.refresh(hotel)
    return new_hotel

@app.get("/hotels/{hotel_id}", status_code=status.HTTP_200_OK, response_model=HotelRead)
async def get_hotel(hotel_id: str,
                    connection: AsyncSession = Depends(get_connection)):
    hotel = await connection.get(Hotel, hotel_id)
    if hotel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Hotel with {hotel_id} is not found")
    return hotel
    

@app.patch("/hotels/{id}")
async def update_hotel():
    ...

@app.post("/hotels/{id}/rooms")
async def create_room():
    ...

@app.get("/hotels/{id}/rooms")
async def get_rooms():
    ...
