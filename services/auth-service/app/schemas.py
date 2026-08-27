from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import UTC, datetime, timedelta

class CredentialsBase(BaseModel):
    email: EmailStr
    password: str

class RegisterUser(CredentialsBase):
    pass

class token_payload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    exp: datetime
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead

class UserRead(BaseModel):
    id: str
    email: str