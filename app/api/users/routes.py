from fastapi import APIRouter
from passlib.context import CryptContext
from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import SQLModel, Session, create_engine, select
from typing import Annotated
from sqlalchemy.exc import IntegrityError
from app.db.database import get_session
from app.api.users.models import User 
from app.api.users.schemas import UserBase, UserPublic, UserCreate, UserUpdate, UserLogin

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

@router.post("/login", response_model=UserPublic, responses={409: {"description": "Wrong email or password"}})
async def login(user: UserLogin, session: SessionDep): # async def with non-blocking IO operations
    """
    Logs a user in, upon success, the user is authenticated and a JWT is returned.

    - **email**: The email of the user from the HTML form.
    - **plain_password**: The plain password from the HTML form.
    """

    validated_user = UserLogin.model_validate(user)

    stmt = select(User).where(User.email == validated_user.email)
    result = session.exec(stmt).first()

    print(result)
    
    if not result:
        raise HTTPException(status_code=409, detail="Wrong email or password")
    
    # Verify if the provided plain password matches the hashed password in the database
    if not pwd_context.verify(validated_user.plain_password, result.hashed_password):
        raise HTTPException(status_code=409, detail="Wrong email or password")

    return UserPublic(email=validated_user.email)

@router.post("/register", response_model=UserPublic, responses={409: {"description": "Email already registered"}})
def register(user: UserCreate, session: SessionDep):
    """
    Creates a new account, upon success, a user is register in the database, authenticated and a JWT is returned.

    - **email**: The email of the user from the HTML form.
    - **plain_password**: The plain password from the HTML form.
    """

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
    return db_user