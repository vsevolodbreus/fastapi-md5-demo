import datetime
import uuid
from typing import Optional

import sqlalchemy.dialects.postgresql as psql
from sqlalchemy import Boolean, DateTime, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.scoping import ScopedSession

from .db import Base


class FileHash(Base):
    """Data model for table that stores MD5 file hashes"""

    __tablename__ = "file_hash"

    # ID to access the hash
    req_id: Mapped[uuid.UUID] = mapped_column(
        psql.UUID, primary_key=True, nullable=False, index=True, unique=True
    )

    # File Name
    file_name: Mapped[str]

    # MD5 file hash
    md5_hash: Mapped[str] = None

    # Whether the file hash has been calculated
    processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # When the request was received
    received_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )

    # When the request was processed
    processed_at: Mapped[datetime.datetime] = None

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> "FileHash":
        """Create a record in the database of a file hash"""
        file_hash = cls(**kwargs)
        session.add(file_hash)
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e

        await session.refresh(file_hash)

        return file_hash

    @classmethod
    async def get(
        cls, session: AsyncSession, req_id: uuid.UUID
    ) -> Optional["FileHash"]:
        """Retrieve a record from the database"""
        try:
            file_hash = (
                await session.execute(select(cls).where(cls.req_id == req_id))
            ).scalar_one()

        except Exception as e:
            raise e

        return file_hash

    @classmethod
    def mark_as_processed(
        cls,
        session: ScopedSession,
        req_id: uuid.UUID,
        md5_hash: str,
        processed_at: datetime.datetime,
    ) -> None:
        """Update the record in the database as processed"""
        update_stmt = (
            update(cls)
            .where(cls.req_id == req_id)
            .values(processed=True, md5_hash=md5_hash, processed_at=processed_at)
        )

        try:
            session.execute(update_stmt)
            session.commit()

        except Exception as e:
            session.rollback()
            raise e
