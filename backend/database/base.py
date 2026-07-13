"""
SQLAlchemy declarative Base used by all ORM models.
"""

from sqlalchemy.orm import DeclarativeBase, MappedColumn
from sqlalchemy import DateTime, func
from datetime import datetime


class Base(DeclarativeBase):
    """Common base for all AMHABINGO models."""

    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }
