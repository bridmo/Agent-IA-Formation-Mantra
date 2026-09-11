#!/usr/bin/env python3
"""Génère des créas Meta Ads en PNG aux formats exacts (1:1, 4:5, 9:16).

Usage: python3 generate_ad_images.py <manifest.json>

Manifest:
{
  "output_dir": "ads/meta/meta-remix/output/2026-06-11/concept-x",
  "images": [
    {"name": "concept-x-v1", "prompt": "...", "formats": ["square", "portrait", "story"]}
  ]
}

Pipeline : OpenAI gpt-image-2 (clé OPENAI_API_KEY du .env projet) génère une source
1024x1024 (square) ou 1024x1536 (portrait/story), puis sips (macOS) resize/crop
aux dimensions Meta exactes. Pattern repris de skills/seo-deploy/scripts/generate_article_images.py.
"""
import base64
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

import requests

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]

# format Meta -> (taille source gpt-image, dimensions finales WxH)
FORMATS = {
    "square": ("1024x1024", (1080, 1080)),    # feed carré
    "portrait": ("1024x1536", (1080, 1350)),  # feed 4:5
    "story": ("1024x1536", (1080, 1920)),     # stories / reels 9:16
}


def load_env(env_path):
    p = pathlib.Path(env_path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def generate_source(prompt, size, api_key, out_path):
    t0 = time.time()
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "gpt-image-2", "prompt": prompt, "n": 1, "size": size, "quality": "high"},
        timeout=300,
    )
    if r.status_code != 200:
        print(f"  ERREUR {r.status_code}: {r.text[:400]}", flush=True)
        return False
    img_bytes = base64.b64decode(r.json()["data"][0]["b64_json"])
    out_path.write_bytes(img_bytes)
    print(f"  source {size} générée ({len(img_bytes)//1024} kB, {time.time()-t0:.1f}s)", flush=True)
    return True


def sips(*args):
    subprocess.run(["sips", *args], check=True, capture_output=True)


def derive(source_path, fmt, out_path):
    """Resize/crop la source vers les dimensions Meta exactes, sans distorsion."""
    w, h = FORMATS[fmt][1]
    shutil.copyfile(source_path, out_path)
    if fmt == "square":
        sips("-z", str(h), str(w), str(out_path))
    elif fmt == "portrait":
        # 1024x1536 -> largeur 1080 (=> 1080x1620) -> crop centré 1080x1350
        sips("--resampleWidth", str(w), str(out_path))
        sips("-c", str(h), str(w), str(out_path))
    elif fmt == "story":
        # 1024x1536 -> hauteur 1920 (=> 1280x1920) -> crop centré 1080x1920
        sips("--resampleHeight", str(h), str(out_path))
        sips("-c", str(h), str(w), str(out_path))
    print(f"  -> {out_path.name} ({w}x{h})", flush=True)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    load_env(PROJECT_ROOT / ".env")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY manquante (.env projet)", file=sys.stderr)
        sys.exit(1)

    manifest = json.loads(pathlib.Path(sys.argv[1]).read_text())
    output_dir = pathlib.Path(manifest["output_dir"])
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    failures = 0
    for img in manifest["images"]:
        name, prompt = img["name"], img["prompt"]
        formats = img.get("formats", ["square", "portrait"])
        print(f"[{name}] formats: {', '.join(formats)}", flush=True)
        # une seule génération par taille source, déclinée ensuite
        sources = {}
        for fmt in formats:
            size = FORMATS[fmt][0]
            if size not in sources:
                src = output_dir / f"{name}-src-{size}.png"
                if generate_source(prompt, size, api_key, src):
                    sources[size] = src
                else:
                    sources[size] = None
                    failures += 1
        for fmt in formats:
            src = sources.get(FORMATS[fmt][0])
            if src:
                derive(src, fmt, output_dir / f"{name}-{fmt}.png")
        # nettoyage des sources intermédiaires
        for src in sources.values():
            if src and src.exists():
                src.unlink()

    print(f"\nTerminé. Sortie : {output_dir}" + (f" — {failures} échec(s)" if failures else ""))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
