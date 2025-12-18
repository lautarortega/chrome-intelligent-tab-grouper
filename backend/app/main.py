import time
from fastapi import FastAPI, Request
from app.api.endpoints import tabs
from app.core.logging import setup_logging, logger

# Initialize logging
setup_logging()

app = FastAPI(title="Chrome Intelligent Tab Grouper API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Duration: {process_time:.2f}ms"
    )
    return response

app.include_router(tabs.router, prefix="/api/v1", tags=["tabs"])

@app.get("/")
async def root():
    return {"message": "Welcome to Chrome Intelligent Tab Grouper API"}
