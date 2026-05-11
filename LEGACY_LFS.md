# Legacy Drupal Import — Files Tracked for Git LFS

The initial import of the legacy `sbpl.net` Drupal 7 site (see the
`feat(legacy): import sbpl.net content` PR) drops the entire extracted
snapshot into `static/archive/legacy-drupal/`. Two subdirectories of
that snapshot are **not** committed in the initial PR:

| Path | Size | Reason |
|------|------|--------|
| `static/archive/legacy-drupal/media/videos/` | ~559 MB (5 `.mp4`) | Too large without LFS; migration environment couldn't install `git-lfs` |
| `static/archive/legacy-drupal/data/raw/`     | ~184 MB (2 `.sql`)  | Same as above; also need sanitisation (passwords, spam users) before public hosting |

Both folders have a stub `README.md` explaining what is missing and how
to add it.

## Adding the missing files on a workstation with Git LFS

```bash
# 1. Make sure git-lfs is installed locally
git lfs install

# 2. Tracking rules are already in .gitattributes:
#    static/archive/legacy-drupal/media/videos/*.mp4 filter=lfs ...
#    static/archive/legacy-drupal/data/raw/*.sql     filter=lfs ...
#    (no additional `git lfs track` needed — but it doesn't hurt)

# 3. Drop the files in
cp /path/to/extracted/newwebsite/media/videos/*.mp4 \
   static/archive/legacy-drupal/media/videos/
cp /path/to/extracted/newwebsite/data/raw/*.sql \
   static/archive/legacy-drupal/data/raw/

# 4. Commit on this PR's branch (or a follow-up)
git add static/archive/legacy-drupal/media/videos/*.mp4
git add static/archive/legacy-drupal/data/raw/*.sql
git commit -m "feat(archive): add legacy videos and Drupal dumps via LFS"
git push
```

## GitHub LFS storage / bandwidth budget

Free GitHub accounts get **1 GB of LFS storage** and **1 GB of LFS
bandwidth/month**. The `sbpl` organisation may already have a paid
plan; if not, the 743 MB total of videos + dumps will fit under the
free quota, but downloading them through the `sbpl.github.io` site
deploys (GitHub Pages clones the repo into the runner) will consume
bandwidth on every build. Two options to keep bandwidth low:

1. Keep the LFS files in the repo but exclude
   `static/archive/legacy-drupal/media/videos/` from the published site
   via `[markup] -> [outputFormats]` or by moving them out of `static/`
   into a non-static folder like `archive/`.
2. Host the videos and SQL dumps on an external archive (Internet
   Archive, CMU Box, etc.) and just link to them from
   `/archive/legacy-drupal/media/videos/README.md`.

## What is in the snapshot

See `static/archive/legacy-drupal/README.md` and
`static/archive/legacy-drupal/manifest.md` for the full inventory. The
short version:

- 55 page triplets (`*.md` / `*.html` / `*.json`)
- 25 historical lab member pages (already promoted to
  `data/members/alumni.yaml`)
- 77 site images, 3 user avatars, 12 misc uploads (~22 MB, **committed
  to repo** under `static/archive/legacy-drupal/media/`)
- 5 videos (**deferred to LFS**)
- 2 raw SQL dumps (**deferred to LFS**)
- All Drupal metadata: users, menus, taxonomies, comments, roles,
  permissions, contact categories, text formats, ~180 site variables
