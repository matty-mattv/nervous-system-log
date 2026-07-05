"""
FastAPI application and routes.

Java comparison: this file is your @RestController. FastAPI's
decorators (@app.post, @app.get) play the same role as @PostMapping,
@GetMapping - they map an HTTP method + path to a function.
"""

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from api import crud, schemas
from api.database import get_db, engine, Base

# In a Spring Boot app, Hibernate can auto-create tables via
# spring.jpa.hibernate.ddl-auto=update (dev only, never production).
# We're intentionally NOT doing that here - Alembic migrations are
# the only thing allowed to change schema, even in dev. This line is
# commented out on purpose, as a reminder of that discipline:
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nervous System Log")

@app.post("/entries", response_model=schemas.EntryResponse)
def create_entry(entry: schemas.EntryCreate, db: Session = Depends(get_db)):
    try:
        saved = crud.create_entry(db, entry)
        return crud.entry_to_response(saved)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/entries", response_model=list[schemas.EntryResponse])
def list_entries(limit: int = 50, db: Session = Depends(get_db)):
    entries = crud.get_entries(db, limit=limit)
    return [crud.entry_to_response(e) for e in entries]


@app.get("/health")
def health_check():
    """
    A simple liveness endpoint - useful once we containerize, since
    Docker/Kubernetes health checks need something to hit.
    """
    return {"status": "ok"}