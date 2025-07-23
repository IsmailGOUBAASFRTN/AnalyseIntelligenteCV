from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import analysis_router
from .db.session import engine
from .db import models

# Crée la table si elle n'existe pas (pour un démarrage simple sans migrations)
# Dans un projet de production, utilisez Alembic pour gérer les migrations.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CV Analyzer API")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Autorise le frontend React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the CV Analyzer API"}