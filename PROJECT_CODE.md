# Hotels Microservices Project

Микросервисное приложение для управления отелями, бронированиями и рецензиями.

## Структура проекта

```
hotels/
├── all_requirements.txt
├── gateway/
├── infra/
├── services/
│   ├── auth-service/
│   ├── availability-service/
│   ├── booking-service/
│   ├── hotel-service/
│   ├── notification-service/
│   ├── payment-service/
│   ├── review-service/
│   └── search-service/
├── shared/
│   └── schemas/
└── myenv/               # Python virtual environment
```

---

## Зависимости проекта (all_requirements.txt)

```
fastapi
uvicorn[standard]
pydantic-settings
sqlalchemy
asyncpg
httpx
aio-pika
aiokafka
pymongo
email-validator
PyJWT[crypto]
pwdlib[argon2]
```

---

## Auth Service

### main.py

```python
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

app = FastAPI(lifespan=lifespan)

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

@app.post("/login",
         status_code=status.HTTP_200_OK)
async def login(current_user: UserRegister,
                session: AsyncSession = Depends(get_connection)):
    user = await session.execute(select(User).where(User.email == current_user.email)).scalars().first()
    
    if not user:
       raise HTTPException(
                   status_code=status.HTTP_400_BAD_REQUEST,
                   detail="Incorrect email or password"
               )
     
    if not verify_password(current_user.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password or eamil"
        )
    access_token = create_access_token(user)

    return TokenResponse(access_token=access_token, user=UserRead.model_validate(user))
```

### config.py

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):   
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str 
    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"


settings = Settings()
```

### database.py

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from .config import settings

from typing import AsyncGenerator


engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_connection() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as connection:
        yield connection
```

### models.py

```python
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
```

### schemas.py

```python
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import UTC, datetime, timedelta


class CredentialsBase(BaseModel):
    email: EmailStr
    password: str

class UserRegister(CredentialsBase):
    pass

class TokenPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    exp: datetime
    role: str

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
```

### security.py

```python
from pwdlib import PasswordHash
import jwt
from datetime import UTC, datetime, timedelta

from .models import User
from .schemas import TokenPayload
from .config import settings


password_hash = PasswordHash()

def hash_password(password):
    return password_hash.hash(password)

def verify_password(password, encoded_password):
    return password_hash.verify(password, encoded_password)

def create_access_token(user: User):
    now = datetime.now(UTC)
    expires_in = now + timedelta(seconds=360)
    payload = TokenPayload(email=user.email, exp=expires_in, role="user").model_dump(mode="json")
    token = jwt.encode(
        payload,
        key=settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm
    )

    return token
```

---

## Hotel Service

### main.py

```python
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

@app.post("/hotels/{hotel_id}/rooms", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(hotel_id: str,
                      room: RoomCreate,
                      connection: AsyncSession = Depends(get_connection)):
    hotel = await connection.get(Hotel, hotel_id)
    if hotel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Hotel with {hotel_id} is not found")
    new_room = Room(**room.model_dump(), hotel_id=hotel_id)
    return new_room

@app.get("/hotels/{id}/rooms", response_model=RoomRead, status_code=status.HTTP_200_OK)
async def get_rooms(room_id: int,
                    connection: AsyncSession = Depends(get_connection)):
    room = await connection.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Room with {room_id} is not found")
    return Room
```

### config.py

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):   
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str 
    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"


settings = Settings()
```

### database.py

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from .config import settings

from typing import AsyncGenerator


engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_connection() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as connection:
        yield connection
```

### models.py

```python
from uuid import uuid4
from decimal import Decimal
from sqlalchemy import ForeignKey, String, Numeric
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
    capacity: Mapped[int]
    base_price: Mapped[Decimal] = mapped_column(Numeric(10,2))
```

### schemas.py

```python
from pydantic import BaseModel, ConfigDict
from decimal import Decimal


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
    model_config = ConfigDict(from_attributes=True)
    name: str | None = None
    city: str | None = None
    address: str | None = None
    description: str | None = None
    rating: float | None = None

class RoomBase(BaseModel):
    capacity: int
    base_price: Decimal

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    capacity: int | None = None
    base_price: Decimal | None = None

class RoomRead(RoomBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hotel_id: int
```

---

## Архитектура проекта

### Auth Service
- **Описание**: Сервис аутентификации и авторизации
- **API Endpoints**:
  - `POST /register` - Регистрация нового пользователя
  - `POST /login` - Вход пользователя
- **Функции**: Хеширование паролей, создание JWT токенов

### Hotel Service
- **Описание**: Сервис управления отелями и комнатами
- **API Endpoints**:
  - `POST /hotels` - Создание отеля
  - `GET /hotels/{hotel_id}` - Получение информации об отеле
  - `PATCH /hotels/{hotel_id}` - Обновление информации об отеле
  - `POST /hotels/{hotel_id}/rooms` - Создание комнаты
  - `GET /hotels/{id}/rooms` - Получение списка комнат

### Прочие сервисы
- **availability-service** - Управление доступностью комнат
- **booking-service** - Управление бронированиями
- **notification-service** - Отправка уведомлений
- **payment-service** - Обработка платежей
- **review-service** - Управление рецензиями
- **search-service** - Поиск отелей и комнат

---

## Технологический стек

- **Framework**: FastAPI
- **ORM**: SQLAlchemy (async)
- **Database**: PostgreSQL (asyncpg)
- **Authentication**: JWT + PyJWT
- **Password Hashing**: pwdlib (Argon2)
- **Message Queue**: RabbitMQ (aio-pika), Kafka (aiokafka)
- **Database Alternatives**: MongoDB (pymongo)
- **Validation**: Pydantic + Email-validator
- **Web Server**: Uvicorn

---

## Примечания

✅ Проект имеет асинхронную архитектуру с async/await
✅ Использует Pydantic для валидации данных
✅ JWT-токены для аутентификации
✅ SQLAlchemy ORM для работы с БД
✅ Микросервисная архитектура с несколькими сервисами
✅ Поддержка различных типов БД (PostgreSQL, MongoDB)

