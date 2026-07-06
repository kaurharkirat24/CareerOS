from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db.session import create_db_and_tables
from backend.api import applications, auth, jobs, profile
from backend.core.logger import get_logger
from backend.core.config import settings
from fastapi.responses import JSONResponse
from fastapi.requests import Request

logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    create_db_and_tables()
    logger.info("Database initialized and server started")
    yield
    logger.info("Server shutting down")

app = FastAPI(title="AI Job Search Agent API", lifespan=lifespan)

@app.middleware("http")
async def log_unhandled_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled Exception on {request.method} {request.url}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected internal server error occurred. Please try again later."},
        )

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=settings.BACKEND_CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Job Search Agent API"}

# Add routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
