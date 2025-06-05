from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import schedules, consumables
from app.database import init_db
import logging
from pydantic import BaseModel

class Config:
    from_attributes = True  # Update for Pydantic v2

app = FastAPI(title="Smart Home Assistant API")

# Configure CORS
origins = [
    "http://localhost:4200",  # Dev - Angular default
    "http://localhost:80",    # Dev - Docker with port 80
    "http://localhost",       # Dev - Docker default port
    "*",                      # Allow all origins in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize logger
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

# Initialize database
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up database...")
    try:
        await init_db.create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

# Include routers
app.include_router(schedules.router, prefix="/api/schedules", tags=["schedules"])
app.include_router(consumables.router, prefix="/api/consumables", tags=["consumables"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Home Assistant API"}

@app.get("/health")
async def health():
    return {"status": "ok"}
