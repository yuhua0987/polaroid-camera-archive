#!/usr/bin/env python3
"""Build a static, offline-capable gallery using only the Python standard library."""

import argparse
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def build(output: Path) -> Path:
    output = output.resolve()
    template = (ROOT / "web/index.html").read_text(encoding="utf-8")
    data = json.loads((ROOT / "data/catalog.json").read_text(encoding="utf-8"))
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    html = template.replace("__STYLE__", (ROOT / "web/style.css").read_text(encoding="utf-8"))
    html = html.replace("__APP__", (ROOT / "web/app.js").read_text(encoding="utf-8"))
    html = html.replace("__DATA__", payload)
    output.mkdir(parents=True, exist_ok=True)
    if output != ROOT:
        for directory in ("assets", "data", "docs"):
            shutil.copytree(ROOT / directory, output / directory, dirs_exist_ok=True)
        for filename in ("LICENSE", "NOTICE.md", "README.md", "README.en.md"):
            shutil.copy2(ROOT / filename, output / filename)
    target = output / "index.html"
    target.write_text(html, encoding="utf-8")
    (output / ".nojekyll").touch()
    print(f"Built {target.name}: {len(data['models'])} catalog entries, {data['stats']['bundled_images']} bundled images")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    build(parser.parse_args().output)
