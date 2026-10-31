#!/usr/bin/env python3
"""Label every photo's source website and generate a complete source directory."""

from collections import defaultdict
import json
from pathlib import Path
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
NAMES = {
    "retrospekt.com": "Retrospekt",
    "polamad.com": "Polaroid Madness",
    "filmphotography.eu": "FilmPhotography.eu",
    "polaroid.com": "Polaroid 官方网站",
    "brooklynfilmcamera.com": "Brooklyn Film Camera",
    "commons.wikimedia.org": "Wikimedia Commons",
    "ebay.com": "eBay",
    "ebay.es": "eBay España",
    "ebay.co.uk": "eBay UK",
    "etsy.com": "Etsy",
    "dancuny.com": "Dan Cuny",
    "polaroidcollection.jimdofree.com": "Polaroid Collection",
    "upcycledclassics.com": "Upcycled Classics",
    "kleinanzeigen.de": "Kleinanzeigen",
    "item.fril.jp": "Rakuma / ラクマ",
    "tiendainstant.com": "Tienda Instant",
    "axioart.com": "Axioart / Darabanth",
    "photothinking.com": "PhotoThinking",
    "cjo.info": "Christopher J Osborne",
    "stanstudio.com": "Stanley Rowin / StanStudio",
    "flickr.com": "Flickr",
}


def host(url):
    return (urlsplit(url).hostname or "").lower().removeprefix("www.")


def label(value):
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("[", "\\[").replace("]", "\\]").replace("\n", " ")


def target(url):
    # Keep provenance URLs unchanged in the JSON; omit marketing parameters only
    # from generated human-facing links. Parentheses are escaped for Markdown.
    u = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(u.query, keep_blank_values=True) if not k.startswith("utm_") and k != "srsltid"]
    return urlunsplit((u.scheme, u.netloc, u.path, urlencode(query), u.fragment)).replace("(", "%28").replace(")", "%29")


def update():
    path = ROOT / "data/catalog.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    rights = json.loads((ROOT / "data/source-rights.json").read_text(encoding="utf-8"))
    groups = defaultdict(list)
    for model in d["models"]:
        for position, photo in enumerate(model["photos"], 1):
            h = host(photo["source"])
            photo["source_host"] = h
            photo["source_website"] = NAMES.get(h, h)
            groups[h].append((model, position, photo))
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    folder = ROOT / "docs/sources"
    folder.mkdir(exist_ok=True)
    sites = []
    for h, rows in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0])):
        name = NAMES.get(h, h)
        filename = re.sub(r"[^a-z0-9.-]", "_", h) + ".md"
        policy = rights["sites"].get(h, {
            "status": "redistribution-not-confirmed",
            "summary": "未确认照片可公开再分发；仅保留来源页面与原图地址。",
            "policy_url": None,
        })
        bundled = sum(p["distribution"] == "bundled" for _, _, p in rows)
        sites.append(dict(host=h, name=name, references=len(rows), models=len({m["id"] for m, _, _ in rows}), bundled=bundled, reference_only=len(rows)-bundled, document="docs/sources/"+filename, **policy))
        lines = [f"# {name}", "", f"来源域名：`{h}`。共 {len(rows)} 条图片参考，覆盖 {len({m['id'] for m, _, _ in rows})} 个型号；{bundled} 张图片随仓库分发，其余为来源链接。", "", policy["summary"], ""]
        if policy["policy_url"]:
            lines += [f"[来源站的许可或使用条款]({policy['policy_url']}) · 核查日期：{rights['reviewed_date']}", ""]
        lines += ["原图链接指向来源网站或其图片 CDN，不表示图像已复制到本仓库。逐图的作者和许可按原记录保留。", "", "[返回全部来源网站](../PHOTO_SOURCES.md)", "", "| 型号 / 记录 | 视角或状态 | 作者 / 来源标注 | 原始页面 | 原图地址 | 收录方式 / 许可 |", "|---|---|---|---|---|---|"]
        for m, i, p in rows:
            permission = "仓库内图片：" + p["license"] if p["distribution"] == "bundled" else "来源链接；" + p["license"]
            lines.append(f"| {m['id']} · {label(m['name'])} · #{i} | {label(p['label'])} | {label(p['credit'])} | [来源网页]({target(p['source'])}) | [来源原图]({target(p.get('original_url') or p['url'])}) | {label(permission)} |")
        (folder / filename).write_text("\n".join(lines).rstrip()+"\n", encoding="utf-8")
    index = ["# 全部照片来源网站 / Complete photo source directory", "", f"本索引包含全部 **{d['stats']['photo_references']:,} 条图片参考**，包括未复制到仓库的 **{sum(s['reference_only'] for s in sites):,} 条来源链接**。按网站分组后，每条记录都列出型号、视角、作者或来源标注、原始页面、原图地址与许可状态。", "", "公开仓库内有明确许可的图片与外部来源链接分别标注。注明网站来源不代表已获再分发许可。", "", f"共 {len(sites)} 个来源网站；同一图像可能关联多个型号，因此记录数不等于独立图片数。", "", "| 来源网站 | 域名 | 型号条目 | 参考记录 | 仓库内图片 | 仅来源链接 |", "|---|---|---:|---:|---:|---:|"]
    for site in sites:
        relative = "sources/" + site["document"].rsplit("/", 1)[-1]
        index.append(f"| [{label(site['name'])}]({relative}) | {site['host']} | {site['models']} | {site['references']} | {site['bundled']} | {site['reference_only']} |")
    index += ["", "数据文件：[source-sites.json](../data/source-sites.json)；逐图完整记录：[catalog.json](../data/catalog.json)；仓库内图片署名：[ATTRIBUTION.md](ATTRIBUTION.md)。"]
    (ROOT / "docs/PHOTO_SOURCES.md").write_text("\n".join(index).rstrip()+"\n", encoding="utf-8")
    (ROOT / "data/source-sites.json").write_text(json.dumps(dict(reviewed_date=rights["reviewed_date"], sites=sites), ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"Updated {d['stats']['photo_references']} source records across {len(sites)} websites")


if __name__ == "__main__":
    update()
