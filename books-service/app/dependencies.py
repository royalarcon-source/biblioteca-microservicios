"""Inyección de dependencias (Depends)."""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import Book, Member
from .repository import Repository


def get_book_repo(db: Session = Depends(get_db)) -> Repository[Book]:
    return Repository(db, Book)


def get_member_repo(db: Session = Depends(get_db)) -> Repository[Member]:
    return Repository(db, Member)


BookRepo = Annotated[Repository[Book], Depends(get_book_repo)]
MemberRepo = Annotated[Repository[Member], Depends(get_member_repo)]
