"""empty message

Revision ID: 7fe41c1faa64
Revises: 597a86f9da94
Create Date: 2024-12-18 10:41:18.085335

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fe41c1faa64'
down_revision: Union[str, None] = '597a86f9da94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('issues', sa.Column('urgency', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('issues', 'urgency')
    # ### end Alembic commands ###
