#!/usr/bin/env python3
"""Regenerate coverage and attribution documents from the public catalog."""

import json
from pathlib import Path
from update_sources import update as update_sources

ROOT = Path(__file__).resolve().parents[1]


def text(value):
    return str(value).replace("|", "/").replace("[", "\\[").replace("]", "\\]")


def update():
    update_sources()
    d = json.loads((ROOT / "data/catalog.json").read_text(encoding="utf-8"))
    media = json.loads((ROOT / "data/media-manifest.json").read_text(encoding="utf-8"))["images"]
    lines = ["# Model and angle coverage / 型号与视角覆盖", "",
             "Angle labels describe all source references, including images not distributed here. Oblique views and folded state are separate labels. A missing label means a view is missing or not yet checked. A source link does not imply that the image is bundled.", "",
             "| ID / model | Family | References | Bundled | Recorded views / state | Pure front / side / back pending |",
             "|---|---|---:|---:|---|---|"]
    for m in d["models"]:
        n = sum(p["distribution"] == "bundled" for p in m["photos"])
        views = " / ".join(m["views_recorded"]) or "未标注"
        pending = " / ".join(m["strict_views_pending"]) or "已标注"
        lines.append(f"| [{m['id']} · {text(m['name'])}](../index.html#{m['id']}) | {text(m['family'])} | {len(m['photos'])} | {n} | {views} | {pending} |")
    (ROOT / "docs/COVERAGE.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    lines = ["# Image attributions / 图片署名", "",
             "Each photograph and its preview retain the license below. Downloaded responses were not edited locally; previews were resized and composited onto white where needed. Source servers may have supplied resized versions. Public-domain records retain the source's stated status.", "",
             f"**{len(media)} images.** License capture dates are recorded per image in the media manifest. Original file pages include further attribution information.", ""]
    for a in sorted(media, key=lambda item: item["sha256"]):
        title = text(a["title"].removeprefix("File:"))
        lines += [f"## {a['sha256'][:16]}", "",
                  f"- Image: [{title}](../{a['path']})",
                  f"- Author / attribution: {text(a['author'])}",
                  f"- Original file page: [{a['source']}]({a['source']})",
                  f"- License: [{a['license']}]({a['license_url']})",
                  f"- Source usage terms: {text(a['usage_terms'])}",
                  f"- Changes: {a['changes']}",
                  f"- SHA-256: `{a['sha256']}`", ""]
    (ROOT / "docs/ATTRIBUTION.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Updated coverage for {len(d['models'])} entries and credits for {len(media)} images")


if __name__ == "__main__":
    update()
