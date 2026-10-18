from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from ..dependencies import BookRepo
from ..schemas import BookIn, BookOut

router = APIRouter(prefix="/books", tags=["Libros"])


@router.get("", response_model=list[BookOut])
def list_books(repo: BookRepo, skip: int = 0, limit: int = Query(50, le=200)):
    return repo.list(skip, limit)


@router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: int, repo: BookRepo):
    book = repo.get(book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Libro no encontrado")
    return book


@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(data: BookIn, repo: BookRepo):
    try:
        return repo.create(data.model_dump())
    except IntegrityError:
        repo.db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un libro con ese ISBN")


@router.put("/{book_id}", response_model=BookOut)
def update_book(book_id: int, data: BookIn, repo: BookRepo):
    book = repo.get(book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Libro no encontrado")
    try:
        return repo.update(book, data.model_dump())
    except IntegrityError:
        repo.db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un libro con ese ISBN")


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, repo: BookRepo):
    book = repo.get(book_id)
    if not book:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Libro no encontrado")
    repo.delete(book)
