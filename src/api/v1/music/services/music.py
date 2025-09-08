import json
import shutil
from pathlib import Path

from fastapi import UploadFile
from fastapi.responses import StreamingResponse

from src.api.v1.music.enums import ToolTypeEnum
from src.api.v1.music.schemas.response import GetInfoResponse, GetResultResponse


class MusicService:

    async def get_info(self, tool: ToolTypeEnum) -> GetInfoResponse:
        match tool:
            case ToolTypeEnum.AUDIVERIS:
                return GetInfoResponse(
                    note="Audiveris is best with clean, printed PDFs. Not recommended for handwriting or phone pictures."
                )
            case ToolTypeEnum.HOMR:
                return GetInfoResponse(
                    note="HOMR is best with handwritten notes, sketches, or informal lead sheets."
                )
            case ToolTypeEnum.OEMER:
                return GetInfoResponse(
                    note="OEMER is best with scanned pages or mobile photos of simple sheet music."
                )

    async def convert(
        self, file: UploadFile, tool: ToolTypeEnum, tempo: int = 160, transpose: int = 0
    ):
        # Create input/output dirs
        input_dir = Path("input")
        # output_dir = Path("output")
        input_dir.mkdir(exist_ok=True)
        # output_dir.mkdir(exist_ok=True)

        ROOT_DIR = Path("/home/mind/Desktop/fastapi-demo-app/ScoreAPI")
        output_dir = ROOT_DIR / "output"

        # Clear the output folder
        if output_dir.exists():
            shutil.rmtree(output_dir)

        # Recreate the empty folder
        output_dir.mkdir(parents=True, exist_ok=True)

        # Safe filename
        filename = Path(file.filename or "uploaded_file.pdf").name
        input_path = input_dir / filename

        # Save uploaded file
        with open(input_path, "wb") as f:
            f.write(await file.read())

        SOUNDFONT_PATH = Path(
            "/home/mind/Downloads/twinkle-twinkle-little-star-piano-solo.sf2"
        )

        try:
            if tool == "AUDIVERIS":
                from .audiveris import process_input

                # ✅ Only pass 2 arguments (input and output)
                process_input(
                    input_file=input_path,
                    output_dir=output_dir,
                    bpm=tempo,
                    transpose_interval=transpose,
                )

                mp3_path = output_dir / input_path.stem / f"{input_path.stem}.mp3"

                meta = {"processingTime": "~18–20 sec/page", "accuracy": "85–95%"}

            elif tool == "HOMR":
                from .homr import main

                main(
                    input_path, SOUNDFONT_PATH, bpm=tempo, transpose_interval=transpose
                )
                mp3_path = output_dir / f"{input_path.stem}_merged.mp3"

                meta = {"processingTime": "~60–80 sec/image", "accuracy": "70–85%"}

            elif tool == "OEMER":
                from src.api.v1.music.services import oemer

                oemer.main(
                    input_path, SOUNDFONT_PATH, transpose_interval=transpose, bpm=tempo
                )
                mp3_path = Path("output") / f"{input_path.stem}_merged.mp3"

                meta = {"processingTime": "~160–170 sec/image", "accuracy": "60–70%"}

            else:
                raise ValueError("Unsupported tool")

            if not mp3_path.exists():
                raise FileNotFoundError("MP3 not created")

            # Return MP3 directly with metadata in headers
            return StreamingResponse(
                open(mp3_path, "rb"),
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": f"attachment; filename={mp3_path.name}",
                    "X-Tool": tool,
                    "X-Meta": json.dumps(meta),
                },
            )

        except Exception as e:
            raise RuntimeError(f"Conversion failed: {str(e)}")

    async def get_results(self, tool: ToolTypeEnum) -> GetResultResponse:
        match tool:
            case ToolTypeEnum.AUDIVERIS:
                return GetResultResponse(
                    pros=[
                        "Works great with clean, printed sheet music",
                        "Can handle full-length music books or multiple pages",
                        "Keeps details like lyrics, notes, and rhythms",
                    ],
                    cons=[
                        "Takes more time than some tools",
                        "Needs good quality PDFs for best results",
                        "May be tricky to set up without help",
                    ],
                    accuracy="85–95% (best with clear prints)",
                    processing_time="~18-20 sec/page",
                )
            case ToolTypeEnum.HOMR:
                return GetResultResponse(
                    pros=[
                        "Great for handwritten music sheets",
                        "Fast and easy to try out",
                        "Doesn't need big software installations",
                    ],
                    cons=[
                        "Might miss some musical details",
                        "Still in testing — not for professional use yet",
                    ],
                    accuracy="70–85% (best with handwritten scores)",
                    processing_time="~60–80 sec/image",
                )
            case ToolTypeEnum.OEMER:
                return GetResultResponse(
                    pros=[
                        "Uses smart AI to read music directly from images",
                        "Works well with clean scans or phone pictures",
                    ],
                    cons=[
                        "May skip over advanced music symbols"
                        "Works better with simple, single-instrument music",
                        "Slower than other tools for large or messy files",
                        "Unclear or low-quality sheet music can introduce extra noise or timing discrepancies in the output.",
                    ],
                    accuracy="60–70% (best with simple scores)",
                    processing_time="~160–170 sec/image without GPU",
                )
