"""DTOs (Pydantic) de entrada y salida."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BookIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=120)
    isbn: str = Field(min_length=10, max_length=20)
    year: int | None = Field(default=None, ge=0, le=2100)
    copies_available: int = Field(default=1, ge=0)


class BookOut(BookIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class MemberIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    email: EmailStr


class MemberOut(MemberIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
