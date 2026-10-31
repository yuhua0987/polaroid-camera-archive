# Polaroid Camera Archive

An independent, source-linked catalog of historical Polaroid instant cameras,
maintained by [yuhua0987](https://github.com/yuhua0987).

[中文说明](README.md) · [Model coverage](docs/COVERAGE.md) · [Image credits](docs/ATTRIBUTION.md)

The 2026-10-31 snapshot contains **378 catalog names / versions across 16 families**,
**1,207 photo references** covering **1,206 distinct images**, and **151 bundled,
openly licensed images** illustrating 57 entries. Another six entries have no
verified camera-photo reference. Names include generations, regional badges and
selected special-purpose versions; this is not an official model total or a
count of distinct body designs.

The static viewer supports family/name search, view filtering, missing-view
lists, attribution details and keyboard photo navigation. Oblique views and
folded state are recorded separately; full three-view coverage is incomplete.

Download and extract the repository, then open **index.html**. All bundled images,
catalog data and viewer code work offline. Other records provide source-page
links only; the viewer does not hotlink those images.

To build or check the project, use Python 3.10+ with no third-party dependencies:

```sh
python3 tools/validate.py
python3 tools/build.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open <http://127.0.0.1:8000>. After editing `web/`, run
`python3 tools/build.py --output .` to refresh the committed offline entry point.

Original software is MIT-licensed. Original catalog compilation/annotations are
CC BY-SA 4.0, subject to source rights. **Photos retain their individual licenses;
MIT does not apply to them.** Source images with unverified redistribution rights
are linked, not bundled. See [NOTICE](NOTICE.md), [data terms](data/LICENSE.md),
[source credits](docs/SOURCES.md) and [image attributions](docs/ATTRIBUTION.md).

Contributions should include a model ID, an identifiable source and explicit
photo-license evidence. See [CONTRIBUTING](CONTRIBUTING.md).
The project is not affiliated with or endorsed by Polaroid.
