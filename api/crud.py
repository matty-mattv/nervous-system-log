"""
Data access layer - the Repository equivalent.

Java comparison: in Spring Data JPA, you'd declare an interface like
`EntryRepository extends JpaRepository<Entry, Long>` and Spring
generates the implementation (findById, save, etc.) for you at
runtime via proxies. SQLAlchemy has no equivalent auto-generation -
every query function here is hand-written. More typing, but nothing
hidden: every SQL-generating call is visible Python code.
"""

from sqlalchemy.orm import Session

from api import models, schemas


def get_reference_id(db: Session, table_model, code: str):
    """
    Look up the numeric primary key for a reference table row given
    its code (e.g. "chest" -> 1).

    Java comparison: this is roughly what a
    `sensationLocationRepository.findByCode("chest")` call would do
    in a Spring Data JPA repository - a single lookup by a unique
    non-id column.
    """
    if code is None:
        return None
    row = db.query(table_model).filter(table_model.code == code).first()
    if row is None:
        raise ValueError(f"Unknown {table_model.__tablename__} code: '{code}'")
    return row.id


def create_entry(db: Session, entry_in: schemas.EntryCreate) -> models.Entry:
    """
    Translate an EntryCreate (codes) into an Entry row (foreign key
    IDs), save it, and return the saved row.

    Java comparison: this is your Service layer method - the thing
    that would sit between your @RestController and your
    @Repository, doing the actual business logic (here: resolving
    codes to IDs) before persisting.
    """
    entry = models.Entry(
        entry_type_id=get_reference_id(db, models.EntryType, entry_in.entry_type),
        origin_id=get_reference_id(db, models.Origin, entry_in.origin),
        sensation_location_id=get_reference_id(db, models.SensationLocation, entry_in.sensation_location),
        intensity_id=get_reference_id(db, models.Intensity, entry_in.intensity),
        trigger_category_id=get_reference_id(db, models.TriggerCategory, entry_in.trigger_category),
        resolution_id=get_reference_id(db, models.Resolution, entry_in.resolution),
        note=entry_in.note,
    )
    db.add(entry)      # stage the insert - like calling save() before commit
    db.commit()         # actually write to the DB - like a transaction commit
    db.refresh(entry)   # pull back DB-generated values (id, created_at)
    return entry


def get_entries(db: Session, limit: int = 50):
    """
    Fetch recent entries, most recent first.

    Java comparison: `entryRepository.findAllByOrderByCreatedAtDesc(Pageable)`
    """
    return (
        db.query(models.Entry)
        .order_by(models.Entry.created_at.desc())
        .limit(limit)
        .all()
    )

def entry_to_response(entry: models.Entry) -> schemas.EntryResponse:
    """
    Explicit mapping from the ORM entity (nested relationship objects)
    to the flat API response schema.

    Java comparison: this is your mapper method - e.g. what a
    MapStruct-generated class or a hand-written EntryMapper would do,
    pulling entity.getResolution().getCode() instead of exposing the
    nested @ManyToOne object directly.
    """
    return schemas.EntryResponse(
        id=entry.id,
        entry_type=entry.entry_type.code,
        origin=entry.origin.code if entry.origin else None,
        sensation_location=entry.sensation_location.code if entry.sensation_location else None,
        intensity=entry.intensity.code if entry.intensity else None,
        trigger_category=entry.trigger_category.code if entry.trigger_category else None,
        resolution=entry.resolution.code if entry.resolution else None,
        note=entry.note,
        created_at=entry.created_at,
    )