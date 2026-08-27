from pwdlib import PasswordHash
import jwt
from datetime import UTC, datetime, timedelta

from .models import User
from .schemas import token_payload
from .config import settings


password_hash = PasswordHash()

def hash_password(password):
    return password_hash.hash(password)

def verify_password(password, encoded_password):
    return password_hash.verify(password, encoded_password)

def create_access_token(user: User):
    now = datetime.now(UTC)
    expires_in = now + timedelta(seconds=360)
    payload = token_payload(**user, exp=expires_in, role="user").model_dump(mode="json")
    token = jwt.encode(
        payload,
        key=settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm
    )

    return token