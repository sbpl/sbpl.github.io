# Legacy SBPL Raw Drupal SQL Dumps — Held Back for Privacy Review

The original sbpl.net `data/raw/` folder contained two MySQL dumps
totalling roughly **184 MB**:

| File | Size | Date | Tables |
|------|------|------|--------|
| `dump-2018-04-12.sql` | ~161 MB | Apr 12, 2018 | 112 |
| `drupal_dump.sql`     | ~23 MB  | Nov 2014     | 88  |

They are **not** committed to this repository — even though Git LFS is
now configured and the videos in `../../media/videos/` are checked in —
because the raw dumps contain personally identifiable information that
the rest of this archive has already redacted:

- Real lab-member email addresses (in the `users` table)
- Hashed user passwords (Drupal 7 `phpass`)
- Client IP addresses (in `sessions`, `comments`, `accesslog`)
- ~27 466 spam-bot registrations (from the open-registration era)
- The original SMTP password and other site secrets (in the
  `variable` table) — these are already `***REDACTED***` in the
  extracted `data/drupal_variables.json` but still present in the
  raw dumps

Everything *non-sensitive* in the dumps has already been extracted into
the readable JSON / Markdown trees in the surrounding `content/` and
`data/` directories (with the appropriate redactions applied). If you
specifically need the raw dumps, please:

1. Sanitise them first — drop or column-redact the `users`,
   `sessions`, `comments`, `accesslog`, and `variable` tables.
2. Then commit them via Git LFS — the `.gitattributes` rule
   `static/archive/legacy-drupal/data/raw/*.sql filter=lfs ...` is
   already in place, so a simple `git add *.sql && git commit && git push`
   will route the files to LFS automatically.
3. Or — preferably — keep them out of the public repo entirely and
   archive them on internal storage (CMU Box, Internet Archive
   private item, etc.).

The unredacted dumps remain on the migration workstation under
`~/Desktop/newsite/newwebsite/data/raw/` for anyone with legitimate
access who wants to do the sanitisation work.
