# Legacy SBPL Video Assets — Awaiting LFS Push from a Maintainer

The five video files from the original sbpl.net `media/videos/` folder
**are not yet committed** to this repository, but the scaffolding is in
place so a maintainer with write access to `sbpl/sbpl.github.io` can
add them in a single push.

| File                       | Size    | sha256 (from the workstation extraction) |
|----------------------------|---------|-------------------------------------------|
| `manip1_collect.mp4`       | ~241 MB | (compute on add)                          |
| `sbpl_flight_march17.mp4`  | ~207 MB | (compute on add)                          |
| `icra2_HD.mp4`             | ~122 MB | (compute on add)                          |
| `beam_graphs.mp4`          | ~9 MB   | (compute on add)                          |
| `crashes1.wmv`             | ~6 MB   | (compute on add)                          |

## Why aren't they in the PR?

The PR is opened from a **public fork** (`PegasusGTV/sbpl.github.io`).
GitHub does not allow public forks to upload new LFS objects to their
LFS namespace — they share LFS storage with the upstream parent, and
upstream-write permission is required for new objects. The migration
account does not currently have push permission on
`sbpl/sbpl.github.io`, so the videos couldn't be uploaded directly.

The `.gitattributes` file at the repo root already declares
`static/archive/legacy-drupal/media/videos/*.{mp4,wmv,avi,mov}` as
Git LFS-tracked, so dropping the files in and committing them will
route them to LFS automatically — no further configuration is needed.

## To add the videos

On a machine with `git-lfs` installed and **push access to
`sbpl/sbpl.github.io`** (i.e. a maintainer):

```bash
git lfs install                                    # one-time per machine
git clone git@github.com:sbpl/sbpl.github.io.git
cd sbpl.github.io
git checkout import-legacy-sbpl-net-content        # after merging the PR, this is `main`

# Copy the .mp4 / .wmv files in from wherever the workstation extraction lives:
cp /path/to/newwebsite/media/videos/*.mp4 \
   static/archive/legacy-drupal/media/videos/
cp /path/to/newwebsite/media/videos/*.wmv \
   static/archive/legacy-drupal/media/videos/

# Remove this README and commit the videos as LFS:
git rm static/archive/legacy-drupal/media/videos/README.md
git add static/archive/legacy-drupal/media/videos/*.mp4 \
        static/archive/legacy-drupal/media/videos/*.wmv
git commit -m "feat(archive): add legacy sbpl.net video assets via Git LFS"
git push
```

After the push, `git lfs ls-files` should list all five video files.

## Want to keep them out of LFS entirely?

If the maintainers prefer to avoid GitHub LFS bandwidth costs, two
alternatives that keep the archive structure intact:

1. **Mirror to Internet Archive / CMU Box** — upload the videos there
   and replace this README with a list of permanent external URLs.
2. **Move out of `static/`** — the `static/` directory ships with
   every GitHub-Pages deploy; moving the videos to a sibling
   non-static `archive/` folder keeps them in the repo for posterity
   but stops them from being served at every deploy.

See [`/LEGACY_LFS.md`](/LEGACY_LFS.md) at the repo root for the longer
discussion of LFS quotas and bandwidth.
