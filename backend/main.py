from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from .database import engine
from . import models
from .routers import auth, leads, calls, dashboard

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Life Insurance CRM", version="1.0.0")

app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(calls.router)
app.include_router(dashboard.router)

FRONTEND = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND)), name="static")


@app.get("/")
def root():
    return FileResponse(str(FRONTEND / "index.html"))


@app.get("/{page}.html")
def serve_page(page: str):
    f = FRONTEND / f"{page}.html"
    if f.exists():
        return FileResponse(str(f))
    return FileResponse(str(FRONTEND / "index.html"))
