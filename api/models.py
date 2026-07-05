"""
ORM models.

Java comparison: each class below is your @Entity. The Column(...)
calls are your @Column annotations. ForeignKey(...) is @ManyToOne /
@JoinColumn. There's no @Table annotation needed - the __tablename__
class attribute does that job directly.

One real difference worth knowing for the interview: JPA/Hibernate
often does a lot of implicit magic (lazy loading proxies, dirty
checking, cascade behavior) based on annotations. SQLAlchemy can do
similar things, but it's generally more explicit - you'll see that
as we write queries later.

DESIGN NOTE ON THE REFERENCE TABLES:
Each lookup dimension (sensation location, trigger category, entry
type, origin, intensity, resolution) gets its own small reference
table, seeded via an Alembic migration - this is your Flyway-seeded
lookup table pattern. The `entries` table then has a foreign key into
each one, instead of storing free-text strings. That gives you
referential integrity (can't log a sensation_location that doesn't
exist) and makes the taxonomy editable via a migration instead of a
code change.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from api.database import Base


class ReferenceTableMixin:
    """
    Shared shape for every lookup table: a code (stable, used in code/API)
    and a label (human-readable, shown in CLI/UI).

    Java comparison: this is like an abstract @MappedSuperclass that
    EntryType, Origin, SensationLocation, etc. would all extend,
    factoring out the repeated id/code/label columns.
    """
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    label = Column(String(100), nullable=False)


class EntryType(Base, ReferenceTableMixin):
    __tablename__ = "entry_types"
    # values seeded: activation, completion, reparenting, reflection


class Origin(Base, ReferenceTableMixin):
    __tablename__ = "origins"
    # values seeded: thought, sensation, both, unclear


class SensationLocation(Base, ReferenceTableMixin):
    __tablename__ = "sensation_locations"
    # values seeded: chest, throat_neck_back, stomach, other


class Intensity(Base, ReferenceTableMixin):
    __tablename__ = "intensities"
    # values seeded: wave, storm


class TriggerCategory(Base, ReferenceTableMixin):
    __tablename__ = "trigger_categories"
    # values seeded: social_uncertainty, attachment_relevant, work,
    # unprompted_memory, other


class Resolution(Base, ReferenceTableMixin):
    __tablename__ = "resolutions"
    # values seeded: discharged, interrupted, ongoing


class Entry(Base):
    """
    The core table - one row per check-in / log entry.

    Java comparison: this is your main @Entity with several @ManyToOne
    relationships. Note we're using nullable=True on most foreign keys
    on purpose - a quick CLI check-in shouldn't force you to fill out
    every field (e.g. a 'reflection' entry might not have a sensation
    location at all).
    """
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True)

    entry_type_id = Column(Integer, ForeignKey("entry_types.id"), nullable=False)
    origin_id = Column(Integer, ForeignKey("origins.id"), nullable=True)
    sensation_location_id = Column(Integer, ForeignKey("sensation_locations.id"), nullable=True)
    intensity_id = Column(Integer, ForeignKey("intensities.id"), nullable=True)
    trigger_category_id = Column(Integer, ForeignKey("trigger_categories.id"), nullable=True)
    resolution_id = Column(Integer, ForeignKey("resolutions.id"), nullable=True)

    note = Column(Text, nullable=True)

    # server_default=func.now() means SQLite/Postgres sets this at
    # insert time - equivalent to @CreationTimestamp in Hibernate.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationship() gives you the Java-style navigable object graph
    # (entry.entry_type.label) instead of manually joining on the FK id.
    # This is your @ManyToOne mapping - lazy loading works similarly too.
    entry_type = relationship("EntryType")
    origin = relationship("Origin")
    sensation_location = relationship("SensationLocation")
    intensity = relationship("Intensity")
    trigger_category = relationship("TriggerCategory")
    resolution = relationship("Resolution")