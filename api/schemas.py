"""
Pydantic schemas - the request/response contract layer.

Java comparison: these are your DTOs. In Spring Boot you'd typically
hand-write a separate DTO class (or use a mapper like MapStruct) to
avoid exposing your @Entity directly over the API. Pydantic plays
that same role here - schemas.py never touches the database directly,
models.py never gets serialized directly to JSON.

Bean Validation comparison: where Java uses annotations like
@NotNull, @Size(max=100) on DTO fields, Pydantic uses type hints
plus its own validation - str vs Optional[str], for example - and
raises a 422 automatically on violation, similar to how a Spring
@Valid failure produces a 400 with field errors.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EntryCreate(BaseModel):
    """
    Shape of an incoming POST /entries request body.

    Note: this uses the *codes* (e.g. "chest", "wave") rather than
    numeric IDs - the CLI and any future client should never need to
    know the database's internal integer IDs. The API layer will look
    up the actual foreign key IDs from these codes.
    """
    entry_type: str
    origin: Optional[str] = None
    sensation_location: Optional[str] = None
    intensity: Optional[str] = None
    trigger_category: Optional[str] = None
    resolution: Optional[str] = None
    note: Optional[str] = None


class EntryResponse(BaseModel):
    """
    Shape of an entry returned from the API - what the CLI/client
    actually receives back.
    """
    id: int
    entry_type: str
    origin: Optional[str] = None
    sensation_location: Optional[str] = None
    intensity: Optional[str] = None
    trigger_category: Optional[str] = None
    resolution: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime

    # Java comparison: this tells Pydantic it's allowed to read
    # attributes off an ORM object directly (entry.entry_type.label,
    # etc.) rather than only accepting plain dicts - similar in spirit
    # to a mapper reading getters off your @Entity to build a DTO.
    model_config = ConfigDict(from_attributes=True)