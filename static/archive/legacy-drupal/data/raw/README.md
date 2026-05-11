# Legacy SBPL Raw Drupal SQL Dumps — Not Checked In

The original sbpl.net `data/raw/` folder contained two MySQL dumps
totalling roughly **184 MB**:

| File | Size | Date | Tables |
|------|------|------|--------|
| `dump-2018-04-12.sql` | ~161 MB | Apr 12, 2018 | 112 |
| `drupal_dump.sql`     | ~23 MB  | Nov 2014     | 88  |

They are intentionally **not committed to this repository in the initial
import PR** because:

1. Git LFS could not be configured in the migration environment (the
   GitHub release-assets host required to download `git-lfs` was
   unreachable),
2. Drupal dumps contain old `users` rows with hashed passwords, email
   addresses, and 27 000+ spam-bot registrations from the open-
   registration era — they should be reviewed and sanitised before
   public re-publication, and
3. The content of the dumps has already been extracted into the
   human-readable `archive/legacy-drupal/content/` and
   `archive/legacy-drupal/data/` trees, which are committed.

## To add the dumps via Git LFS (optional / private mirror only)

```bash
git lfs install
git lfs track "static/archive/legacy-drupal/data/raw/*.sql"
git add .gitattributes
git add static/archive/legacy-drupal/data/raw/*.sql
git commit -m "chore(archive): add raw Drupal SQL dumps via LFS"
git push
```

If publishing publicly, please first strip the `users`, `sessions`,
and `comments` tables (or at least the password / mail / IP columns)
so the dumps are safe to share.
