from pydantic import BaseModel, EmailStr


class CredentialsBase(BaseModel):
    email: EmailStr
    password: str

class RegisterUser(CredentialsBase):
    pass
