"""seed initial user

Revision ID: 0b136f33f1df
Revises: 6419eace36e5
Create Date: 2026-05-28 10:36:57.216968

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from core.security import SecurityInstance

# revision identifiers, used by Alembic.
revision: str = '0b136f33f1df'
down_revision: Union[str, Sequence[str], None] = '6419eace36e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()


    hashed_pw = SecurityInstance.hash_password("test123!@#")

    conn.execute(sa.text("""
        INSERT INTO users (email, first_name, last_name, hashed_password, created_at, updated_at)
        VALUES (:email, :first_name, :last_name, :hashed_password, NOW(), NOW())
    """), {"email": "thebackdoors182@gmail.com", "first_name": "Patrick", "last_name": "Tester", "hashed_password": hashed_pw})


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM users WHERE email = :email"), {"email": "thebackdoors182@gmail.com"})
