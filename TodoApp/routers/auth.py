from fastapi import Depends, HTTPException, status,APIRouter
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import models
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "9aVfsmugd8InEDof"
ALGORITHM = "HS256"


class CreateUser(BaseModel):
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str


router= APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=200)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def raise_item_cannot_be_found_exception(status_code: int, detail: str, headers: str):
    raise HTTPException(status_code=status_code, detail=detail,
                        headers={"X-Header-Error": headers})

async def get_current_user(token:str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])
        username:str=payload.get("sub")
        user_id : int = payload.get("id")
        if username is None or user_id is None:
            raise get_user_exception()
        return {"username": username, "id": user_id}
    except:
        raise get_user_exception()


@router.post("/create/user", status_code=status.HTTP_201_CREATED)
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):
    create_user_model = models.Users()
    create_user_model.email = create_user.email
    create_user_model.username = create_user.username
    create_user_model.first_name = create_user.first_name
    create_user_model.last_name = create_user.last_name
    create_user_model.hashed_password = get_password_hash(create_user.password)
    create_user_model.is_active = True
    try:
        db.add(create_user_model)
        db.commit()
        return "User created"
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate users")


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise get_user_exception()
    token_expires = timedelta(minutes=20)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)
    return {"token":token}


#exception

def get_user_excetpion_unauthorized():
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="unauthorized user",
                                          headers={"WWW- Authenticate": "Bearer"},
                                          )
    return credentials_exception


def get_user_exception():
    credentials_exception = HTTPException( status_code = status.HTTP_401_UNAUTHORIZED,
                                           detail="Could not validate credentials",
                                           headers={"WWW- Authenticate": "Bearer"},
                                           )
    return credentials_exception


def token_exception():
    token_exception = HTTPException( status_code = status.HTTP_401_UNAUTHORIZED,
                                           detail="Incorrect username or password",
                                           headers={"WWW- Authenticate": "Bearer"},
                                           )
    return token_exception

