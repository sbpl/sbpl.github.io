# SBPL — Search-Based Planning Lab Website

Static website for the Search-Based Planning Lab at Carnegie Mellon University.
Built with [Hugo](https://gohugo.io/) and [Pico.css](https://picocss.com/).

---

## Quick Start

### Prerequisites

- [Hugo](https://gohugo.io/installation/) (extended edition, v0.120+)

### Run Locally

```bash
hugo serve
```

Open [http://localhost:1313](http://localhost:1313) in your browser.
Changes are live-reloaded automatically.

---

## How To: Common Tasks

### Add Yourself as a Lab Member

1. Open `data/members/current.yaml`
2. Copy an existing entry and fill in your details:
   ```yaml
   - name: "Your Full Name"          # MUST match your name in publications exactly
     slug: "your-full-name"           # lowercase, hyphens (auto-generated from name)
     category: "phd"                  # phd | masters | undergraduate | postdoc
     year: "1st year"                 # optional
     enrollment: "RI PhD, Fall 2025"  # optional, shown next to your name on /people/
     co_advisor:                      # optional, shown as "(co-advised with <name>)"
       name: "Co-Advisor Name"
       website: "https://their-site.com"
     photo: "/images/members/your-full-name.jpg"
     bio: >
       A short paragraph about your research interests
       and background.
     links:
       website: "https://yoursite.com"      # optional; your name and photo link here
   ```
   Only `website` is shown on `/people/` (Google Scholar is shown for the advisor only).
3. Add your headshot photo to `static/images/members/your-full-name.jpg`
   - Portrait 2:3 aspect ratio (400×600px recommended); it is shown uncropped
   - JPEG format, reasonable file size (<500KB)
4. Commit and push. The site deploys automatically.

### Add a Publication

`/publications/` lists papers from 2024 on (`from_year` in
`content/publications/_index.md`), with links to Maxim's Google Scholar profile
for the full list. Older papers keep their files but aren't listed.

1. Create a new file `content/publications/short-descriptive-name.md`:
   ```yaml
   ---
   title: "Your Paper Title"
   date: 2025-06-15                # Publication date (the year sets its section)
   scholar_rank: 12                # optional: its position on Maxim's Google Scholar
                                   # profile (sorted by year). Within a year, papers with
                                   # a thumbnail come first, then all are ordered by
                                   # venue (`venue_order` in
                                   # content/publications/_index.md), then by this;
                                   # papers without one come first in their venue.
   authors:                        # MUST match names in data/members/*.yaml
     - "Your Name"
     - "Coauthor Name"
     - "Maxim Likhachev"
   first_authors: 2                # optional: number of co-first authors
   venue: "ICRA 2025"
   description: "A one-sentence summary of the paper for the card view."
   thumbnail: "/images/publications/short-descriptive-name.gif"  # image, GIF or short .mp4
   arxiv: "https://arxiv.org/abs/XXXX.XXXXX"          # [Paper] link (else pdf, then doi)
   doi: "https://doi.org/10.XXXX/XXXXX"                # optional
   project_page: "https://yourproject.github.io/"      # optional [Project Page] link
   code: "https://github.com/your/repo"                # optional
   draft: false
   ---

   Optional extended abstract or description (rendered on the publication's page).
   ```
2. Add a thumbnail to `static/images/publications/` and point `thumbnail` at it
   - An image, GIF, or short silent .mp4 clip showing the key result (shown 220px
     wide, at most 200px tall; keep files small, ideally <2MB). Clips loop while on screen.
3. **Co-first authors**: To mark multiple authors as equal contributors, add
   `first_authors: N` where N is the number of co-first authors (counted from the
   top of the `authors` list). They will be displayed with a `*` superscript and an
   "Equal contribution" note.
4. Commit and push.

### Move a Student to Alumni

1. Open `data/members/current.yaml`, find the student's entry
2. Cut (remove) their entire YAML block
3. Paste it into `data/members/alumni.yaml`
4. Add the `now_at` field and optionally a `graduated` year:
   ```yaml
   - name: "Student Name"
     slug: "student-name"
     category: "phd"
     graduated: "2025"
     now_at: "Research Scientist at Google DeepMind"
     # ... rest of their existing fields ...
   ```
5. Add a line for them to the right group (PhD, Master’s, …) in the `alumni`
   list at the top of `content/people/_index.md`; that list is what `/people/` shows.
6. Commit and push. Their publications remain linked automatically.

### Edit the Archive (Software, Videos, Tutorials) or Contact Pages

The **Archive** menu item opens a tabbed section under `content/archive/`
(the tabs are listed in `layouts/partials/archive-tabs.html`):

- **Software** (`content/archive/software.md`): each card is an item under `groups`
  in the front matter (`name`, `description`, `links` of `{label, url}`).
- **Videos** (`content/archive/videos.md`): add `{ id, title }` under a group, where
  `id` is the YouTube video ID (`youtube.com/watch?v=<id>`).
- **Tutorials** (`content/archive/tutorials/`): one page per tutorial; `weight` sets
  the order. The existing ones are the archived sbpl.net pages, kept as HTML.
- **Contact** (`content/contact.md`): plain HTML cards.

### Change the Homepage Photos

The homepage carousel shows every image in `static/images/lab-photos/`, in
filename order. Crop new photos to 4:3 (e.g. 1600×1200) before adding them.

### Change the Research Demos

The **Research Demos** under the lab description are the papers listed under
`demos` in `content/_index.md`, in that order. Each entry is a publication file
name from `content/publications/` without `.md`; its tile plays the paper's
`thumbnail` clip or GIF (no text) and links to its project page. To show a
different clip here than on `/publications/`, add `demo: "/images/…mp4"` to the
paper's front matter (DISCO uses this for its real-world runs).

### Update the PI Information

Edit `data/members/pi.yaml`. Fields:
- `name`, `title`, `photo`, `email`, `bio`, `links`

---
## How Pages Link Together

There are no per-person pages. On `/people/`, each member's name and photo link
straight to their `links.website`; on `/publications/`, author names are plain
text and each title links to the paper's project page or PDF.

## Deployment

The site auto-deploys to GitHub Pages via GitHub Actions on every push to `main`.

### First-Time Setup

1. Go to your GitHub repo → Settings → Pages
2. Under "Source", select "GitHub Actions"
3. Push to `main` — the workflow in `.github/workflows/deploy.yml` handles the rest

### Custom Domain

To use a custom domain (e.g., `sbpl.cs.cmu.edu`):
1. Add a `CNAME` file to `static/` containing your domain
2. Configure DNS to point to GitHub Pages
3. Update `baseURL` in `hugo.toml`
