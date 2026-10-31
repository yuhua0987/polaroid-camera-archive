#!/usr/bin/env python3
"""Validate catalog integrity, media attribution and the publication boundary."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    "CC BY-SA 4.0", "CC BY-SA 3.0", "CC BY-SA 2.0",
    "CC BY 4.0", "CC BY 3.0", "CC BY 2.0",
    "CC0", "Public domain", "FAL",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def web_url(url):
    p = urlsplit(url)
    return p.scheme in {"http", "https"} and bool(p.netloc) and not p.username and not p.password


def local_path(base, value):
    require(isinstance(value, str) and bool(value), "Empty local file path")
    p = (base / value).resolve()
    require(p.is_relative_to(base.resolve()), "Local file path escapes repository")
    require(p.is_file(), f"Missing local file: {value}")
    return p


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(site=None):
    d = json.loads((ROOT / "data/catalog.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "data/media-manifest.json").read_text(encoding="utf-8"))
    models, stats = d["models"], d["stats"]
    require(d["schema_version"] == 1, "Unknown schema version")
    require(len({m["id"] for m in models}) == len(models), "Duplicate model ID")
    media = {m["sha256"]: m for m in manifest["images"]}
    require(len(media) == len(manifest["images"]), "Duplicate media manifest entry")
    photos, included = [], set()
    for m in models:
        require(re.fullmatch(r"P\d{3,}", m["id"]), "Invalid model ID")
        require(m["name"] and m["family"] and m["sources"], f"Incomplete model: {m['id']}")
        require(all(web_url(u) for u in m["sources"]), f"Invalid source URL: {m['id']}")
        require(len({p["sha256"] for p in m["photos"]}) == len(m["photos"]), f"Duplicate image within {m['id']}")
        for p in m["photos"]:
            photos.append(p)
            require(web_url(p["source"]) and web_url(p["url"]), f"Invalid photo source URL: {m['id']}")
            require(not p.get("original_url") or web_url(p["original_url"]), "Invalid original image URL")
            require(p.get("source_host") == (urlsplit(p["source"]).hostname or "").lower().removeprefix("www."), "Photo source website does not match its source URL")
            require(bool(p.get("source_website")), "Missing photo source website label")
            require(re.fullmatch(r"[0-9a-f]{64}", p["sha256"]), "Invalid photo hash")
            require(p["width"] > 0 and p["height"] > 0, "Invalid photo dimensions")
            if p["distribution"] == "reference-only":
                require(p["path"] is None and p["thumb"] is None and p["license_url"] is None, "Source-only image has bundled paths or implied license grant")
                continue
            require(p["distribution"] == "bundled", "Unknown image distribution value")
            require(p["origin"] == "commons" and p["license"] in ALLOWED, "Unapproved media distribution")
            require(p["credit"] and web_url(p["license_url"]), "Missing image attribution / license")
            require(p["sha256"] in media, "Bundled image lacks a license manifest entry")
            a = media[p["sha256"]]
            require(a["path"] == p["path"] and a["thumb"] == p["thumb"], "Media paths disagree")
            require(a["source"] == p["source"] and a["license"] == p["license"], "Media license or source disagrees")
            require(a["license_url"] == p["license_url"] and a["author"] == p["credit"], "Media attribution disagrees")
            require(a["changes"] and a["retrieved_date"] and a["usage_terms"], "Missing media provenance or modification notice")
            if p["sha256"] not in included:
                require(digest(local_path(ROOT, p["path"])) == p["sha256"], "Media content hash mismatch")
                require(digest(local_path(ROOT, p["thumb"])) == a["thumbnail_sha256"], "Thumbnail hash mismatch")
                included.add(p["sha256"])
    expected = {
        "models": len(models),
        "families": len({m["family"] for m in models}),
        "photo_references": len(photos),
        "referenced_images": len({p["sha256"] for p in photos}),
        "models_with_references": sum(bool(m["photos"]) for m in models),
        "missing_reference_models": sum(not m["photos"] for m in models),
        "bundled_images": len(included),
        "models_with_bundled_images": sum(any(p["distribution"] == "bundled" for p in m["photos"]) for m in models),
    }
    require(stats == expected, "Catalog statistics are stale")
    source_sites = json.loads((ROOT / "data/source-sites.json").read_text(encoding="utf-8"))["sites"]
    require(sum(s["references"] for s in source_sites) == len(photos), "Source directory does not cover all photo references")
    require({s["host"] for s in source_sites} == {p["source_host"] for p in photos}, "Source directory websites disagree with photo records")
    for s in source_sites:
        rows = [p for p in photos if p["source_host"] == s["host"]]
        require(len(rows) == s["references"], "Source website reference count is stale")
        require(sum(p["distribution"] == "bundled" for p in rows) == s["bundled"], "Source website bundled count is stale")
        local_path(ROOT, s["document"])
    require(set(media) == included, "Unreferenced media manifest records")
    expected_files = {p[key] for p in media.values() for key in ("path", "thumb")}
    actual_files = {p.relative_to(ROOT).as_posix() for directory in ("assets/media", "assets/thumbs") for p in (ROOT / directory).rglob("*") if p.is_file()}
    require(actual_files == expected_files, "Unexpected or missing distributed image files")
    credits = (ROOT / "docs/ATTRIBUTION.md").read_text(encoding="utf-8")
    require(all(h in credits for h in included), "Bundled photo absent from attribution document")
    forbidden = re.compile(r"/Users/|/home/|github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----")
    for base in (ROOT / "data", ROOT / "web", ROOT / "docs", ROOT / "tools"):
        for f in base.rglob("*"):
            if f.is_file() and f.suffix in {".md", ".json", ".html", ".js", ".css", ".py"} and f.name != "validate.py":
                require(not forbidden.search(f.read_text(encoding="utf-8")), f"Private path or credential pattern in {f.relative_to(ROOT)}")
    if site:
        html = (site / "index.html").read_text(encoding="utf-8")
        match = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S)
        require(match and json.loads(match[1]) == d, "Built HTML data differs from catalog")
        require(not any(token in html for token in ("__STYLE__", "__APP__", "__DATA__")), "Unexpanded HTML placeholder")
        for p in media.values():
            require(digest(local_path(site, p["path"])) == p["sha256"], "Built site image differs")
            local_path(site, p["thumb"])
        require((ROOT / "index.html").read_bytes() == (site / "index.html").read_bytes(), "Committed offline page is stale; run build.py --output .")
    print(json.dumps({"validated": expected, "licenses": dict(Counter(p["license"] for p in media.values()))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path)
    args = parser.parse_args()
    try:
        validate(args.site)
    except (ValueError, KeyError, FileNotFoundError) as error:
        raise SystemExit(f"Validation failed: {error}")
