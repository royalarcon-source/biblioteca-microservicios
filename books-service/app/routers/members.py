from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from ..dependencies import MemberRepo
from ..schemas import MemberIn, MemberOut

router = APIRouter(prefix="/members", tags=["Socios"])


@router.get("", response_model=list[MemberOut])
def list_members(repo: MemberRepo, skip: int = 0, limit: int = Query(50, le=200)):
    return repo.list(skip, limit)


@router.get("/{member_id}", response_model=MemberOut)
def get_member(member_id: int, repo: MemberRepo):
    member = repo.get(member_id)
    if not member:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Socio no encontrado")
    return member


@router.post("", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
def create_member(data: MemberIn, repo: MemberRepo):
    try:
        return repo.create(data.model_dump())
    except IntegrityError:
        repo.db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un socio con ese correo")


@router.put("/{member_id}", response_model=MemberOut)
def update_member(member_id: int, data: MemberIn, repo: MemberRepo):
    member = repo.get(member_id)
    if not member:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Socio no encontrado")
    try:
        return repo.update(member, data.model_dump())
    except IntegrityError:
        repo.db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un socio con ese correo")


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, repo: MemberRepo):
    member = repo.get(member_id)
    if not member:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Socio no encontrado")
    repo.delete(member)
