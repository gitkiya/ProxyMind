from fastapi import APIRouter , Depends, HTTPException, status , Response
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from .. import schema, model , utils , Oauth2
from ..  database import get_db


router = APIRouter( tags=["Authentication"] )

@router.post("/login",response_model=schema.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.email == user_credentials.username).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid username")
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password")
    
    access_token = Oauth2.create_access_token(data={"user_id": user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}


