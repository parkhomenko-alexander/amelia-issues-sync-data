"""make issue foreign service_id reffer service external_id

Revision ID: 59bb6bdf153c
Revises: 91c958b27059
Create Date: 2024-03-13 17:35:55.920070

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59bb6bdf153c'
down_revision: Union[str, None] = '91c958b27059'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('issues_service_id_fkey', 'issues', type_='foreignkey')
    op.create_foreign_key(None, 'issues', 'services', ['service_id'], ['external_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'issues', type_='foreignkey')
    op.create_foreign_key('issues_service_id_fkey', 'issues', 'services', ['service_id'], ['id'])
    # ### end Alembic commands ###
