from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address (unique).")
    password: str = Field(..., min_length=6, description="User password (min 6 chars).")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address.")
    password: str = Field(..., description="User password.")


class AuthTokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token (Bearer).")
    token_type: str = Field("bearer", description="Token type.")


class UserMeResponse(BaseModel):
    id: UUID = Field(..., description="User id.")
    email: EmailStr = Field(..., description="User email.")
    created_at: datetime = Field(..., description="Account creation time.")


class FolderCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, description="Folder name.")


class FolderResponse(BaseModel):
    id: UUID = Field(..., description="Folder id.")
    name: str = Field(..., description="Folder name.")
    created_at: datetime = Field(..., description="Creation time.")
    updated_at: datetime = Field(..., description="Last update time.")


class NoteCreateRequest(BaseModel):
    folder_id: Optional[UUID] = Field(None, description="Folder id (optional).")
    title: str = Field("", max_length=200, description="Note title.")
    content: str = Field("", description="Note content.")


class NoteUpdateRequest(BaseModel):
    folder_id: Optional[UUID] = Field(None, description="Folder id (optional).")
    title: Optional[str] = Field(None, max_length=200, description="Note title.")
    content: Optional[str] = Field(None, description="Note content.")


class NoteResponse(BaseModel):
    id: UUID = Field(..., description="Note id.")
    folder_id: Optional[UUID] = Field(None, description="Folder id (optional).")
    title: str = Field(..., description="Note title.")
    content: str = Field(..., description="Note content.")
    created_at: datetime = Field(..., description="Creation time.")
    updated_at: datetime = Field(..., description="Last update time.")
