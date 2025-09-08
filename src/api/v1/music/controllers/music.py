from typing import Annotated
from fastapi import APIRouter, Depends, File, UploadFile, Form
from starlette import status

from src.api.v1.music.schemas.response import GetResultResponse, GetInfoResponse
from src.api.v1.music.services.music import MusicService
from src.api.v1.music.enums import ToolTypeEnum
from src.core.utils import BaseResponse

router = APIRouter(prefix="/music", tags=["Music"])

@router.get("/tools/{tool}/info", name="Get info")
async def info(
    service: Annotated[MusicService, Depends()],
    tool: ToolTypeEnum,
) -> BaseResponse[GetInfoResponse]:

    return BaseResponse(
        data=await service.get_info(tool=tool),
        code=status.HTTP_200_OK,
    )

@router.post("/convert/{tool}", name="Convert sheet music to MP3")
async def convert_music(
    service: Annotated[MusicService, Depends()],
    tool: ToolTypeEnum,
    file: UploadFile = File(...),
    tempo: int = 120,
    transpose: int = 0,
):
    """
    Single endpoint to return MP3 file with metadata in headers
    """

    return await service.convert(file=file, tool=tool, tempo=tempo, transpose=transpose)

@router.get("/tools/{tool}/results", name="Get results")
async def results(
    service: Annotated[MusicService, Depends()],
    tool: ToolTypeEnum,
) -> BaseResponse[GetResultResponse]:

    return BaseResponse(
        data=await service.get_results(tool=tool),
        code=status.HTTP_200_OK,
    )
