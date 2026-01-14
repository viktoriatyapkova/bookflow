"""Update books and library

Revision ID: 002_update_books_library
Revises: 001_initial
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_update_books_library'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add ISBN column to books
    op.add_column('books', sa.Column('isbn', sa.String(), nullable=True))
    op.create_index('ix_books_isbn', 'books', ['isbn'], unique=True)
    
    # Make file_path nullable
    op.alter_column('books', 'file_path', nullable=True)
    
    # Add added_at to user_books
    op.add_column('user_books', sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True))
    
    # Add unique constraint to user_books (user_id, book_id)
    op.create_unique_constraint('uq_user_book', 'user_books', ['user_id', 'book_id'])


def downgrade() -> None:
    # Remove unique constraint
    op.drop_constraint('uq_user_book', 'user_books', type_='unique')
    
    # Remove added_at
    op.drop_column('user_books', 'added_at')
    
    # Make file_path not nullable
    op.alter_column('books', 'file_path', nullable=False)
    
    # Remove ISBN
    op.drop_index('ix_books_isbn', table_name='books')
    op.drop_column('books', 'isbn')


