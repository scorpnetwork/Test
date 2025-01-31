from fastapi import Depends, FastAPI, HTTPException, status
from typing import Annotated
from sqlmodel import SQLModel, Session

from app.api.users.models import User 
from app.api.users.schemas import UserBase, UserPublic, UserCreate, UserUpdate, UserLogin
from app.db.database import get_session, create_db_and_tables
from app.api.users.routes import router as user_routes

app = FastAPI()
app.include_router(user_routes)

# Database configuration

SessionDep = Annotated[Session, Depends(get_session)]

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def home():
    return {"Hello": "World"}
