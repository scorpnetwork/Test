from app.api.users.schemas import UserBase
from sqlmodel import SQLModel, Field


class User(UserBase, table=True):
    # This is a databse table because it has table=True
    id: int | None = Field(default=None, primary_key=True)
    # The email field is inherited from the UserBase model
    hashed_password: str
