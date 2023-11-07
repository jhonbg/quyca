from fastapi import APIRouter, HTTPException

from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.services.user import user_svc


router = APIRouter()


@router.post("", response_model=UserInDB, status_code=201)
def create_user(*, new_user: UserCreate) -> UserInDB:
    """Endpoint to create a new user in db

    Args:
        new_user (UserCreate): Schema

    Returns:
        UserInDB: User in DB schema
    """

    user = user_svc.create(obj_in=new_user)
    return user


@router.get("", response_model=list[UserInDB], status_code=200)
def get_all_user(*, skip: int = 0, limit: int = 10) -> list[UserInDB]:
    return user_svc.get_multi(skip=skip, limit=limit)


@router.get("/{id}", response_model=UserInDB, status_code=200)
def get_user(*, id: int) -> UserInDB:
    user = user_svc.get(id=id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.patch("/{id}", response_model=None)
def update_user(*, obj_in: UserUpdate, id: int) -> None:
    user = user_svc.get(id=id)
    if not user:
        raise HTTPException(404, "User not found")
    user_svc.update(id=id, obj_in=obj_in)
    return None


@router.delete("/{id}", response_model=None, status_code=204)
def delete_user(*, id: int) -> None:
    user = user_svc.delete(id=id)
    if user == 0:
        raise HTTPException(404, "User not found")
    return None
