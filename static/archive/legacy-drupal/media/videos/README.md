# Legacy SBPL Video Assets — Not Checked In

The original sbpl.net `media/videos/` folder contained five video
files totalling roughly **559 MB**:

| File | Size |
|------|------|
| `manip1_collect.mp4`     | ~231 MB |
| `sbpl_flight_march17.mp4` | ~198 MB |
| `icra2_HD.mp4`            | ~117 MB |
| `crashes.mp4`             | ~7 MB   |
| `beam_graphs.mp4`         | ~6 MB   |

They are intentionally **not committed to this repository in the initial
import PR** because:

1. Git LFS could not be configured in the migration environment (the
   GitHub release-assets host required to download `git-lfs` was
   unreachable), and
2. Committing ~559 MB of binary blobs without LFS would bloat the repo
   permanently and slow every clone.

## To add the videos via Git LFS

On a workstation that has `git-lfs` installed:

```bash
git lfs install
git lfs track "static/archive/legacy-drupal/media/videos/*.mp4"
git add .gitattributes
# Copy the .mp4 files into this directory, then:
git add static/archive/legacy-drupal/media/videos/*.mp4
git commit -m "feat(archive): add legacy sbpl.net video assets via LFS"
git push
```

The source `.mp4` files live in the original on-disk extraction at
`newwebsite/media/videos/` (not in the repo). The clean-cut
catalogue of video URLs (YouTube embeds) is rendered on
[`/videos/`](/videos/).

A matching `.gitattributes` entry already declares
`static/archive/legacy-drupal/media/videos/*.mp4` for LFS — running
`git lfs track` above is mostly a no-op confirmation.
