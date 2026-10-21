from datetime import datetime, timedelta

from passlib.context import CryptContext
from jose import jwt




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
    hashed_password: str
):

    return pwd_context.verify(
        password[:72],
        hashed_password
    )



def create_access_token(data: dict):

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