"""Service helpers for D-Day orchestration."""

from __future__ import annotations

import json
import logging
from datetime import date
from typing import Any

from openai import OpenAI

from app.core.config import get_settings
from app.services.models import MovieData
from app.services.tmdb import TMDbClient


def calculate_dday_label(release_date: date, *, today: date | None = None) -> str:
    """Return the canonical D-Day label (D-10/D-DAY/D+5)."""

    today = today or date.today()
    delta = (release_date - today).days
    if delta > 0:
        return f"D-{delta}"
    if delta == 0:
        return "D-DAY"
    return f"D+{abs(delta)}"


def build_project_params(
    *, project_name: str, movie: MovieData, today: date | None = None
) -> dict:
    """Create kwargs for ProjectRepository.create from movie data."""

    return {
        "name": project_name,
        "movie_title": movie.title,
        "distributor": movie.distributor,
        "release_date": movie.release_date,
        "director": movie.director,
        "cast": movie.cast_as_string(),
        "genre": movie.genre_as_string(),
        "dday_label": calculate_dday_label(movie.release_date, today=today),
        "source": movie.source,
        "external_id": movie.external_id,
        "is_re_release": movie.is_re_release,
    }


def orchestrate_movie_lookup(user_query: str) -> MovieData:
    """Use OpenAI + TMDb tool-calling flow to fetch movie metadata."""

    settings = get_settings()
    tmdb_client = TMDbClient()
    client = _get_openai_client(settings.openai_api_key)

    if client is None:
        return tmdb_client.search_movie(title=user_query)

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": _SYSTEM_PROMPT,
                },
                {"role": "user", "content": user_query},
            ],
            tools=_TOOLS,
            tool_choice="auto",
        )
    except Exception as exc:  # pragma: no cover - network failure
        logger.warning("OpenAI call failed, falling back to direct TMDb lookup: %s", exc)
        return tmdb_client.search_movie(title=user_query)

    tool_call = _extract_movie_tool_call(response)
    args = _parse_tool_arguments(tool_call) if tool_call else {}
    return tmdb_client.search_movie(
        title=args.get("title") or user_query,
        year=args.get("year"),
        language=args.get("language"),
        region=args.get("country") or settings.tmdb_region,
    )


logger = logging.getLogger(__name__)
_openai_client: OpenAI | None = None
_SYSTEM_PROMPT = (
    "You help users coordinate shared movie release D-Days. "
    "Always normalize the movie title (fix missing spaces like '28년후' -> '28년 후',"
    " correct casing, prefer official Korean titles) before calling the movie_search"
    " tool, and always call that tool before answering."
)
_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "movie_search",
            "description": "Search TMDb for a movie release date and metadata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Movie title to search for",
                    },
                    "year": {
                        "type": "integer",
                        "description": "Optional release year for disambiguation",
                    },
                    "country": {
                        "type": "string",
                        "description": "ISO country code (KR, US, etc.)",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language/locale hint (ko-KR, en-US)",
                    },
                },
                "required": ["title"],
            },
        },
    }
]


def _get_openai_client(api_key: str | None) -> OpenAI | None:
    global _openai_client
    if not api_key:
        return None
    if _openai_client is None:
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client


def _extract_movie_tool_call(response: Any) -> Any:
    try:
        choice = response.choices[0]
        message = choice.message
        tool_calls = getattr(message, "tool_calls", None) or []
    except (AttributeError, IndexError):
        return None
    for call in tool_calls:
        if call.function.name == "movie_search":
            return call
    return None


def _parse_tool_arguments(tool_call: Any) -> dict[str, Any]:
    if not tool_call:
        return {}
    try:
        return json.loads(tool_call.function.arguments or "{}")
    except json.JSONDecodeError:
        logger.warning("Failed to parse tool arguments: %s", tool_call.function.arguments)
        return {}
