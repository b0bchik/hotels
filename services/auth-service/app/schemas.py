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