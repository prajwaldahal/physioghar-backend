from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=settings.api_v1_prefix)


# HEAD as well as GET, because uptime monitors ping with HEAD by default.
@app.api_route("/health", methods=["GET", "HEAD"])
def health() -> dict[str, str]:
    return {"status": "ok"}
