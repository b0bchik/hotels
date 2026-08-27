from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import engine, get_connection
from .models import Base, User
from .schemas import UserRegister
from .security import hash_password, verify_password, create_access_token


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI()

@app.post("/regiser",
          status_code=status.HTTP_201_CREATED)
async def register(current_user: UserRegister,
                   session = Depends(get_connection)):
    user = User(email=current_user.email, hash_password=hash_password(current_user.password))
    session.add(user)
    await session.commit()
    return 
