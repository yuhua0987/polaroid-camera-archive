# Data format

`data/catalog.json` uses UTF-8 JSON, currently `schema_version: 1`.

Top-level fields are `title`, `schema_version`, `data_date`, `publication_date`,
`maintainer`, `scope`, `stats` and `models`.
Statistics distinguish photo **references** from unique referenced images and
images actually **bundled** in the public repository.

## Model record

| Field | Meaning |
| --- | --- |
| `id` | Stable identifier such as `P114`; do not recycle identifiers |
| `family` | Historical family / film grouping |
| `name` | Source-attributed model or version name |
| `sources` | Model-reference page URLs |
| `note` | Project-authored qualification or uncertainty |
| `kind` | Counting convention, generally a model / named version |
| `source_year` | Source's date text, not independently verified for every record |
| `views_recorded` | Labels observed across **all** photo references |
| `strict_views_pending` | Pure front / side / back labels still absent or unchecked |
| `photos` | Photo-reference records; may be empty |

## Photo reference

| Field | Meaning |
| --- | --- |
| `url`, `original_url` | Public source image URLs; they are references, not hosted copies |
| `source` | Original source page |
| `credit`, `title` | Author / provider and supplied title, where available |
| `label` | Actual angle or camera state; unknown views remain marked unknown |
| `license`, `license_url` | Source's license statement; null URL for unverified references |
| `origin` | Source family used during research |
| `width`, `height` | Dimensions of the image response recorded during research |
| `sha256` | Content hash of that recorded image response |
| `collected_date` | Research capture date |
| `distribution` | `bundled` or `reference-only` |
| `path`, `thumb` | Relative repository paths, present only for `bundled` media |

For `reference-only` entries, `path`, `thumb` and `license_url` are `null`.
The UI must never put `url` or `original_url` into an automatically loaded image.

`data/media-manifest.json` covers the bundled originals and thumbnails. It retains
author links, exact source-license URLs, source usage terms, hashes, snapshot
date and modification notices. A source-specific file license always takes
precedence over the project's software or catalog-compilation license.
