from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import engine, get_connection
from .models import Base, User
from .schemas import UserRegister, TokenResponse, UserRead, Credentials
from .security import hash_password, verify_password, create_access_token


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/register",
          status_code=status.HTTP_201_CREATED)
async def register(credentials: UserRegister,
                   session: AsyncSession = Depends(get_connection)):
    result = await session.execute(select(User).where(User.email == credentials.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    user = User(
        email=credentials.email,
        hashed_password=hash_password(credentials.password),
        role=credentials.role
    )
     
    session.add(user)
    await session.commit()
    await session.refresh(user)
    access_token = create_access_token(user)

    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))

@app.post("/login",
         status_code=status.HTTP_200_OK)
async def login(credentials: Credentials,
                session: AsyncSession = Depends(get_connection)):
    result = await session.execute(select(User).where(User.email == credentials.email))
    user = result.scalars().first()

    if not user:
       raise HTTPException(
                   status_code=status.HTTP_400_BAD_REQUEST,
                   detail="Incorrect email or password"
               )

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    access_token = create_access_token(user)

    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))
