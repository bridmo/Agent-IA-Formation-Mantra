"""
Webflow deploy pipeline for {{COMPANY}} blog articles.

Usage:
    from webflow_deploy import WebflowDeployer, build_sommaire, BRAND_CATEGORIES
    deployer = WebflowDeployer()
    item_id = deployer.create_draft(markdown_path)
    deployer.generate_and_inject_images(item_id, article_slug, placeholders)
"""
import os, json, base64, hashlib, pathlib, re, requests, sys
from dataclasses import dataclass
from pathlib import Path

# Racine du repo, déduite de l'emplacement de ce fichier
REPO_ROOT = Path(__file__).resolve().parents[3]



# {{COMPANY}} Blog Categories (MultiReference item IDs)
# Source: Webflow CMS collection Blog Categories (690388bd287938ccbb5d7c72)
BRAND_CATEGORIES = {
    "outils": "692c9a1d937c5e652dd51d44",
    "news_ia": "692c9b69ddd2e695edf9ac8f",
    "growth_marketing": "692c9a49a7d5a8847c1b9c13",
    "metier": "692c99fe3fd8217ac4eebf85",
    "podcasts": "692c9b554d9648112bb49387",
    "success_stories": "690389291e34c9f32b2c071f",
}

# Enum options for categorie-afficher (filter label UI, different from MultiRef)
BRAND_CATEGORIE_FILTER = {
    "metier": "70cbe239f7cf96d5c2141b4bb993f15b",
    "outils": "38d9d7ace7825ded9cab1817df4ead67",
    "growth_marketing": "9ff562763a0c3745cba798d5d2d47499",
    "podcasts": "9f8277055bb61b0557b7000cbb6ca8ab",
    "news_ia": "628d12274fdfd373bb78e86739a97b88",
    "success_stories": "b6b08abaf6e6822d2c1f706f5eebc19e",
}


def build_sommaire(html_body: str, exclude_titles=("FAQ", "Ressources")) -> str:
    """Extract H2s from HTML body and build a simple TOC for the sommaire-2 field.
    Excludes FAQ and Ressources by default (typical TOC convention)."""
    h2_titles = re.findall(r"<h2>([^<]+)</h2>", html_body)
    toc_items = [h for h in h2_titles if h not in exclude_titles]
    if not toc_items:
        return ""
    return "<ul>\n" + "\n".join(f"  <li>{t}</li>" for t in toc_items) + "\n</ul>"


def load_env(env_path=REPO_ROOT / ".env"):
    """Load env vars from .env file (since shell env vars may not inherit)."""
    p = pathlib.Path(env_path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


@dataclass
class ImagePlaceholder:
    """Represents an image placeholder in a markdown article."""
    kind: str  # "photo" or "schema"
    description: str
    alt_text: str
    index: int  # order of appearance (0-based)


class NanoBananaGenerator:
    """Generate photo-style images via Gemini Nano Banana Pro."""

    def __init__(self):
        load_env()
        self.api_key = os.environ["GEMINI_API_KEY"]
        self.model = "nano-banana-pro-preview"
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def brand_prompt_wrapper(self, scene_description):
        """Wrap a scene description with {{COMPANY}} brand art direction."""
        return f"""A minimalist flat-design editorial illustration in {{COMPANY}} brand style.

PALETTE (STRICT — follow exactly):
- Dominant: warm cream background (#FAF9F5) + navy deep (#282C4B) as primary contrast
- Secondary variation: warm light beige (#F0E9E3) and navy medium (#394E8A)
- Accents ONLY (tiny details, max 5% of surface): royal blue (#103ACD) or mustard yellow (#EFC222)
  — NEVER use blue or yellow as dominant surface color
  — They can only highlight ONE small element (a dot, a small icon, a single line)

STYLE:
- Soft rounded shapes, clean vector-style aesthetic
- Professional, warm, serious
- Magazine editorial quality (NY Times / Le Monde long-read style)
- Understated French editorial chic
- NOT corporate SaaS, NOT colorful stock

RULES:
- NO text in the image
- NO close-up faces
- NO 3D / neon / futuristic tech aesthetic
- 16:9 blog hero ratio

SCENE: {scene_description}"""

    def generate(self, prompt, output_path):
        """Generate one image and save to output_path. Returns (path, mime, bytes)."""
        full_prompt = self.brand_prompt_wrapper(prompt)
        r = requests.post(
            self.endpoint,
            headers={"Content-Type": "application/json", "X-goog-api-key": self.api_key},
            json={
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"responseModalities": ["IMAGE"]}
            },
            timeout=60
        )
        d = json.loads(r.content, strict=False)
        if "candidates" not in d:
            raise RuntimeError(f"Gemini error: {d.get('error', d)}")
        for part in d["candidates"][0]["content"]["parts"]:
            if "inlineData" in part:
                img_bytes = base64.b64decode(part["inlineData"]["data"])
                mime = part["inlineData"].get("mimeType", "image/jpeg")
                pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                pathlib.Path(output_path).write_bytes(img_bytes)
                return output_path, mime, img_bytes
        raise RuntimeError("No image returned by Gemini")


class WebflowDeployer:
    """Push drafts + images to Webflow CMS."""

    def __init__(self):
        load_env()
        self.token = os.environ["WEBFLOW_API_TOKEN"]
        self.site_id = os.environ["WEBFLOW_SITE_ID"]
        self.coll_id = os.environ["WEBFLOW_BLOG_COLLECTION_ID"]
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        self.base = "https://api.webflow.com/v2"

    def upload_asset(self, filepath, filename, mime, alt_text=""):
        """Upload a local file to Webflow assets. Returns (asset_id, hosted_url)."""
        data = pathlib.Path(filepath).read_bytes()
        file_hash = hashlib.md5(data).hexdigest()

        # Step 1: presigned URL
        r = requests.post(
            f"{self.base}/sites/{self.site_id}/assets",
            headers=self.headers,
            json={"fileName": filename, "fileHash": file_hash}
        )
        if r.status_code != 202:
            raise RuntimeError(f"assets create failed: {r.status_code} — {r.text[:300]}")
        ad = r.json()
        asset_id = ad["id"]
        hosted_url = ad["hostedUrl"]
        upload_url = ad.get("uploadUrl") or ad["uploadDetails"]["url"]
        fields = dict(ad["uploadDetails"])
        fields.pop("url", None)

        # Step 2: S3 multipart upload
        files = {"file": (filename, data, mime)}
        r2 = requests.post(upload_url, data=fields, files=files)
        if r2.status_code not in (200, 201, 204):
            raise RuntimeError(f"S3 upload failed: {r2.status_code} — {r2.text[:300]}")

        # Step 3: PATCH alt text (async, don't block on failure)
        if alt_text:
            requests.patch(
                f"{self.base}/assets/{asset_id}",
                headers=self.headers,
                json={"altText": alt_text}
            )

        return asset_id, hosted_url

    def get_item(self, item_id):
        r = requests.get(
            f"{self.base}/collections/{self.coll_id}/items/{item_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        r.raise_for_status()
        return r.json()

    def find_item_by_slug(self, slug):
        """Lookup CMS item by slug. Returns the item dict (with fieldData) or None.
        Paginates the collection — Webflow caps page size at 100."""
        offset = 0
        while True:
            r = requests.get(
                f"{self.base}/collections/{self.coll_id}/items",
                headers={"Authorization": f"Bearer {self.token}"},
                params={"limit": 100, "offset": offset}
            )
            r.raise_for_status()
            payload = r.json()
            for item in payload.get("items", []):
                if item.get("fieldData", {}).get("slug") == slug:
                    return item
            total = payload.get("pagination", {}).get("total", 0)
            offset += len(payload.get("items", []))
            if offset >= total or not payload.get("items"):
                return None

    def diff_post_body(self, local_html, remote_html):
        """Compare local post-body HTML vs remote (Webflow) post-body HTML.
        Returns {drift, blocks_only_in_remote, blocks_changed, summary}.
        Block granularity: <p>, <h2>, <h3>, <h4>, <li>, <blockquote> text content.
        Whitespace and tags inside blocks are normalized; image src URLs are excluded
        (assets get re-uploaded with new URLs every push, that's not real drift)."""
        local_blocks = _extract_text_blocks(local_html or "")
        remote_blocks = _extract_text_blocks(remote_html or "")

        local_set = {b["norm"] for b in local_blocks}
        remote_set = {b["norm"] for b in remote_blocks}

        only_in_remote = [b for b in remote_blocks if b["norm"] not in local_set]
        only_in_local = [b for b in local_blocks if b["norm"] not in remote_set]

        # blocks_changed: same tag + similar position but different normalized text.
        # Heuristic: pair sequential headings (h2/h3) by index since they anchor structure.
        blocks_changed = []
        local_headings = [b for b in local_blocks if b["tag"] in ("h2", "h3", "h4")]
        remote_headings = [b for b in remote_blocks if b["tag"] in ("h2", "h3", "h4")]
        for i in range(min(len(local_headings), len(remote_headings))):
            l, r = local_headings[i], remote_headings[i]
            if l["tag"] == r["tag"] and l["norm"] != r["norm"]:
                blocks_changed.append({"tag": l["tag"], "local": l["text"], "remote": r["text"]})

        drift = bool(only_in_remote) or bool(blocks_changed)
        summary = (
            f"local={len(local_blocks)} blocks, remote={len(remote_blocks)} blocks, "
            f"only_in_remote={len(only_in_remote)}, only_in_local={len(only_in_local)}, "
            f"headings_changed={len(blocks_changed)}"
        )
        return {
            "drift": drift,
            "blocks_only_in_remote": [{"tag": b["tag"], "text": b["text"][:200]} for b in only_in_remote],
            "blocks_only_in_local": [{"tag": b["tag"], "text": b["text"][:200]} for b in only_in_local],
            "blocks_changed": blocks_changed,
            "summary": summary,
        }

    def patch_item(self, item_id, field_updates, is_draft=True):
        """PATCH a CMS item with new field values."""
        payload = {
            "fieldData": field_updates,
            "isDraft": is_draft,
            "isArchived": False
        }
        r = requests.patch(
            f"{self.base}/collections/{self.coll_id}/items/{item_id}",
            headers=self.headers,
            json=payload
        )
        if r.status_code not in (200, 204):
            raise RuntimeError(f"PATCH item failed: {r.status_code} — {r.text[:300]}")
        return r.json() if r.status_code == 200 else None

    def replace_placeholder(self, html, placeholder_pattern_regex, img_url, alt_text):
        """Replace a [IMAGE: ...] placeholder blockquote with an <img> tag in Webflow rich text format."""
        img_html = (
            f'<figure class="w-richtext-figure-type-image w-richtext-align-fullwidth" data-rt-type="image">'
            f'<div><img src="{img_url}" loading="lazy" alt="{alt_text}" />'
            f'</div></figure>'
        )
        return re.sub(placeholder_pattern_regex, img_html, html, count=1, flags=re.DOTALL)


_BLOCK_RE = re.compile(
    r"<(?P<tag>p|h2|h3|h4|li|blockquote)[^>]*>(?P<inner>.*?)</(?P=tag)>",
    re.DOTALL | re.IGNORECASE,
)
_TAG_STRIP_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _extract_text_blocks(html):
    """Extract text content of each block-level element used in {{COMPANY}} rich text.
    Returns list of {tag, text, norm}. `norm` is lowercased + whitespace-normalized
    for diff comparison."""
    blocks = []
    for m in _BLOCK_RE.finditer(html):
        tag = m.group("tag").lower()
        inner = m.group("inner")
        text = _TAG_STRIP_RE.sub("", inner)
        text = _WS_RE.sub(" ", text).strip()
        if not text:
            continue
        norm = text.lower()
        blocks.append({"tag": tag, "text": text, "norm": norm})
    return blocks


def extract_image_placeholders(markdown_text):
    """Parse [IMAGE-PHOTO: ...] and [IMAGE-SCHEMA: ...] from markdown.
    Falls back to [IMAGE: ...] with heuristic classification."""
    placeholders = []
    # Typed placeholders
    typed_re = re.compile(
        r"\[IMAGE-(PHOTO|SCHEMA)\s*:\s*([^\]]+)\]\s*\n(?:Alt\s*text\s*:\s*\"?([^\"\n]+)\"?)?",
        re.IGNORECASE
    )
    # Untyped placeholder (legacy)
    untyped_re = re.compile(
        r"\[IMAGE\s*:\s*([^\]]+)\]\s*\n(?:Alt\s*text\s*:\s*\"?([^\"\n]+)\"?)?",
        re.IGNORECASE
    )

    idx = 0
    for m in typed_re.finditer(markdown_text):
        placeholders.append(ImagePlaceholder(
            kind=m.group(1).lower(),
            description=m.group(2).strip(),
            alt_text=(m.group(3) or "").strip(),
            index=idx
        ))
        idx += 1

    # Also capture untyped placeholders not already caught by typed_re
    typed_spans = [m.span() for m in typed_re.finditer(markdown_text)]
    for m in untyped_re.finditer(markdown_text):
        # skip if this match is inside a typed_re match already
        if any(m.start() >= s and m.end() <= e for s, e in typed_spans):
            continue
        desc = m.group(1).strip()
        # Heuristic classification
        schema_hints = ["schéma", "schema", "diagramme", "tableau", "comparatif", "flowchart", "étapes", "quadrant", "timeline"]
        kind = "schema" if any(h in desc.lower() for h in schema_hints) else "photo"
        placeholders.append(ImagePlaceholder(
            kind=kind,
            description=desc,
            alt_text=(m.group(2) or "").strip(),
            index=idx
        ))
        idx += 1

    return placeholders


if __name__ == "__main__":
    # CLI test
    print("WebflowDeployer + NanoBananaGenerator library loaded.")
    print(f"Site ID: {os.environ.get('WEBFLOW_SITE_ID','?')}")
