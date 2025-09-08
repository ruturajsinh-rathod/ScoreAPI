import time
import shutil
import subprocess
from pathlib import Path
import os
from music21 import converter, tempo
from pdf2image import convert_from_path
from concurrent.futures import ThreadPoolExecutor
import sys

# Disable GPU
os.environ["CUDA_VISIBLE_DEVICES"] = ""

ROOT_DIR = Path("/home/mind/Desktop/fastapi-demo-app/ScoreAPI")
OUTPUT_DIR = ROOT_DIR / "output"
IMG_DIR = OUTPUT_DIR / "images"

def prepare_image_dir():
    if IMG_DIR.exists():
        shutil.rmtree(IMG_DIR)
    IMG_DIR.mkdir(parents=True)

def pdf_to_images(pdf_path: Path):
    images = convert_from_path(str(pdf_path), dpi=300)
    img_paths = []
    for i, img in enumerate(images, start=1):
        img_path = IMG_DIR / f"page_{i}.png"
        img.save(img_path, "PNG")
        img_paths.append(img_path)
    return img_paths

def run_homr(img_path: Path) -> Path:
    print(f"🎵 Running HOMR on: {img_path.name}")
    result = subprocess.run(
        [sys.executable, "-m", "homr.main", str(img_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"HOMR failed for {img_path.name}: {result.stderr}")

    xml_path = img_path.with_suffix(".musicxml")
    if not xml_path.exists():
        raise FileNotFoundError(f"MusicXML not found for: {img_path.name}")
    print(f"✅ HOMR done: {img_path.name}")
    return xml_path

def xml_to_midi_mp3(xml_path: Path, sf2_path: Path, bpm: int, transpose_interval: int = 0) -> Path:
    midi = xml_path.with_suffix(".mid")
    wav = xml_path.with_suffix(".wav")
    mp3 = xml_path.with_suffix(".mp3")

    print(f"🎶 Converting to MP3: {xml_path.name}")
    # MusicXML → MIDI
    score = converter.parse(str(xml_path))
    score.insert(0, tempo.MetronomeMark(number=bpm))

    # --- Transpose the score if needed ---

    if transpose_interval != 0:
        score = score.transpose(transpose_interval)

    score.write("midi", fp=str(midi))

    # MIDI → WAV
    subprocess.run(["fluidsynth", "-ni", str(sf2_path), str(midi), "-F", str(wav)], check=True)
    # WAV → MP3
    subprocess.run(["ffmpeg", "-y", "-i", str(wav), str(mp3)], check=True)
    print(f"🟢 Done MP3: {xml_path.name}")

    return mp3

def merge_mp3s(mp3_files: list[Path], output_path: Path):
    concat_file = output_path.with_suffix(".txt")
    with open(concat_file, "w") as f:
        for mp3 in mp3_files:
            f.write(f"file '{mp3.resolve()}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file), "-c", "copy", str(output_path)
    ], check=True)
    concat_file.unlink()

def main(pdf_path: Path, sf2_path: Path, bpm: int = 120, max_workers: int = 4, transpose_interval: int = 0):
    start_time = time.time()
    prepare_image_dir()
    img_paths = pdf_to_images(pdf_path)

    # --- Run HOMR sequentially to avoid deadlocks ---
    xml_paths = []
    for img in img_paths:
        try:
            xml = run_homr(img)
            xml_paths.append(xml)
        except Exception as e:
            print(f"⚠️ Error HOMR {img.name}: {e}")

    if not xml_paths:
        print("❌ No MusicXMLs generated. Exiting.")
        return

    # --- Convert MusicXML → MP3 in parallel using threads ---
    mp3_files = []
    def worker(xml):
        try:
            return xml_to_midi_mp3(xml, sf2_path, bpm, transpose_interval=transpose_interval)
        except Exception as e:
            print(f"⚠️ Error converting {xml.name}: {e}")
            return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(worker, xml_paths))
    mp3_files = [f for f in results if f is not None]

    if mp3_files:
        merged = OUTPUT_DIR / f"{pdf_path.stem}_merged.mp3"
        merge_mp3s(mp3_files, merged)
        print(f"✅ Merged MP3 saved to: {merged}")
    else:
        print("❌ No MP3s generated.")

    print(f"⏱️ Total time: {time.time() - start_time:.2f} sec")
