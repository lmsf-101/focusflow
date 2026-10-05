from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ProjectUpdate(BaseModel):
    name: str = Field(default="", min_length=1)


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1)


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CategoryUpdate(BaseModel):
    name: str = Field(default="", min_length=1)
