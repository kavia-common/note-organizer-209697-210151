from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import get_current_user
from src.api.schemas import (
    AuthTokenResponse,
    LoginRequest,
    RegisterRequest,
    UserMeResponse,
)
from src.core.db import fetch_one
from src.core.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserMeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account with email + password.",
)
def register(payload: RegisterRequest) -> UserMeResponse:
    existing = fetch_one("SELECT id FROM users WHERE email = %s", (payload.email,))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    pw_hash = hash_password(payload.password)
    user = fetch_one(
        "INSERT INTO users (email, password_hash) VALUES (%s, %s) "
        "RETURNING id, email, created_at",
        (payload.email, pw_hash),
    )
    assert user is not None
    return UserMeResponse(**user)


@router.post(
    "/login",
    response_model=AuthTokenResponse,
    summary="Login",
    description="Authenticates user and returns a Bearer JWT access token.",
)
def login(payload: LoginRequest) -> AuthTokenResponse:
    user = fetch_one(
        "SELECT id, email, password_hash FROM users WHERE email = %s",
        (payload.email,),
    )
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(sub=str(user["id"]), email=user["email"])
    return AuthTokenResponse(access_token=token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserMeResponse,
    summary="Get current user",
    description="Returns the current authenticated user's profile.",
)
def me(current_user: dict = Depends(get_current_user)) -> UserMeResponse:
    return UserMeResponse(**current_user)
