from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext


SECRET_KEY = "prathamesh"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):

    return pwd_context.hash(
        password[:72]
    )


def verify_password(
    password: str,
    password_hash: str
):

    return pwd_context.verify(
        password[:72],
        password_hash
    )


def create_access_token(
    data: dict
):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )