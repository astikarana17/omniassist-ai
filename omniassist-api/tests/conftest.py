"""Pytest fixtures."""
from __future__ import annotations

import os

import pytest

# Ensure test-safe settings before importing the app.
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-tests-1234567890")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/omniassist_test"
)
os.environ.setdefault(
    "DATABASE_SYNC_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/omniassist_test"
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c
