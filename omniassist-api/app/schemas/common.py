"""Shared response envelope and pagination schemas."""
from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: object | None = None


class Envelope(BaseModel, Generic[T]):
    data: T | None = None
    error: ErrorDetail | None = None


class PageMeta(BaseModel):
    total: int
    limit: int
    offset: int
    has_more: bool


class Page(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str
