from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.deps import get_current_user
from src.api.schemas import NoteCreateRequest, NoteResponse, NoteUpdateRequest
from src.core.db import fetch_all, fetch_one

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get(
    "",
    response_model=list[NoteResponse],
    summary="List notes",
    description="List notes for the current user. Optionally filter by folder_id.",
)
def list_notes(
    folder_id: UUID | None = Query(None, description="Filter notes by folder id."),
    current_user: dict = Depends(get_current_user),
) -> list[NoteResponse]:
    if folder_id is None:
        rows = fetch_all(
            "SELECT id, folder_id, title, content, created_at, updated_at "
            "FROM notes WHERE user_id = %s ORDER BY updated_at DESC",
            (str(current_user["id"]),),
        )
    else:
        rows = fetch_all(
            "SELECT id, folder_id, title, content, created_at, updated_at "
            "FROM notes WHERE user_id = %s AND folder_id = %s ORDER BY updated_at DESC",
            (str(current_user["id"]), str(folder_id)),
        )
    return [NoteResponse(**r) for r in rows]


@router.post(
    "",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create note",
    description="Create a new note for the current user.",
)
def create_note(payload: NoteCreateRequest, current_user: dict = Depends(get_current_user)) -> NoteResponse:
    # Optional: validate folder belongs to user
    if payload.folder_id is not None:
        folder = fetch_one(
            "SELECT id FROM folders WHERE id = %s AND user_id = %s",
            (str(payload.folder_id), str(current_user["id"])),
        )
        if not folder:
            raise HTTPException(status_code=400, detail="Invalid folder_id")

    row = fetch_one(
        "INSERT INTO notes (user_id, folder_id, title, content) VALUES (%s, %s, %s, %s) "
        "RETURNING id, folder_id, title, content, created_at, updated_at",
        (str(current_user["id"]), str(payload.folder_id) if payload.folder_id else None, payload.title, payload.content),
    )
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create note")
    return NoteResponse(**row)


@router.patch(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Update note",
    description="Update a note (title/content/folder). Only affects current user's note.",
)
def update_note(
    note_id: UUID,
    payload: NoteUpdateRequest,
    current_user: dict = Depends(get_current_user),
) -> NoteResponse:
    if payload.folder_id is not None:
        folder = fetch_one(
            "SELECT id FROM folders WHERE id = %s AND user_id = %s",
            (str(payload.folder_id), str(current_user["id"])),
        )
        if not folder:
            raise HTTPException(status_code=400, detail="Invalid folder_id")

    existing = fetch_one(
        "SELECT id, folder_id, title, content FROM notes WHERE id = %s AND user_id = %s",
        (str(note_id), str(current_user["id"])),
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")

    new_title = payload.title if payload.title is not None else existing["title"]
    new_content = payload.content if payload.content is not None else existing["content"]
    new_folder_id = payload.folder_id if payload.folder_id is not None else existing["folder_id"]

    row = fetch_one(
        "UPDATE notes SET folder_id = %s, title = %s, content = %s WHERE id = %s AND user_id = %s "
        "RETURNING id, folder_id, title, content, created_at, updated_at",
        (str(new_folder_id) if new_folder_id else None, new_title, new_content, str(note_id), str(current_user["id"])),
    )
    if not row:
        raise HTTPException(status_code=500, detail="Failed to update note")
    return NoteResponse(**row)


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete note",
    description="Delete a note owned by the current user.",
)
def delete_note(note_id: UUID, current_user: dict = Depends(get_current_user)) -> None:
    row = fetch_one(
        "DELETE FROM notes WHERE id = %s AND user_id = %s RETURNING id",
        (str(note_id), str(current_user["id"])),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    return None
