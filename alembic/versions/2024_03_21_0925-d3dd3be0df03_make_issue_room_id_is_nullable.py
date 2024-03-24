"""make issue room_id is nullable

Revision ID: d3dd3be0df03
Revises: 7c23bb3fb3ff
Create Date: 2024-03-21 09:25:21.069882

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3dd3be0df03'
down_revision: Union[str, None] = '7c23bb3fb3ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('issues', 'room_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('issues', 'room_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
