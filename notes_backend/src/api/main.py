from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.api.routes_auth import router as auth_router
from src.api.routes_folders import router as folders_router
from src.api.routes_notes import router as notes_router

openapi_tags = [
    {"name": "auth", "description": "Authentication (register/login/me)."},
    {"name": "folders", "description": "Folder management."},
    {"name": "notes", "description": "Notes CRUD."},
    {"name": "system", "description": "Health and system endpoints."},
]

settings = get_settings()

app = FastAPI(
    title="Notes API",
    description="A simple full-stack notes app API (auth, folders, notes).",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(folders_router)
app.include_router(notes_router)


@app.get(
    "/",
    tags=["system"],
    summary="Health check",
    description="Simple health check endpoint.",
)
def health_check():
    """Backend health check."""
    return {"message": "Healthy"}
