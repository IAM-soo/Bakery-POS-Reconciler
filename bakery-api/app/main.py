from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import Base, engine
from app.routers import products, reconciliation

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="REST API for Bakery POS — manages products and reconciliation records.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(reconciliation.router)

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(os.path.join(frontend_path, "index.html"))
