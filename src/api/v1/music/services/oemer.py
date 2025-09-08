import shutil
import subprocess
from pathlib import Path
from pdf2image import convert_from_path
from multiprocessing import Pool, cpu_count
from music21 import converter, tempo, midi

def run_oemer(img_path: Path, out_dir: Path):
    cmd = ["oemer", str(img_path), "-o", str(out_dir)]
    subprocess.run(cmd, check=True)

def merge_mp3s(mp3_files: list[Path], output_path: Path):
    concat_file = output_path.with_suffix(".txt")
    with open(concat_file, "w") as f:
        for mp3 in mp3_files:
            f.write(f"file '{mp3.resolve()}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(output_path)
    ], check=True)
    concat_file.unlink()

def convert_pdf_parallel(pdf: Path, out_dir: Path):
    pages = convert_from_path(str(pdf), dpi=300)
    args = []

    for i, page in enumerate(pages, start=1):
        img = out_dir / f"{pdf.stem}_pg{i}.png"
        page.save(img, "PNG")
        args.append((img, out_dir))

    # Run OEMER on all pages in parallel
    with Pool(cpu_count()) as pool:
        pool.starmap(run_oemer, args)

def musicxml_to_midi_and_mp3(xml_path: Path, out_dir: Path, sf2: Path, transpose_interval: int = 0, tempo_bpm: int = 120):
    try:
        score = converter.parse(str(xml_path))

        # Remove all tempo marks
        for el in score.recurse().getElementsByClass("MetronomeMark"):
            el.activeSite.remove(el)
        score.insert(0, tempo.MetronomeMark(number=tempo_bpm))

        # Transpose if needed
        if transpose_interval != 0:
            print(transpose_interval)
            score = score.transpose(transpose_interval)

        # Flatten to avoid part overlaps
        score = score.flatten()

        # 🔍 Extract note times
        note_offsets = [n.offset for n in score.recurse().notes]
        if not note_offsets:
            print(f"⚠️ No notes found in {xml_path.name}")
            return

        start_time = min(note_offsets)
        end_time = max(note_offsets)

        # Clamp very long note durations
        for n in score.recurse().notes:
            if n.quarterLength > 100:
                print(f"⚠️ Clamping note {n} with duration {n.quarterLength:.2f}")
                n.quarterLength = 1.0

        # Trim score to only actual notes (+10s padding)
        trimmed_score = score.getElementsByOffset(start_time, end_time + 10, includeEndBoundary=True).flatten()

        # 🔒 Hard cap duration: 10 minutes (600s)
        if trimmed_score.highestTime > 600:
            print(f"⚠️ Trimming {xml_path.name} to 600s max (was {trimmed_score.highestTime:.2f}s)")
            trimmed_score = trimmed_score.getElementsByOffset(0, 600, includeEndBoundary=True).flatten()

        # Final check
        if trimmed_score.highestTime > 1000:
            print(f"❌ Still too long after trim: {trimmed_score.highestTime:.2f}s → Skipping {xml_path.name}")
            return

        # Write MIDI
        midi_path = xml_path.with_suffix(".mid")
        mf = midi.translate.music21ObjectToMidiFile(trimmed_score)
        mf.open(str(midi_path), 'wb')
        mf.write()
        mf.close()

        # Convert to WAV using FluidSynth
        wav_path = midi_path.with_suffix(".wav")
        mp3_path = midi_path.with_suffix(".mp3")
        subprocess.run(["fluidsynth", "-ni", str(sf2), str(midi_path), "-F", str(wav_path)], check=True)

        # Convert WAV to MP3
        subprocess.run(["ffmpeg", "-y", "-i", str(wav_path), str(mp3_path)], check=True)

        # Clean up
        midi_path.unlink()
        wav_path.unlink()

    except Exception as e:
        print(f"❌ Failed processing {xml_path.name}: {e}")

def musicxml_to_mp3_parallel(xml_files, out_dir, sf2, transpose_interval: int = 0, tempo_bpm: int = 120):
    args = [(xml, out_dir, sf2, transpose_interval, tempo_bpm) for xml in xml_files]
    with Pool(cpu_count()) as pool:
        pool.starmap(musicxml_to_midi_and_mp3, args)

def main(input_file: Path, soundfont: Path, transpose_interval: int = 0, bpm: int = 120):
    output = Path("output")

    # 🧹 Step 1: Clean previous output
    if output.exists():
        for file in output.iterdir():
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                shutil.rmtree(file)
    else:
        output.mkdir(parents=True, exist_ok=True)

    # ---------------- PDF → OEMER ---------------- #
    if input_file.suffix.lower() == ".pdf":
        convert_pdf_parallel(input_file, output)
    else:
        run_oemer(input_file, output)

    # ---------------- Sort XML files by page number ---------------- #
    xml_files = sorted(output.glob("*.musicxml"), key=lambda x: int(x.stem.split("_pg")[-1]))

    # ---------------- MusicXML → MP3 in parallel ---------------- #
    musicxml_to_mp3_parallel(xml_files, output, soundfont, transpose_interval=transpose_interval, tempo_bpm=bpm)

    # ---------------- Merge MP3s ---------------- #
    mp3_files = [xml.with_suffix(".mp3") for xml in xml_files if xml.with_suffix(".mp3").exists()]
    if mp3_files:
        merged_mp3 = output / f"{input_file.stem}_merged.mp3"
        merge_mp3s(mp3_files, merged_mp3)
        print(f"🎵 Merged MP3 available at: {merged_mp3}")
    else:
        print("⚠️ No MP3s were generated. Skipping merge.")
