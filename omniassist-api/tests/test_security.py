"""Unit tests for security primitives."""
from __future__ import annotations

from cryptography.fernet import Fernet

from app.core import security


def test_password_hash_and_verify():
    hashed = security.hash_password("S3curePass!")
    assert hashed != "S3curePass!"
    assert security.verify_password("S3curePass!", hashed)
    assert not security.verify_password("wrong", hashed)


def test_access_token_roundtrip():
    token = security.create_access_token("user-1", org_id="org-1", role="admin")
    payload = security.decode_token(token, expected_type="access")
    assert payload["sub"] == "user-1"
    assert payload["org_id"] == "org-1"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"


def test_refresh_token_has_jti_and_expiry():
    token, jti, expires = security.create_refresh_token("user-2")
    payload = security.decode_token(token, expected_type="refresh")
    assert payload["jti"] == jti
    assert expires is not None


def test_wrong_token_type_rejected():
    import pytest

    from app.core.exceptions import AuthenticationError

    access = security.create_access_token("u", org_id="o", role="viewer")
    with pytest.raises(AuthenticationError):
        security.decode_token(access, expected_type="refresh")


def test_token_hashing_is_deterministic():
    raw = security.generate_token()
    assert security.hash_token(raw) == security.hash_token(raw)
    assert security.hash_token(raw) != raw


def test_field_encryption_roundtrip(monkeypatch):
    monkeypatch.setattr(security.settings, "ENCRYPTION_KEY", Fernet.generate_key().decode())
    ciphertext = security.encrypt_value("super-secret-token")
    assert ciphertext != "super-secret-token"
    assert security.decrypt_value(ciphertext) == "super-secret-token"
