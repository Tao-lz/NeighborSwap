from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import BASE_DIR, settings
from .database import Base, engine
from .routers import comments, dashboard, images, items, llm, me, users, wants

# 导入 models 以注册所有表
from . import models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title=f"{settings.app_name} API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uploads_dir = BASE_DIR / "uploads"
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

app.include_router(users.router)
app.include_router(items.router)
app.include_router(wants.router)
app.include_router(comments.router)
app.include_router(images.router)
app.include_router(me.router)
app.include_router(dashboard.router)
app.include_router(llm.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}
