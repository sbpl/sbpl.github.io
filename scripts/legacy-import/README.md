# Legacy `sbpl.net` Publication Import Scripts

These two scripts generated the entries under `content/publications/`. They
are committed for reproducibility — running them again will refresh the
catalogue if Maxim Likhachev's CMU publications page changes.

## Pipeline

### Step 1 — `01_import_from_sbpl_net_pdf_list.py`

Walks a hard-coded list of every `http://sbpl.net/files/*.pdf` URL that
appeared in the legacy Drupal access-log SQL dump
(`static/archive/legacy-drupal/data/raw/dump-2018-04-12.sql`, withheld
from this repo for privacy reasons).

For each filename it produces a `content/publications/<slug>.md` stub
with a **heuristic** title parsed from the filename slug, a venue+year
parsed from the trailing `_<conf><yy>` token, and a single-author list
of `Maxim Likhachev` (everyone else is flagged for verification).

This step exists so that the catalogue has 1:1 coverage of every PDF
that was hosted on the original sbpl.net file server through 2016.

### Step 2 — `02_rewrite_with_canonical_citations.py`

Fetches Maxim Likhachev's canonical publications page from
<https://www.cs.cmu.edu/~maxim/publications.html> (cached locally for
the run), parses each bullet, and rewrites every matching
`content/publications/<slug>.md` with:

- the canonical title
- the full author list in original order
- the proper venue label (short form for the card, long form in the body)
- any award (Best Paper, Honorable Mention, Influential Paper, etc.)
- the live PDF URL on `cs.cmu.edu/~maxim/files/`
- the abstract HTML URL where Maxim's page provides one

Slugs are matched by normalising the PDF basename
(`SBPlanningwithMotionPrims_icra10.pdf` →
`sbplanningwithmotionprims-icra10`). Papers Maxim has added since the
original sbpl.net file catalogue (2017–2022) are created automatically.

## Re-running

```bash
cd /path/to/sbpl.github.io
python3 scripts/legacy-import/01_import_from_sbpl_net_pdf_list.py
python3 scripts/legacy-import/02_rewrite_with_canonical_citations.py
```

Both scripts are idempotent — running them twice produces no further
diff once Maxim's page hasn't changed.

## Manual edits expected

Two pre-existing publication files were untouched because they aren't
on Maxim's page:

- `content/publications/mmd.md`
- `content/publications/xecbs.md`

Anything else that needs a fix (typo, missing co-author, etc.) should
be edited **in the generated `.md` file directly** — the next run of
the scripts will respect manual changes only in fields that are not in
the canonical source. A safer pattern is to fix the upstream listing
on Maxim's page and re-run script 2.
