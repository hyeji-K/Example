"""Database session management and repositories."""

from __future__ import annotations

import os
import uuid
from datetime import date
from typing import Iterator

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.models import Base, Movie, UserDDay


def _database_url() -> str:
    """Return the SQLAlchemy URL from env (defaults to local SQLite for dev)."""
    settings = get_settings()
    # Handle postgresql:// vs postgres:// for SQLAlchemy compatibility
    url = settings.database_url
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


engine = create_engine(_database_url(), future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_models() -> None:
    """Create tables if they do not exist (handy for local dev)."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Iterator[Session]:
    """FastAPI-friendly dependency that manages commits/rollbacks."""

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

class DDayRepository:
    """High level data access helpers for personalized D-Day records."""

    def get_movie_by_source_and_id(
        self,
        session: Session,
        *,
        source: str | None,
        external_id: str | None,
    ) -> Movie | None:
        if not source or not external_id:
            return None
        query = select(Movie).where(
            Movie.source == source,
            Movie.external_id == external_id,
        )
        return session.execute(query).scalar_one_or_none()
        
    def get_movie_by_title(self, session: Session, title: str) -> Movie | None:
        query = select(Movie).where(Movie.title == title)
        return session.execute(query).scalar_one_or_none()

    def get_user_dday(
        self, session: Session, user_id: str, movie_id: uuid.UUID
    ) -> UserDDay | None:
        query = select(UserDDay).where(
            UserDDay.user_id == user_id,
            UserDDay.movie_id == movie_id,
        )
        return session.execute(query).scalar_one_or_none()

    def create_movie(
        self,
        session: Session,
        *,
        title: str,
        distributor: str | None,
        release_date: date,
        director: str | None,
        cast: str | None,
        genre: str | None,
        poster_url: str | None,
        source: str | None,
        external_id: str | None,
        is_re_release: bool,
        content_type: str,
    ) -> Movie:
        movie = Movie(
            title=title,
            distributor=distributor,
            release_date=release_date,
            director=director,
            cast=cast,
            genre=genre,
            poster_url=poster_url,
            source=source,
            external_id=external_id,
            is_re_release=is_re_release,
            content_type=content_type,
        )
        session.add(movie)
        session.flush()
        return movie

    def create_user_dday(
        self,
        session: Session,
        *,
        user_id: str,
        movie_id: uuid.UUID,
        query_name: str,
        dday_label: str,
    ) -> UserDDay:
        user_dday = UserDDay(
            user_id=user_id,
            movie_id=movie_id,
            query_name=query_name,
            dday_label=dday_label,
        )
        session.add(user_dday)
        session.flush()
        session.refresh(user_dday)
        return user_dday

    def list_user_ddays(self, session: Session, user_id: str) -> list[tuple[UserDDay, Movie]]:
        """Returns the user's D-Days joined with the Movie metadata."""
        query = (
            select(UserDDay, Movie)
            .join(Movie, UserDDay.movie_id == Movie.id)
            .where(UserDDay.user_id == user_id)
            .order_by(Movie.release_date)
        )
        return list(session.execute(query).all())
        
    def count_waiting_users(self, session: Session, movie_id: uuid.UUID) -> int:
        """Returns the total number of users waiting for this specific movie."""
        query = select(func.count(UserDDay.id)).where(UserDDay.movie_id == movie_id)
        return session.execute(query).scalar_one()
