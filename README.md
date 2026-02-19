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
     photo: "/images/members/your-full-name.jpg"
     bio: >
       A short paragraph about your research interests
       and background.
     links:
       website: "https://yoursite.com"      # optional
       scholar: "https://scholar.google..." # optional
       github: "https://github.com/you"     # optional
   ```
3. Add your headshot photo to `static/images/members/your-full-name.jpg`
   - Square aspect ratio (400×400px recommended)
   - JPEG format, reasonable file size (<500KB)
4. Commit and push. The site deploys automatically.

### Add a Publication

1. Create a new file `content/publications/short-descriptive-name.md`:
   ```yaml
   ---
   title: "Your Paper Title"
   date: 2025-06-15                # Publication date
   authors:                        # MUST match names in data/members/*.yaml
     - "Your Name"
     - "Coauthor Name"
     - "Maxim Likhachev"
   first_authors: 2                # optional: number of co-first authors
   venue: "ICRA 2025"
   description: "A one-sentence summary of the paper for the card view."
   thumbnail: "/images/publications/short-descriptive-name.gif"
   arxiv: "https://arxiv.org/abs/XXXX.XXXXX"          # optional
   project_page: "https://yourproject.github.io/"      # optional
   code: "https://github.com/your/repo"                # optional
   draft: false
   ---

   Optional extended abstract or description (rendered on the publication's page).
   ```
2. Add a thumbnail GIF/image to `static/images/publications/short-descriptive-name.gif`
   - Small animated GIF showing key result (~180×120px display, keep file <2MB)
3. **Important**: Make sure author names in the `authors` list match *exactly* how
   they appear in `data/members/current.yaml` or `data/members/alumni.yaml`.
   This is how publications auto-link to member profiles.
4. **Co-first authors**: To mark multiple authors as equal contributors, add
   `first_authors: N` where N is the number of co-first authors (counted from the
   top of the `authors` list). They will be displayed with a `*` superscript and an
   "Equal contribution" note.
5. Commit and push.

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
5. Commit and push. Their publications remain linked automatically.

### Update the PI Information

Edit `data/members/pi.yaml`. Fields:
- `name`, `title`, `photo`, `email`, `bio`, `research_vision`, `links`

---
## How Cross-Referencing Works

Publications and members are linked automatically via Hugo's **taxonomy** system:

1. Each publication lists its `authors` in front matter
2. Hugo auto-generates a page at `/authors/author-name/` listing all their papers
3. Member cards check `/authors/<slug>/` to count and link to that member's publications
4. **The key**: the `name` field in member YAML must exactly match the name string
   used in publication `authors` lists

This means:
- Adding a publication automatically updates every co-author's profile
- No need to manually maintain per-person publication lists
- Moving a member to alumni doesn't break their publication links

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
