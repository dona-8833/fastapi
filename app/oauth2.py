from fastapi import Depends,status,HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError,jwt
from datetime import datetime,timedelta

from sqlalchemy.orm import Session

from . import schema, database, models

oauth2_scheme = OAuth2PasswordBearer('login')



SECRET_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp':expire})
    encode_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt

def verify_access_token(token:str,credential_exception):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        id:str = payload.get("user_id")
        if id is None:
            raise  credential_exception
        token_data = schema.TokenData(id=id)
    except JWTError:
        raise credential_exception


    return token_data

def get_current_user(token:str = Depends(oauth2_scheme),db:Session = Depends(database.get_db)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate credentials ",headers={"WWW-Authenticate":"Bearer"})
    token =  verify_access_token(token,credential_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return  user
