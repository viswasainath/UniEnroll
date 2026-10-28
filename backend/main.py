from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import logging
from .database import Neo4jManager
from .routers import students, courses, clashes, venues, faculty, graph, seed

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("unienroll")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing UniEnroll FFCS Backend...")
    try:
        health = Neo4jManager.check_connection()
        logger.info(f"Connected to Neo4j successfully! Node counts: {health.get('node_counts')}")
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j on startup: {e}")
    yield
    logger.info("Shutting down UniEnroll FFCS Backend...")
    Neo4jManager.close()

app = FastAPI(
    title="UniEnroll: FFCS Management Platform API",
    description="Full-stack Graph Database Backend for University FFCS with Neo4j",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(students.router)
app.include_router(courses.router)
app.include_router(clashes.router)
app.include_router(venues.router)
app.include_router(faculty.router)
app.include_router(graph.router)
app.include_router(seed.router)

@app.get("/api/health")
def api_health():
    return Neo4jManager.check_connection()

# Serve built frontend if available
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    from fastapi.staticfiles import StaticFiles
    from starlette.responses import FileResponse

    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.api_route("/{full_path:path}", methods=["GET", "HEAD"])
    async def serve_spa(full_path: str):
        # Don't intercept API calls
        if full_path.startswith("api"):
            return {"error": "API route not found"}
        target_file = frontend_dist / full_path
        if target_file.exists() and target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(frontend_dist / "index.html")
else:
    @app.get("/")
    def root():
        return {
            "app": "UniEnroll: FFCS Management Platform",
            "version": "1.0.0",
            "status": "online",
            "docs_url": "/docs",
            "frontend": "Run 'npm run dev' inside frontend/ or 'npm run build' to generate static assets."
        }

if __name__ == "__main__":
    import uvicorn
    from .config import BACKEND_PORT
    uvicorn.run("backend.main:app", host="0.0.0.0", port=BACKEND_PORT, reload=True)
