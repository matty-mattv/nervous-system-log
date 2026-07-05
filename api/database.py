"""
Database connection setup.

Java comparison: this file is roughly what your DataSource bean +
application.yml datasource config + EntityManagerFactory setup do
together in Spring Boot — except explicit, because FastAPI has no
auto-configuration magic. You wire it yourself.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Reads DATABASE_URL from the environment if set (Docker Compose sets
# this for the api service - see docker-compose.yml). Falls back to
# local SQLite when running directly on your Mac without Docker.
# Java comparison: this is the same idea as
# ${DATABASE_URL:jdbc:sqlite:local.db} in a Spring application.yml -
# environment variable with a default fallback.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nervous_system_log.db")

# check_same_thread is a SQLite-only quirk; harmless to skip for
# Postgres, so we only apply it conditionally below.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a DB session and guarantees it's
    closed after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()