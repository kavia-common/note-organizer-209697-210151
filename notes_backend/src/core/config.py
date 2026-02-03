import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""
    database_url: str
    jwt_secret: str
    jwt_expires_in: int
    cors_origins: list[str]


def _parse_cors_origins(raw: str | None) -> list[str]:
    if not raw:
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Load application settings from environment variables."""
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        # Keep a helpful default for local dev consistent with notes_database/startup.sh
        database_url = "postgresql://appuser:dbuser123@localhost:5000/myapp"

    jwt_secret = os.getenv("JWT_SECRET", "").strip() or "change_me_super_secret"
    jwt_expires_in = int(os.getenv("JWT_EXPIRES_IN", "86400").strip() or "86400")
    cors_origins = _parse_cors_origins(os.getenv("CORS_ORIGINS"))

    return Settings(
        database_url=database_url,
        jwt_secret=jwt_secret,
        jwt_expires_in=jwt_expires_in,
        cors_origins=cors_origins,
    )
