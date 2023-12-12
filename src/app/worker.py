import datetime
import os
import uuid

from celery import Celery, Task
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.scoping import ScopedSession

from app.config import settings
from app.logger import logger
from app.models import FileHash
from app.utils import get_md5_hash

app = Celery(settings.CELERY_APP or __name__)
app.conf.broker_url = settings.CELERY_BROKER_URL
app.conf.result_backend = settings.CELERY_BACKEND_URL
app.conf.database_engine_options = {"echo": settings.CELERY_DB_VERBOSE}
app.conf.broker_connection_retry_on_startup = (
    settings.CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP
)
app.conf.task_routes = {"worker.*": {"queue": settings.CELERY_QUEUE}}

engine = create_engine(settings.POSTGRES_DB_URL)


class DBTask(Task):
    _session: ScopedSession = None

    def after_return(self, *args, **kwargs):
        if self._session is not None:
            self._session.remove()

    @property
    def session(self):
        if self._session is None:
            self._session = scoped_session(
                sessionmaker(autocommit=False, expire_on_commit=False, bind=engine)
            )

        return self._session


@app.task(base=DBTask, name="get_file_md5_hash", bind=True)
def get_file_md5_hash(self, file_name: str, req_id: uuid.UUID):
    """Celery task to hash file"""

    # Calculate hash
    md5_hash = get_md5_hash(f"{settings.INPUT_FILE_DIR}/{req_id}_{file_name}")

    # Log result in shared file
    with logger.contextualize(
        req_id=str(req_id),
        worker=settings.CELERY_APP or __name__,
        md5_hash=md5_hash,
        file_name=file_name,
    ):
        logger.info("logging file hash")

    # Update database
    FileHash.mark_as_processed(
        session=self.session,
        req_id=req_id,
        md5_hash=md5_hash,
        processed_at=datetime.datetime.now(),
    )

    # Delete file
    os.remove(f"{settings.INPUT_FILE_DIR}/{req_id}_{file_name}")

    return md5_hash
