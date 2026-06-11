"""Create a demo login user in the seeded `tcs` org so the UI can be tested.

Usage:  python -m scripts.seed_demo_user
Credentials printed at the end.
"""
from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import text

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password

EMAIL = "demo@tcs.com"
PASSWORD = "Tcs@2026!"
FULL_NAME = "TCS Demo Admin"
ROLE = "admin"


async def main() -> None:
    async with AsyncSessionLocal() as db:
        org_id = (
            await db.execute(text("select id from organizations where slug='tcs'"))
        ).scalar_one()

        # Idempotent: remove any prior demo user (memberships cascade).
        await db.execute(text("delete from users where email=:e"), {"e": EMAIL})

        user_id = uuid.uuid4()
        await db.execute(
            text(
                "insert into users(id, email, full_name, hashed_password, auth_provider, "
                "is_active, is_email_verified, is_superuser, mfa_enabled) values "
                "(:id,:email,:name,:pw,'email',true,true,false,false)"
            ),
            {"id": user_id, "email": EMAIL, "name": FULL_NAME, "pw": hash_password(PASSWORD)},
        )
        await db.execute(
            text(
                "insert into memberships(id, org_id, user_id, role, status) values "
                "(:id,:org,:uid,:role,'active')"
            ),
            {"id": uuid.uuid4(), "org": org_id, "uid": user_id, "role": ROLE},
        )
        await db.commit()

    print("=== Demo user ready ===")
    print(f"  Email:    {EMAIL}")
    print(f"  Password: {PASSWORD}")
    print(f"  Org:      Tata Consultancy Services  | Role: {ROLE}")


if __name__ == "__main__":
    asyncio.run(main())
