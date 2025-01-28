"""add id_autoincrement

Revision ID: 88a6078b9c85
Revises: 4a3bfc7322b1
Create Date: 2025-01-26 17:12:18.552285

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88a6078b9c85'
down_revision: Union[str, None] = '4a3bfc7322b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('page_processed_data', sa.Column('id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_page_processed_data_id'), 'page_processed_data', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_page_processed_data_id'), table_name='page_processed_data')
    op.drop_column('page_processed_data', 'id')
    # ### end Alembic commands ###
