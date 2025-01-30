from pydantic import BaseModel
from sqlmodel import SQLModel, Field

# Database models will need to be moved to the db direcotory ->
class UserBase(SQLModel):
    # This is a pydantic data model becuase it doesn't have table=True
    email: str = Field(index=True, unique=True)

class UserPublic(UserBase):
    # This is the model that will be rturned to users, as of now all we need to return is the email, which is similar to the UserBase model anyways, 
    # in the future we can return more data
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


# Pydantic models will need their own file in the future ->
class LoginResponse(BaseModel):
    jwt: str
