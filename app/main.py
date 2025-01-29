import asyncio
from passlib.context import CryptContext
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, Annotated
from sqlalchemy.exc import IntegrityError

app = FastAPI()

# Database configuration

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# This is a dependency, will need to be moved to another file ->
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

# Database models will need to be moved to the db direcotory ->
class UserBase(SQLModel):
    # This is a pydantic data model becuase it doesn't have table=True
    email: str = Field(index=True, unique=True)

class User(UserBase, table=True):
    # This is a databse table because it has table=True
    id: int | None = Field(default=None, primary_key=True)
    # The email field is inherited from the UserBase model
    hashed_password: str

class UserPublic(UserBase):
    # This is the model that will be rturned to users, as of now all we need to return is the email, which is similar to the UserBase model anyways, in the future we can return more data
    pass

class UserCreate(UserBase):
    # The data model that will be used to validate the data used to create a new user
    id: int | None = Field(default=None, primary_key=True)
    plain_password: str

class UserUpdate():
    # There is no need to inherit UserBase because all the fields will be redeclared in order to allow some fields to not be modified
    id: int | None = None
    email: str | None = None
    hashed_password: str | None = None

class UserLogin(UserBase):
    plain_password: str

    def authenticate():
        pass



# Pydantic models will need their own file in the future ->
class LoginResponse(BaseModel):
    jwt: str


# Utility functions
def jwt():
    return 0

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def home():
    return {"Hello": "World"}

@app.post("/login", response_model=UserPublic)
async def login(): # async def with non-blocking IO operations
    jwt_token = jwt
    return jwt_token

@app.post("/register", response_model=UserPublic)
def register(user: UserCreate, session: SessionDep):
    validated_user = UserCreate.model_validate(user)
    
    db_user = User(email=validated_user.email, hashed_password=hash_password(validated_user.plain_password))
    print(db_user)
    
    session.add(db_user)
    
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        ) from e

    session.refresh(db_user)
    return db_use