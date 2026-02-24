"""SQLAlchemy ORM models.

This module defines the "projects" table which stores the shared D-Day
records. Keeping it isolated here makes future Alembic migrations simpler.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Movie(Base):
    """Represents a movie/TV series metadata entry cached from TMDb."""

    __tablename__ = "movies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String(255))
    distributor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    release_date: Mapped[date] = mapped_column(Date, index=True)
    director: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cast: Mapped[str | None] = mapped_column(Text, nullable=True)
    genre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    poster_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(128))
    is_re_release: Mapped[bool] = mapped_column(Boolean, default=False)
    content_type: Mapped[str] = mapped_column(String(32), default="movie")
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_movies_source_external"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"Movie(id={self.id}, title={self.title}, release_date={self.release_date})"


from sqlalchemy import ForeignKey


class UserDDay(Base):
    """Maps a user to their personal D-Day tracking of a specific movie.
    Also tracks the custom name query they used to find it.
    """

    __tablename__ = "user_ddays"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    movie_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("movies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    query_name: Mapped[str] = mapped_column(String(255))
    dday_label: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie_dday"),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"UserDDay(user_id={self.user_id}, movie_id={self.movie_id})"
