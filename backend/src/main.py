from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.src.core.neo4j_db import close_neo4j_driver, init_neo4j_driver, _driver
from backend.src.core.neo4j_indexes import create_vector_indexes
from backend.src.modules.auth.router import router as auth_router
from backend.src.modules.users.router import router as users_router
from backend.src.modules.artifacts.router import router as artifacts_router
from backend.src.modules.data_forge.router import router as data_forge
from backend.src.modules.search.router import router as search_router
from backend.src.modules.search.router import router as impact_analysis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_neo4j_driver()
    if _driver:
        with _driver.session() as session:
            create_vector_indexes(session)
    yield
    # Shutdown
    close_neo4j_driver()


app = FastAPI(title="DefectMind API", lifespan=lifespan)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router, tags=["Auth"])
app.include_router(users_router, prefix="/api/v1", tags=["Users"])
app.include_router(artifacts_router, prefix="/api/v1", tags=["Artifacts"])
app.include_router(data_forge, prefix="/data-forge", tags=["Data Forge"])
app.include_router(search_router, prefix="/api/v1/search", tags=["Search"])
app.include_router(impact_analysis, prefix="/api/v1/search", tags=["Impact Analysis"])
