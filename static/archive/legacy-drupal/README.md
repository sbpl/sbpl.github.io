# SBPL Website Asset Bundle

This folder contains everything that was salvaged from the old
**Search-Based Planning Laboratory (SBPL)** Drupal 7 website so it can
be used as the source-of-truth for building a new website from scratch.

The original site lived at `sbpl.net` and was a Drupal 7 install. The
two snapshots on disk were:

- `dump-2018-04-12.sql` — the latest MySQL dump (Apr 12, 2018, 112 tables, 161 MB)
- `drupal_dump.sql`     — an older MySQL dump (Nov 2014, 88 tables, 23 MB)

All site-relevant content (page bodies, menus, user list, file refs,
images, videos, logos, and install notes) has been extracted and
copied here in a clean, human-readable layout.

> **Privacy / security note for this snapshot inside `sbpl.github.io`:**
> Before this archive was committed to a public repository, the following
> redactions were applied:
>
> - All user email addresses in `content/users.json` were partially
>   masked (first + last character of the local-part kept).
> - The Drupal `cron_key`, `drupal_private_key`, `smtp_password`, and
>   the FTP `username` in `data/drupal_variables.json` were replaced
>   with `***REDACTED***`.
> - The legacy contact-form recipient in `data/contact_categories.json`
>   was partially masked.
> - The `andrew.dornbush@gmail.com` address that appeared on the old
>   Contact page (`content/pages/0030-contact.*`) was partially masked.
> - The `username:` / `password:` credentials in the
>   `content/blocks/001-private-files.*` block were redacted (the
>   `sbpl.net/private/SBPL/` upload form no longer exists).
> - The two raw MySQL dumps (`data/raw/*.sql`, ~184 MB total) and the
>   five legacy video files (`media/videos/*.mp4`, ~559 MB total) were
>   **not** committed in this initial PR — see `media/videos/README.md`
>   and `data/raw/README.md` for instructions on adding them via Git LFS.
>
> The original, fully-unredacted extraction lives on the migration
> workstation under `~/Desktop/newsite/newwebsite/`.

---

## Folder map

```
newwebsite/
├── README.md                       this file
├── manifest.md                     full inventory of every file in here, with sizes + sources
├── requirements.txt                Python deps (stdlib-only)
├── scripts/
│   ├── extract.py                  re-runnable extractor (parses the SQL dump)
│   └── build_manifest.py           regenerates manifest.md by walking the tree
├── content/
│   ├── pages/                      one Drupal node per page (55 pages × 3 files)
│   │   ├── 0009-home.md            Markdown rendering
│   │   ├── 0009-home.html          original WYSIWYG HTML (links rewritten)
│   │   ├── 0009-home.json          {nid, title, type, dates, url_aliases, field_image, body_*, ...}
│   │   └── …(55 pages)
│   ├── blocks/                     custom HTML "blocks" (sidebar / footer text)
│   │   └── <bid>-<slug>.{html,md,json}
│   ├── blocks_index.json           index of all custom blocks
│   ├── menus.json                  decoded navigation tree (4 site menus)
│   ├── users.json                  real users (passwords stripped, spam removed, with roles)
│   └── site_variables.json         curated subset of Drupal variables (site_name, theme, …)
├── media/
│   ├── logos/                      sbpl_logo2_transparent.png + 70% variant
│   ├── images/                     all SBPL photos / figures from shared/Images
│   ├── pictures/                   user avatars
│   ├── uploads/                    misc Drupal uploads (sites/default/files/…)
│   │   └── SBPL/                   sbpl.tar.gz + sbpl.zip software downloads (+ index.html)
│   └── videos/                     all 5 video assets (manip, flight, crashes, icra2, beam_graphs)
├── data/
│   ├── pages_index.csv             nid,title,type,created,updated,uid,slug,url_aliases,file_*
│   ├── url_aliases.json            every Drupal URL alias, grouped by node id
│   ├── node_types.json             Drupal content-type definitions
│   ├── files_managed.json          decoded `file_managed` table
│   ├── file_usage.json             which entity (node/comment/user) uses each file
│   ├── page_field_image.json       per-page image-field values
│   ├── page_field_page_file.json   per-page file-attachment values
│   ├── page_field_tags.json        per-page taxonomy tags
│   ├── taxonomy.json               vocabularies + terms + node→tag links
│   ├── comments.json               page comments (subject + body + author)
│   ├── roles.json                  Drupal roles + their permissions
│   ├── contact_categories.json     Drupal contact-form categories
│   ├── text_formats.json           text-format / WYSIWYG-filter definitions
│   ├── drupal_variables.json       all 180 `variable` rows (PHP-decoded)
│   └── raw/
│       ├── dump-2018-04-12.sql     verbatim copy of the latest dump
│       └── drupal_dump.sql         verbatim copy of the older dump
└── reference/
    ├── website_installation_procedure.md   original install guide
    └── original_settings.php               original Drupal settings (DB password redacted)
```

---

## How to use this for a new website

The cleanest input for a static-site generator (Astro / Next.js /
Hugo / 11ty) is the per-page triplet under `content/pages/`:

- **`0009-home.json`** — front-matter (title, dates, author, etc.). Use this to feed the build pipeline.
- **`0009-home.md`** — Markdown body, ready to drop into a Markdown-driven SSG. Asset URLs have been rewritten to point at `../../media/`.
- **`0009-home.html`** — original WYSIWYG HTML, kept verbatim (with rewritten asset URLs) in case the Markdown conversion lost some formatting and you need to re-render parts.

`content/menus.json` is the original Drupal navigation tree — use it to
seed the new site's nav. Items pointing at `node/<nid>` map to the
matching `<nid>-<slug>.{md,html,json}` file.

`content/users.json` lists the 25 real user accounts (anonymous + admin
+ 23 lab members who either authored a page or logged in at least
once). The 27,466 spam-bot registrations from the open-registration
era are filtered out. Combine with the `pages/` triplets that match a
member's name to assemble the new "People" page.

`data/files_managed.json` is the original Drupal file-tracking table.
Cross-reference its `uri` field (e.g. `public://Images/3jZ04.png`)
with the asset paths under `media/uploads/` and `media/images/`.

---

## Re-running the extractor

```bash
cd newwebsite
python3 scripts/extract.py        # rebuild content/ + data/ from the SQL dump
python3 scripts/build_manifest.py # refresh manifest.md
```

The extractor streams `../dump-2018-04-12.sql`, decodes the relevant
tables, and overwrites everything under `content/` and `data/`
(except `data/raw/`, which is just verbatim copies of the SQL dumps).

Both scripts use **only the Python 3 standard library**, so no
`pip install` step is required.

## Quick stats

- 55 pages × 3 files = 165 files under `content/pages/`
- 2 custom blocks × 3 files = 6 files under `content/blocks/`
- 77 source images in `media/images/` plus 77 thumbnails in `media/images/_thumbs/` (~22 MB total)
- 3 user-avatar pictures in `media/pictures/`
- 12 misc upload files in `media/uploads/` (~7 MB; includes `sbpl.tar.gz` + `sbpl.zip` software downloads)
- 5 videos in `media/videos/` (~559 MB)
- 25 real user records in `content/users.json` (passwords stripped; 27,466 spam registrations filtered out)
- 52 navigation links across 4 site menus in `content/menus.json` (admin / management menus dropped)
- 46 URL aliases in `data/url_aliases.json` — used to rewrite intra-site `<a href="AndrewDornbush">` links to local page files
- 4 roles + 144 permissions in `data/roles.json`
- 4 text formats in `data/text_formats.json`
- 180 site variables in `data/drupal_variables.json` (curated subset of 12 in `content/site_variables.json`)
- 85 local references across all extracted page HTML, **all** verified to resolve under the bundle (zero broken links)

---

## Provenance / notes

- The Drupal core code (`drupal-7.33/`, `drupal-7.58/`, `*.tar.gz`,
  `sites/all/modules/`) is intentionally **not** included here — it is
  generic Drupal 7 + contributed modules and not SBPL content. The
  original folders on disk still have it if you ever need it.
- Image references in page bodies originally pointed at
  `/shared/Images/...` (served from a sibling Apache alias). These
  have been rewritten to `../../media/images/...` so all links resolve
  inside this folder.
- Each page JSON keeps three forms of the body:
  `body_html_raw` (verbatim from the SQL dump),
  `body_html_rewritten` (asset URLs pointed at `../../media/...` _and_
  intra-site URL aliases like `AndrewDornbush` rewritten to
  `0015-andrew-dornbush.html`), and `body_markdown` (the cleaned
  Markdown rendering). Use whichever fits your build pipeline.
- Custom HTML blocks in `content/blocks/` include one labeled
  `private files` whose body still contains the original
  `username/password` from the old site. That's how it lived in the DB;
  we kept it verbatim so nothing is lost. **Don't reuse those credentials**
  — they need to be replaced with proper authentication on the new site.
