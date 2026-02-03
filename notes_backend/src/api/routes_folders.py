from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import get_current_user
from src.api.schemas import FolderCreateRequest, FolderResponse
from src.core.db import fetch_all, fetch_one

router = APIRouter(prefix="/folders", tags=["folders"])


@router.get(
    "",
    response_model=list[FolderResponse],
    summary="List folders",
    description="List folders belonging to the current user.",
)
def list_folders(current_user: dict = Depends(get_current_user)) -> list[FolderResponse]:
    rows = fetch_all(
        "SELECT id, name, created_at, updated_at FROM folders WHERE user_id = %s ORDER BY created_at ASC",
        (str(current_user["id"]),),
    )
    return [FolderResponse(**r) for r in rows]


@router.post(
    "",
    response_model=FolderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create folder",
    description="Create a new folder for the current user.",
)
def create_folder(
    payload: FolderCreateRequest,
    current_user: dict = Depends(get_current_user),
) -> FolderResponse:
    row = fetch_one(
        "INSERT INTO folders (user_id, name) VALUES (%s, %s) "
        "RETURNING id, name, created_at, updated_at",
        (str(current_user["id"]), payload.name),
    )
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create folder")
    return FolderResponse(**row)


@router.delete(
    "/{folder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete folder",
    description="Delete a folder. Notes in that folder will have folder_id set to NULL.",
)
def delete_folder(folder_id: UUID, current_user: dict = Depends(get_current_user)) -> None:
    row = fetch_one(
        "DELETE FROM folders WHERE id = %s AND user_id = %s RETURNING id",
        (str(folder_id), str(current_user["id"])),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Folder not found")
    return None
