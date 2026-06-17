from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager
from .database import engine
from . import models
from .routers import auth, leads, calls, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Life Insurance CRM", version="1.0.0", lifespan=lifespan)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})

app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(calls.router)
app.include_router(dashboard.router)

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
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
