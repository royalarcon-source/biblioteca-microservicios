from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import Base, engine
from .routers import books, members


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Microservicio Biblioteca Digital", version="1.0.0", lifespan=lifespan)
app.include_router(books.router)
app.include_router(members.router)


@app.get("/health", tags=["Salud"])
def health():
    return {"status": "ok", "service": "books-service"}
