"""Transcription des calls Ringover via OpenAI Whisper API.

Workflow :
1. Download MP3 depuis CDN Ringover (record URL public, pas d'auth)
2. POST à Whisper API (whisper-1, langue fr)
3. Cache local dans ~/.cache/{{SLUG}}/transcripts/{call_id}.json

Coût : ~$0.006/minute. Pour 1 drill (~30-100 calls de 2-3 min) = $0.5-2.

Si pas de OPENAI_API_KEY dans ~/.config/{{SLUG}}/.env, la fonction lève RuntimeError.
"""
from __future__ import annotations
import os
import json
import time
import urllib.request
import urllib.error
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, List

ENV_PATH = Path.home() / ".config" / "{{SLUG}}" / ".env"
CACHE_DIR = Path.home() / ".cache" / "{{SLUG}}" / "transcripts"
WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions"

# ffmpeg static binary via imageio-ffmpeg (no system install needed)
def _ffmpeg_path() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        # Fallback : try system ffmpeg
        path = shutil.which("ffmpeg")
        if path:
            return path
        raise RuntimeError("ffmpeg introuvable. Installe imageio-ffmpeg : pip3 install imageio-ffmpeg")

_OPENAI_KEY: Optional[str] = None


def _load_openai_key() -> str:
    global _OPENAI_KEY
    if _OPENAI_KEY:
        return _OPENAI_KEY
    if not ENV_PATH.exists():
        raise RuntimeError(f"No env file at {ENV_PATH}")
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("OPENAI_API_KEY="):
            _OPENAI_KEY = line.split("=", 1)[1].strip()
            return _OPENAI_KEY
    raise RuntimeError("OPENAI_API_KEY not found in env file")


def _cache_path(call_id: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{call_id}.json"


def _download_mp3(url: str, timeout: int = 120) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read()


def _post_whisper(audio_bytes: bytes, filename: str = "call.mp3", language: str = "fr") -> Dict:
    boundary = "----WhisperBoundary" + os.urandom(8).hex()
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
    body += b"Content-Type: audio/mpeg\r\n\r\n"
    body += audio_bytes + b"\r\n"
    body += f"--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="model"\r\n\r\n'
    body += b"whisper-1\r\n"
    body += f"--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="language"\r\n\r\n'
    body += f"{language}\r\n".encode()
    body += f"--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="response_format"\r\n\r\n'
    body += b"json\r\n"
    body += f"--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        WHISPER_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {_load_openai_key()}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def _chunk_audio(audio_bytes: bytes, segment_seconds: int = 1200) -> List[Path]:
    """Split MP3 audio en chunks de `segment_seconds` (default 20 min) via ffmpeg.

    Args:
        audio_bytes : MP3 raw data
        segment_seconds : durée max par chunk (1200s = 20min ≈ 12-18MB)

    Returns: liste de Path vers les chunks MP3 dans un tmpdir.
    """
    tmpdir = Path(tempfile.mkdtemp(prefix="brand_chunks_"))
    input_path = tmpdir / "input.mp3"
    input_path.write_bytes(audio_bytes)

    output_pattern = str(tmpdir / "chunk_%03d.mp3")
    ffmpeg = _ffmpeg_path()
    # Re-encode (not -c copy) because Ringover MP3s can have non-stream-copyable headers.
    # 64 kbps mono 16 kHz : largement suffisant pour Whisper (voix), ~10MB / 20 min.
    result = subprocess.run(
        [ffmpeg, "-i", str(input_path),
         "-vn",  # no video
         "-ac", "1",  # mono
         "-ar", "16000",  # 16 kHz
         "-b:a", "64k",  # 64 kbps
         "-f", "segment",
         "-segment_time", str(segment_seconds),
         "-reset_timestamps", "1",
         "-y", "-loglevel", "error", output_pattern],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg chunking failed: {result.stderr[:500]}")

    chunks = sorted(tmpdir.glob("chunk_*.mp3"))
    if not chunks:
        raise RuntimeError("ffmpeg did not produce any chunks")
    return chunks


def _transcribe_chunked(audio_bytes: bytes, call_id: str) -> Dict:
    """Pour les fichiers > 25MB : chunk via ffmpeg, transcrit chaque chunk, concatène."""
    t0 = time.time()
    chunks = _chunk_audio(audio_bytes, segment_seconds=1200)  # 20 min chunks

    texts = []
    chunk_durations = []
    try:
        for i, chunk_path in enumerate(chunks, 1):
            chunk_data = chunk_path.read_bytes()
            chunk_size_mb = len(chunk_data) / 1024 / 1024
            if chunk_size_mb > 24:
                # Edge case : un chunk reste trop gros (très haut bitrate). Skip.
                texts.append(f"[chunk {i} skipped: {chunk_size_mb:.1f}MB too large]")
                continue
            try:
                r = _post_whisper(chunk_data, filename=f"{call_id}_chunk{i}.mp3")
                texts.append(r.get("text", ""))
            except urllib.error.HTTPError as e:
                body = e.read().decode()[:300] if e.fp else ""
                texts.append(f"[chunk {i} error: HTTP {e.code} {body[:100]}]")
    finally:
        # Cleanup
        shutil.rmtree(chunks[0].parent, ignore_errors=True)

    full_text = "\n".join(texts)
    return {
        "cached": False,
        "text": full_text,
        "duration_s": round(time.time() - t0, 1),
        "audio_size_kb": round(len(audio_bytes) / 1024, 0),
        "chunked": True,
        "n_chunks": len(chunks),
        "transcribed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def transcribe_call(call_id: str, recording_url: str, force: bool = False,
                    max_size_mb: int = 24) -> Dict:
    """Transcribe a single Ringover call.

    Args:
        call_id : HubSpot call id (used as cache key)
        recording_url : Public CDN URL of the MP3 (from hs_call_recording_url or Ringover record)
        force : si True, ignore le cache et re-transcrire
        max_size_mb : skip files larger than this (Whisper limit = 25 MB)

    Returns dict :
        - cached : bool (si lu depuis cache)
        - text : str (transcription)
        - duration_s : float (durée du processing)
        - error : str si échec
    """
    cache_file = _cache_path(call_id)
    if not force and cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text())
            cached["cached"] = True
            return cached
        except (json.JSONDecodeError, OSError):
            pass

    t0 = time.time()
    try:
        audio_bytes = _download_mp3(recording_url)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        return {"cached": False, "error": f"download_failed: {e}", "text": ""}
    except (TimeoutError, OSError) as e:
        return {"cached": False, "error": f"download_timeout: {e}", "text": ""}

    size_mb = len(audio_bytes) / 1024 / 1024
    if size_mb > max_size_mb:
        # File too large for a single Whisper request → chunk via ffmpeg
        try:
            result = _transcribe_chunked(audio_bytes, call_id)
            cache_file.write_text(json.dumps(result, ensure_ascii=False, indent=2))
            return result
        except Exception as e:
            return {"cached": False, "error": f"chunking_failed: {type(e).__name__}: {e}", "text": ""}

    try:
        whisper_result = _post_whisper(audio_bytes, filename=f"{call_id}.mp3")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500] if e.fp else ""
        return {"cached": False, "error": f"whisper_http_{e.code}: {body}", "text": ""}
    except Exception as e:
        return {"cached": False, "error": f"whisper_{type(e).__name__}: {e}", "text": ""}

    result = {
        "cached": False,
        "text": whisper_result.get("text", ""),
        "duration_s": round(time.time() - t0, 1),
        "audio_size_kb": round(len(audio_bytes) / 1024, 0),
        "transcribed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    cache_file.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def transcribe_calls_batch(calls: list, force: bool = False, verbose: bool = False) -> Dict[str, Dict]:
    """Transcribe a list of calls. Each call must have 'id' and 'recording_url'.
    Returns: {call_id: transcribe_result}
    """
    out = {}
    total = len(calls)
    for i, c in enumerate(calls, 1):
        cid = c.get("id")
        url = c.get("recording_url") or c.get("hs_call_recording_url")
        if not cid or not url:
            out[cid or f"unknown_{i}"] = {"error": "missing_id_or_url", "text": ""}
            continue
        if verbose:
            print(f"  [{i}/{total}] transcribing call {cid}...", flush=True)
        r = transcribe_call(cid, url, force=force)
        out[cid] = r
        if verbose:
            status = "cached" if r.get("cached") else f"{r.get('duration_s','?')}s"
            err = r.get("error", "")
            print(f"    → {status}{' / ' + err if err else ''}", flush=True)
    return out


if __name__ == "__main__":
    # Self-test sur 1 call Pauline
    test_url = "https://votre-telephonie.example.com/records/EXEMPLE.mp3"  # URL d'un enregistrement à transcrire
    r = transcribe_call("test_pauline_42", test_url)
    print(f"Cached: {r.get('cached')}")
    print(f"Error: {r.get('error', 'none')}")
    print(f"Text length: {len(r.get('text',''))}")
    print(f"Preview: {r.get('text','')[:300]}")
