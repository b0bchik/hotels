from pydantic import BaseModel, EmailStr
from datetime import UTC, datetime, timedelta

class CredentialsBase(BaseModel):
    email: EmailStr
    password: str

class RegisterUser(CredentialsBase):
    pass

class token_payload(CredentialsBase):
    exp: datetime
    role: str