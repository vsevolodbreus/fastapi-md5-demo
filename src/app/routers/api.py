import uuid
from importlib.metadata import distribution

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi import status as http_status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_session
from app.models import FileHash
from app.schemas import FileHashSchema
from app.worker import get_file_md5_hash

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/", response_class=JSONResponse, status_code=http_status.HTTP_200_OK)
async def index():
    return {
        "service": "MD5 File Hash API",
        "version": distribution("app").version,
    }


@router.post(
    "/file",
    response_class=JSONResponse,
    response_model=FileHashSchema,
    status_code=http_status.HTTP_201_CREATED,
)
async def send_form(
    request: Request,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    """Send form containing file to be hashed"""

    # Check if file is sent
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file sent")

    # Generate ID
    req_id = uuid.uuid4()

    # Save file to local tmp folder
    async with aiofiles.open(
        f"{settings.INPUT_FILE_DIR}/{req_id}_{file.filename}", "wb"
    ) as out_file:
        while content := await file.read(1024):
            await out_file.write(content)

    # Create a db entry
    file_hash = await FileHash.create(
        session=session, req_id=req_id, file_name=file.filename
    )

    # Send task to Celery queue
    get_file_md5_hash.apply_async(
        args=(file.filename, req_id), queue=settings.CELERY_QUEUE
    )

    return file_hash


@router.get(
    "/hash/{req_id}",
    response_class=JSONResponse,
    response_model=FileHashSchema,
    status_code=http_status.HTTP_200_OK,
)
async def get_hash(req_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    """Retrieve hash from database by provided ID"""

    try:
        return await FileHash.get(session=session, req_id=req_id)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="The requested ID was not found")
