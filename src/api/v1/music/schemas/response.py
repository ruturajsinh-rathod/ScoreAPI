from typing import Optional, List

from src.core.utils import CamelCaseModel


class GetResultResponse(CamelCaseModel):
    processing_time: str
    accuracy: str
    pros: List[str]
    cons: List[str]


class MusicResponse(CamelCaseModel):
    msg: str
    filename: Optional[str]
    size_bytes: int
    tool: str
    mp3_base64: Optional[str]


class GetInfoResponse(CamelCaseModel):
    note: str
