# Legacy Drupal Import — Files Tracked for Git LFS

The legacy `sbpl.net` Drupal 7 import (see the
`feat(legacy): import sbpl.net content` PR) drops the entire extracted
snapshot into `static/archive/legacy-drupal/`. Two subdirectories
contain assets too large to commit as ordinary blobs:

| Path | Size | Status in repo |
|------|------|----------------|
| `static/archive/legacy-drupal/media/videos/` | ~585 MB (4 `.mp4` + 1 `.wmv`) | **Scaffold only** — `.gitattributes` is ready; needs a maintainer with push access to `sbpl/sbpl.github.io` to add the binaries (see folder's README) |
| `static/archive/legacy-drupal/data/raw/`     | ~184 MB (2 `.sql`)            | **Held back** — also needs PII sanitisation before any LFS push (see folder's README) |

### Why the videos couldn't be added from the fork

GitHub does not allow **public forks** to upload new objects to LFS
storage — the fork shares its LFS namespace with the upstream parent,
and upstream-write permission is required to push new blobs. The PR
was opened from `PegasusGTV/sbpl.github.io` (a public fork) by a
contributor whose account is a member of the `sbpl` org but doesn't
hold individual push permission on `sbpl/sbpl.github.io`.

The fix is simple: after the PR is merged (or before, on this same
branch), any maintainer with push access to `sbpl/sbpl.github.io`
clones the repo, drops the `.mp4` / `.wmv` files into
`static/archive/legacy-drupal/media/videos/`, and commits. The
`.gitattributes` rules already route those file types to LFS
automatically, so the commit-and-push step is one line each.
The full step-by-step is in
[`static/archive/legacy-drupal/media/videos/README.md`](static/archive/legacy-drupal/media/videos/README.md).

### Videos (5 files)

| File                       | Size    |
|----------------------------|---------|
| `manip1_collect.mp4`       | ~241 MB |
| `sbpl_flight_march17.mp4`  | ~207 MB |
| `icra2_HD.mp4`             | ~122 MB |
| `beam_graphs.mp4`          | ~9 MB   |
| `crashes1.wmv`             | ~6 MB   |

### SQL dumps (held back)

The two raw MySQL dumps (`dump-2018-04-12.sql`, `drupal_dump.sql`) are
**not** committed in this PR even though the `.gitattributes` rules
are in place. They contain real lab-member emails, password hashes,
IP addresses, the 27 466 spam-bot registrations, and the
SMTP/private/cron keys that the rest of this archive has already
redacted. See
[`static/archive/legacy-drupal/data/raw/README.md`](static/archive/legacy-drupal/data/raw/README.md)
for the sanitisation checklist.

## Adding the SQL dumps later (after sanitisation)

```bash
# 1. Make sure git-lfs is installed locally
git lfs install

# 2. Tracking rules are already in .gitattributes:
#    static/archive/legacy-drupal/data/raw/*.sql filter=lfs ...

# 3. Drop the sanitised dumps in (see data/raw/README.md for what to strip)
cp /path/to/sanitised/dumps/*.sql \
   static/archive/legacy-drupal/data/raw/

# 4. Commit
git add static/archive/legacy-drupal/data/raw/*.sql
git commit -m "feat(archive): add sanitised Drupal dumps via LFS"
git push
```

## GitHub LFS storage / bandwidth budget — important

GitHub LFS pricing as of 2025: each account (user or org) gets
**1 GB of LFS storage** and **1 GB of LFS bandwidth/month** by default.
The five SBPL videos total ~585 MB, which fits in the free quota
comfortably for **storage**, but a few things to be aware of for
**bandwidth**:

1. **Every GitHub-Actions build (Hugo deploy) that fetches LFS will
   eat bandwidth.** The current `.github/workflows/deploy.yml` does
   **not** pull LFS by default, so site deploys won't accidentally
   drain the 1 GB/month quota — but the trade-off is that the videos
   won't be available at `/archive/legacy-drupal/media/videos/*.mp4`
   on the live site. To serve them publicly, add `with: lfs: true` to
   the `actions/checkout@v4` step in `deploy.yml`, **and** confirm
   that the `sbpl` org has enough bandwidth budget.

2. **Cheaper alternative:** keep the LFS scaffold (this README + the
   `.gitattributes` rules) but host the actual `.mp4` blobs on a
   neutral mirror like the Internet Archive or CMU Box, and edit the
   `/videos/` page to link directly to those external URLs. The
   YouTube embeds already on `/videos/` are usually enough for
   reviewers — the raw `.mp4`s exist mostly for archival and
   re-encoding purposes.

## What is in the snapshot

See `static/archive/legacy-drupal/README.md` and
`static/archive/legacy-drupal/manifest.md` for the full inventory. The
short version:

- 55 page triplets (`*.md` / `*.html` / `*.json`)
- 25 historical lab member pages (already promoted to
  `data/members/alumni.yaml`)
- 77 site images, 3 user avatars, 12 misc uploads (~22 MB, **committed
  to repo** under `static/archive/legacy-drupal/media/`)
- 5 videos (**scaffold only**; needs maintainer with `sbpl` push to commit — see `media/videos/README.md`)
- 2 raw SQL dumps (**held back**, see `data/raw/README.md`)
- All Drupal metadata: users, menus, taxonomies, comments, roles,
  permissions, contact categories, text formats, ~180 site variables
