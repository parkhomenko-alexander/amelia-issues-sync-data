"""add nullable executor_id

Revision ID: 19bc9d73d7eb
Revises: 2094f27593d4
Create Date: 2024-03-13 15:45:52.856593

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19bc9d73d7eb'
down_revision: Union[str, None] = '2094f27593d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('issues', 'executor_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('issues', 'executor_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
