from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi import Depends, APIRouter, HTTPException, status
import model
from database import Session, get_db
import oauth2

router = APIRouter(tags=["Authentication"])


@router.post("/token")
async def get_token(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = (
        db.query(model.LoginModel)
        .filter(model.LoginModel.user_name == request.username)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid username or password"
        )

    if request.password != user.user_password:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="password didn't match."
        )

    access_token = oauth2.create_access_token(data={"sub": user.user_name})

    return {"access_token": access_token, "token_type": "bearer"}
