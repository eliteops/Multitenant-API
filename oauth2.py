from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select

import model
from database import Session, get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


router = APIRouter(tags=["show_current_user"])


@router.get("/show_current_user", status_code=status.HTTP_200_OK)
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Decode the token to extract user information
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name = payload.get("sub")  # Assuming "sub" contains the user ID

        # current_user = db.execute(select(model.LoginModel).where(model.LoginModel.user_name == user_name)).scalars().all()

        # Query the database to retrieve the logged-in user

        current_user = (
            db.execute(select(model.LoginModel.user_name, model.LoginModel.user_id, model.Role.role_name) # getting error in this and joins are not showing only user_name is showing
                       .join(model.UsersRole, model.UsersRole.user_id == model.LoginModel.user_id)
                       .join(model.Role, model.Role.role_id == model.UsersRole.role_id)
                       .where(model.LoginModel.user_name == user_name)).scalars().all()
        )


        print(current_user)

        if current_user:

            return current_user
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
