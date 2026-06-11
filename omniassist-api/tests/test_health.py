"""Smoke tests for system endpoints and the error envelope."""
from __future__ import annotations


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["version"] == "1.0.0"


def test_rbac_matrix_endpoint(client):
    resp = client.get("/api/v1/rbac/matrix")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "super_admin" in data
    assert "viewer" in data


def test_protected_route_requires_auth(client):
    resp = client.get("/api/v1/conversations")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] in ("AUTH_REQUIRED",)


def test_security_headers_present(client):
    resp = client.get("/healthz")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert "X-Request-ID" in resp.headers
