"""Configuration — provider + research budget."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RESEARCH_", env_file=".env", extra="ignore")

    # Synthesis provider: "extractive" (default, offline deterministic), "openai", "anthropic".
    provider: str = "extractive"
    model: str = "extractive-small"

    # Hard budget — the manager stops when either ceiling is hit.
    max_steps: int = 24  # total sub-agent calls
    max_searches: int = 6  # total corpus searches

    top_k: int = 3  # sources per search
    min_relevance: float = 0.12  # claim must share this fraction of question tokens


_CACHE: dict[str, Settings] = {}


def get_settings(name: str = "default") -> Settings:
    if name not in _CACHE:
        _CACHE[name] = Settings()
    return _CACHE[name]


def reset_settings(name: str = "default") -> None:
    _CACHE.pop(name, None)
