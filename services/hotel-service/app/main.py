from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import engine, get_connection
from .models import Base, Hotel, Room
from .schemas import HotelCreateSchema



@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/hotels", status_code=status.HTTP_201_CREATED, response_model=HotelCreateSchema)
async def create_hotel(hotel: HotelCreateSchema, 
                       connection: AsyncSession = Depends(get_connection),
            ):
    new_hotel = Hotel(**hotel.model_dump())
    connection.add(new_hotel)
    await connection.commit()
    return new_hotel

@app.get("hotels/{id}")
async def get_hotel():
    ...

@app.patch("hotels/{id}")
async def update_hotel():
    ...

@app.post("/hotels/{id}/rooms")
async def create_room():
    ...

@app.get("/hotels/{id}/rooms")
async def get_rooms():
    ...
