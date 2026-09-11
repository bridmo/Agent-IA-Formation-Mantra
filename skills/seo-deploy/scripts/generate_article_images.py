#!/usr/bin/env python3
"""Generate editorial images via OpenAI Images API (gpt-image-1).

Standalone helper for the seo-deploy pipeline. Reads OPENAI_API_KEY from
project .env, generates each prompt at 1536x1024 (16:9) high quality, saves
PNGs to the target asset directory.
"""
import os
import sys
import pathlib
import base64
import json
import time
import concurrent.futures
import requests
from pathlib import Path

# Racine du repo, déduite de l'emplacement de ce fichier
REPO_ROOT = Path(__file__).resolve().parents[3]



def load_env(env_path):
    p = pathlib.Path(env_path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def generate_one(name, prompt, api_key, output_dir):
    print(f"[{name}] generating...", flush=True)
    t0 = time.time()
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": "gpt-image-2",
            "prompt": prompt,
            "n": 1,
            "size": "1536x1024",
            "quality": "high",
        },
        timeout=300,
    )
    if r.status_code != 200:
        print(f"[{name}] ERROR {r.status_code}: {r.text[:400]}", flush=True)
        return None
    data = r.json()
    img_b64 = data["data"][0]["b64_json"]
    img_bytes = base64.b64decode(img_b64)
    out_path = output_dir / f"{name}.png"
    out_path.write_bytes(img_bytes)
    dt = time.time() - t0
    print(f"[{name}] saved {out_path} ({len(img_bytes)//1024} kB, {dt:.1f}s)", flush=True)
    return out_path


def main():
    load_env(REPO_ROOT / ".env")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY missing", file=sys.stderr)
        sys.exit(1)

    output_dir = pathlib.Path(
        str(REPO_ROOT / "channels/content/blog/assets/<slug-de-article>")
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    prompts = {
        "A-portrait-marketeuse": (
            "Editorial photograph, three-quarter view of a woman in her late thirties, French marketing professional. "
            "She sits at a light wooden desk by a large window with soft natural daylight. She is leaning slightly forward, "
            "looking thoughtfully at her open laptop screen, mid-decision. A small espresso cup and a leather notebook with "
            "a fountain pen rest beside the laptop. Her style is understated professional creative: minimalist linen shirt, "
            "no logos, no jewelry. Background: warm-toned home office or shared workspace with subtle depth-of-field blur, "
            "soft beige walls, hint of plants. Color palette: warm cream, soft beige, navy blue accents on her shirt. "
            "Editorial magazine quality, NY Times / Le Monde long-read aesthetic. Natural film grain. 16:9 widescreen ratio. "
            "Photorealistic, no readable text, no brand logos visible on the laptop screen."
        ),
        "B-mains-hesitantes": (
            "Editorial close-up photograph, top-down view of a person's hands hovering above a laptop keyboard, fingers "
            "slightly tense as if about to type but hesitating. A smartphone lies beside the laptop, screen softly lit but "
            "blurred. The laptop screen shows a generic interface gently blurred, soft cream and navy tones. Hands are "
            "clean, no jewelry, professional posture. Soft natural lighting from a window on the right. Color palette: "
            "warm cream, soft beige, deep navy. Editorial photography, magazine quality. 16:9 widescreen ratio. "
            "Photorealistic, no readable text, no brand logos."
        ),
        "C-flat-lay-cartes": (
            "Editorial flat lay photograph, top-down view of a clean light wooden desk surface. In the upper part of the "
            "frame, an open laptop with screen partially visible but content abstract and blurred. In the center, four "
            "identical pale paper cards arranged in a neat row, slightly overlapping. A single hand of an adult woman with "
            "minimal natural nails gently pointing with the index finger toward the third card from left. A small espresso "
            "cup on the right. A leather-bound notebook with a fountain pen on the upper left. Soft natural overhead "
            "daylight. The four cards are blank or feature abstract minimal markings, no readable text. Color palette: "
            "warm cream wood tones, soft beige paper, dark navy accents. Premium editorial magazine aesthetic, Monocle / "
            "Kinfolk style. 16:9 widescreen ratio. Photorealistic, no readable text, no logos."
        ),
        "E-paliers-architecturaux": (
            "Editorial architectural photograph, minimalist modern interior space with four ascending terraced platforms "
            "or levels in a quiet contemporary museum-like building. Each platform is slightly higher than the previous, "
            "separated by short steps. Warm natural light pours from a tall side window, illuminating the third platform "
            "more strongly than the others, creating a subtle highlight. The space is empty of people. Materials: pale "
            "stone, light wood, soft cream walls, hints of deep navy in shadows. Architectural minimalism in the spirit "
            "of Vincent Van Duysen, John Pawson, or Studio KO. Monochromatic warm palette. 16:9 widescreen ratio. "
            "Photorealistic, no text, no signage, no logos."
        ),
    }

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futures = {
            ex.submit(generate_one, name, prompt, api_key, output_dir): name
            for name, prompt in prompts.items()
        }
        for f in concurrent.futures.as_completed(futures):
            f.result()

    print("\nDone. Files in:", output_dir)


if __name__ == "__main__":
    main()
