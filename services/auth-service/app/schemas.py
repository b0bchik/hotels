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