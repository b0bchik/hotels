from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import engine, get_connection
from .models import Base, User
from .schemas import UserRegister, TokenResponse, UserRead
from .security import hash_password, verify_password, create_access_token


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI()

@app.post("/register",
          status_code=status.HTTP_201_CREATED)
async def register(current_user: UserRegister,
                   session: AsyncSession = Depends(get_connection)):
    user = await session.execute(select(User).where(User.email == current_user.email))
    
    if user.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    user = User(email=current_user.email, hashed_password=hash_password(current_user.password))

    session.add(user)
    await session.commit()
    await session.refresh(user)
    access_token = create_access_token(user)

    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))
