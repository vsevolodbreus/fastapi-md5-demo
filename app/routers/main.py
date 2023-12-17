import uuid
from typing import Annotated

import aiofiles
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi import status as http_status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_session
from app.models import FileHash
from app.worker import get_file_md5_hash

templates = Jinja2Templates(directory="templates")

router = APIRouter(tags=["frontend", "webapp"])


@router.get("/", response_class=HTMLResponse, status_code=http_status.HTTP_200_OK)
async def root(request: Request):
    """Get root path"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/file", response_class=HTMLResponse, status_code=http_status.HTTP_200_OK)
def get_file_form(request: Request):
    """Get file form"""
    return templates.TemplateResponse("file.html", {"request": request})


@router.post(
    "/file",
    response_class=HTMLResponse,
    status_code=http_status.HTTP_200_OK,
)
async def process_file_form(
    request: Request,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    """Send form containing file to be hashed"""

    # Check if file is sent
    if not file.filename:
        return templates.TemplateResponse("file.html", {"request": request})

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

    return templates.TemplateResponse(
        "file.html", {"request": request, "res": file_hash}
    )


@router.get("/hash", response_class=HTMLResponse, status_code=http_status.HTTP_200_OK)
async def get_hash_form(request: Request):
    """Get hash look up form"""
    return templates.TemplateResponse("hash.html", {"request": request})


@router.post(
    "/hash",
    response_class=HTMLResponse,
    status_code=http_status.HTTP_200_OK,
)
async def process_hash_form(
    request: Request,
    req_id: Annotated[uuid.UUID, Form()],
    session: AsyncSession = Depends(get_session),
):
    """Retrieve hash from database by provided ID via form"""

    try:
        res = await FileHash.get(session=session, req_id=req_id)

    except NoResultFound:
        return templates.TemplateResponse(
            "hash.html", {"request": request, "res": {"md5_hash": "Hash not found!"}}
        )

    return templates.TemplateResponse("hash.html", {"request": request, "res": res})
