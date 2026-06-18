#!/usr/bin/env python3
"""
Parse Maxim Likhachev's canonical publications page and rewrite every Hugo
publication stub with the correct title, authors, venue, year, and any award.

Source of truth: https://www.cs.cmu.edu/~maxim/publications.html
(saved locally to AGENT_TOOL_FILE)
"""
import os, re, sys

"""
By default this script reads a cached copy of Maxim Likhachev's publications
page placed next to it as `maxim_publications_cached.md`. If that file is
missing the script will try to download a fresh copy with `urllib`.

  python3 02_rewrite_with_canonical_citations.py
"""

import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
CACHED_PAGE = os.path.join(HERE, 'maxim_publications_cached.md')
PUB_DIR = os.path.join(REPO_ROOT, 'content', 'publications')
PUB_URL = 'https://www.cs.cmu.edu/~maxim/publications.html'

if not os.path.exists(CACHED_PAGE):
    print(f'Fetching {PUB_URL}...', file=sys.stderr)
    with urllib.request.urlopen(PUB_URL) as resp:
        html = resp.read().decode('utf-8', 'replace')
    # very light HTML→markdown: keep [text](url) links, drop tags
    text = re.sub(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', html, flags=re.I|re.S)
    text = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1', text, flags=re.I|re.S)
    text = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', text, flags=re.I|re.S)
    text = re.sub(r'<[^>]+>', '', text)
    with open(CACHED_PAGE, 'w') as f:
        f.write(text)

AGENT_TOOL_FILE = CACHED_PAGE

with open(AGENT_TOOL_FILE, encoding='utf-8') as f:
    text = f.read()

# Walk through the page section by section
SECTIONS = {
    'Journal and Magazine Articles': 'journal',
    'Full-length Conference Publications': 'conference',
    'Workshop and Short Conference Publications': 'workshop',
    'Thesis': 'thesis',
}

records = {}  # slug (normalized) -> {title, authors, venue, year, type, award, pdf, abs_url}

def normalize_slug(s):
    """Turn a raw PDF basename into our Hugo filename slug convention."""
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    s = re.sub(r'-+', '-', s)
    return s

# Track current section
current_section_type = None
lines = text.splitlines()
for line in lines:
    # Section detection
    m = re.match(r'^####\s+(.*)', line)
    if m:
        heading = m.group(1).strip()
        current_section_type = None
        for needle, kind in SECTIONS.items():
            if needle in heading:
                current_section_type = kind
                break
        continue

    if not line.startswith('- ') or current_section_type in (None, 'thesis'):
        continue

    # Find any PDF link in this bullet
    pdf_m = re.search(r'\[(?:Full version|Full preprint version|PDF file)\s*\(PDF\)\]\((https?://[^\)]+\.pdf)\)', line)
    if not pdf_m:
        # try generic [PDF file](url.pdf)
        pdf_m = re.search(r'\[PDF file\]\((https?://[^\)]+\.pdf)\)', line)
    if not pdf_m:
        continue
    pdf_url = pdf_m.group(1)
    pdf_base = os.path.basename(pdf_url)
    pdf_stem = re.sub(r'\.pdf$', '', pdf_base, flags=re.IGNORECASE)
    slug = normalize_slug(pdf_stem)

    # Optional abstract link
    abs_m = re.search(r'\[Abstract\s*\(HTML\)\]\((https?://[^\)]+)\)', line)
    abs_url = abs_m.group(1) if abs_m else None

    # Strip the line down to just the human-readable citation (no markdown links)
    citation = line[2:]  # drop "- "
    # Remove every "[...](...)" block
    citation = re.sub(r'\[[^\]]*\]\([^\)]*\)', '', citation)
    citation = citation.strip().strip('.').strip()

    # Title is between the first paired delimiter. Maxim's page uses both `"`
    # and the literal text `&quot` (HTML entity, end-only) as quote markers.
    # Normalise: replace `&quot;` (rare) and `&quot` with `"`
    citation_norm = citation.replace('&quot;', '"').replace('&quot', '"')
    # Match: authors,? "title," venue... year
    # The title is the first balanced "..." region.
    t_m = re.search(r'"([^"]+?),?\s*"', citation_norm)
    if not t_m:
        # Try with a single trailing quote / smart quote
        t_m = re.search(r'"([^"]+?)"', citation_norm)
    if not t_m:
        print(f'WARN: could not extract title from: {citation_norm[:120]}', file=sys.stderr)
        continue
    title = t_m.group(1).strip().rstrip(',').strip()
    authors_raw = citation_norm[:t_m.start()].strip().rstrip(',').strip()
    venue_raw   = citation_norm[t_m.end():].strip().lstrip(',').strip()

    # Year: last 4-digit number in venue
    year_m = re.findall(r'\b(19|20)(\d{2})\b', venue_raw)
    year = None
    if year_m:
        year = int(year_m[-1][0] + year_m[-1][1])

    # Award: phrases in parens after year (don't strip these from venue here;
    # we leave acronym-only parens like "(ICRA)" intact for short_venue matching)
    award = None
    aw_m = re.search(r'\(([^)]*?(?:Award|Honorable Mention|invited paper|Best Paper|Best Student Paper|oral presentation|Poster Abstract)[^)]*)\)', venue_raw, re.IGNORECASE)
    if aw_m:
        award = aw_m.group(1).strip()
        # Drop only the award parens from the venue string
        venue_raw = venue_raw.replace(aw_m.group(0), '')

    venue = re.sub(r'\.\s*$', '', venue_raw).strip().rstrip(',').strip()

    # Split authors on ", and " or " and " or commas
    parts = re.split(r',\s*and\s+|\s+and\s+|,\s*', authors_raw)
    authors = [a.strip() for a in parts if a.strip()]
    # Filter out junk fragments
    authors = [a for a in authors if not re.match(r'^(by|et\s+al\.?|al\.?)$', a, re.IGNORECASE)]

    records[slug] = {
        'title': title,
        'authors': authors,
        'venue': venue,
        'year': year,
        'type': current_section_type,
        'award': award,
        'pdf': pdf_url,
        'abs_url': abs_url,
        'pdf_stem': pdf_stem,
    }

print(f'Parsed {len(records)} canonical citations from Maxim\'s publications page.', file=sys.stderr)

# Map: which Hugo files do I have? Build slug -> filename
hugo_files = {}
for fn in sorted(os.listdir(PUB_DIR)):
    if not fn.endswith('.md') or fn == '_index.md':
        continue
    stem = fn[:-3]
    hugo_files[stem] = os.path.join(PUB_DIR, fn)

# Also build alternate slug lookup so we can match e.g. record slug
# 'sbplanningwithmotionprims-icra10' to hugo filename 'sbpl-manipulation-icra-2010'
# We will primarily rely on record slug matching since I generated stubs from
# the same PDF basenames. The 9 hand-curated files have different names but
# share a PDF; we will match them by mapping their `project_page` instead.
HAND_CURATED_MAP = {
    'lattice-rss-2008':         'planlongdynfeasmotions-rss08',
    'sbpl-manipulation-icra-2010': 'sbplanningwithmotionprims-icra10',
    'arm-adaptive-primitives-icra-2011': 'armplanwithadaptmprim-icra11',
    'dual-arm-icra-2012':       'dualarmplanning-icra12',
    'sipp-icra-2011':           'sipp-icra11',
    'cfdaa-aaai-2011':          'cfdaa-aaai11',
    'egraphs-rss-2012':         'egraph-rss12',
    'anytime-egraphs-icra-2013':'anytimeincrementalegraphs-icra13',
    'd2p':                      'searchwithlearningforperception-rss16',
}

# Build venue label heuristic (e.g. shorten "Proceedings of the IEEE International Conference on Robotics and Automation (ICRA)")
VENUE_SHORTS = [
    ('IEEE International Conference on Robotics and Automation (ICRA)', 'ICRA'),
    ('IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)', 'IROS'),
    ('Robotics: Science and Systems Conference (RSS)', 'RSS'),
    ('Robotics: Science and Systems', 'RSS'),
    ('International Joint Conference on Artificial Intelligence (IJCAI)', 'IJCAI'),
    ('National Conference on Artificial Intelligence (AAAI)', 'AAAI'),
    ('International Conference on Automated Planning and Scheduling (ICAPS)', 'ICAPS'),
    ('International Symposium on Combinatorial Search (SoCS)', 'SoCS'),
    ('International Joint Conference on Autonomous Agents and Multiagent Systems (AAMAS)', 'AAMAS'),
    ('International Conference on Machine Learning (ICML)', 'ICML'),
    ('Advances in Neural Information Processing Systems', 'NeurIPS (formerly NIPS)'),
    ('IEEE Transactions on Robotics', 'IEEE T-RO'),
    ('IEEE Robotics and Automation Magazine', 'IEEE RA-M'),
    ('Artificial Intelligence Journal (AIJ)', 'AIJ'),
    ('Artificial Intelligence Magazine', 'AI Magazine'),
    ('International Journal of Robotics Research (IJRR)', 'IJRR'),
    ('Journal of Field Robotics (JFR)', 'JFR'),
    ('Autonomous Robots (AURO)', 'AURO'),
    ('Lecture Notes in Artificial Intelligence', 'LNAI'),
    ('IEEE Intelligent Vehicles Symposium (IV)', 'IEEE IV'),
    ('IEEE-RAS International Conference on Humanoid Robots', 'Humanoids'),
    ('Army Science Conference (ASC)', 'ASC'),
    ('AAAI Conference on Artificial Intelligence and Interactive Digital Entertainment (AIIDE)', 'AIIDE'),
    ('Artificial Intelligence and Interactive Digital Entertainment Conference (AIIDE)', 'AIIDE'),
    ('Twelfth Conference on Artificial Intelligence and Interactive Digital Entertainment (AIIDE)', 'AIIDE'),
    ('Eight Conference on Artificial Intelligence and Interactive Digital Entertainment (AIIDE)', 'AIIDE'),
    ('International Conference on Computer Vision (ICCV)', 'ICCV'),
    ('SIGGRAPH Symposium on Interactive 3D Graphics and Games (I3D)', 'I3D'),
    ('International Conference on Unmanned Aircraft Systems', 'ICUAS'),
    ('ICRA Workshop on Planning with Cost Maps', 'ICRA Workshop'),
    ('ICAPS Workshop on Planning under Uncertainty for Autonomous Systems', 'ICAPS Workshop'),
    ('Digital Audio Effects (DAFx)', 'DAFx'),
    ('NVIDIA GPU Technology Conference', 'NVIDIA GTC'),
    ('SPIE: Sensor Fusion and Decentralized Control in Robotic Systems', 'SPIE'),
]

def short_venue(venue_full, year):
    # First try with the full text (acronyms still in parens)
    for pat, short in VENUE_SHORTS:
        if pat in venue_full:
            return f"{short} {year}" if year else short
    # Try matching by acronym present in any parens, e.g. "(SoCS)"
    acro_m = re.search(r'\(([A-Z][A-Za-z0-9-]{1,12})\)', venue_full)
    if acro_m:
        return f"{acro_m.group(1)} {year}" if year else acro_m.group(1)
    # generic fallback: strip "Proceedings of the" and Vol.# tail
    v = re.sub(r'^Proceedings of (the )?', '', venue_full)
    v = re.sub(r',\s*Vol\.\s*\d+.*', '', v)
    v = re.sub(r'\(\s*\)', '', v).strip().rstrip(',').strip()
    if year and not str(year) in v:
        v = f"{v}, {year}"
    return v or (f"Venue {year}" if year else "Venue")

def clean_venue_text(s):
    """Strip empty parens, dangling commas, double-spaces left after `()` removal."""
    s = re.sub(r'\(\s*\)', '', s)        # empty parens
    s = re.sub(r'\s{2,}', ' ', s)        # collapse spaces
    s = re.sub(r'\s+,', ',', s)          # space before comma
    s = re.sub(r',\s*,', ',', s)         # double commas
    s = s.strip().rstrip(',').strip()
    return s

def write_md(path, rec, slug_stem):
    yaml_authors = '\n'.join(f'  - "{a}"' for a in rec['authors'])
    award_line = f'award: "{rec["award"]}"\n' if rec['award'] else ''
    abs_line = f'abstract_html: "{rec["abs_url"]}"\n' if rec.get('abs_url') else ''
    date = f"{rec['year']}-01-01" if rec['year'] else "2010-01-01"
    venue_short = short_venue(rec['venue'], rec['year'])
    venue_long = clean_venue_text(rec['venue'])
    if rec['year'] and str(rec['year']) not in venue_long:
        venue_long = f"{venue_long}, {rec['year']}"

    # Hugo YAML title escaping: replace literal `"` and trailing `*`
    safe_title = rec['title'].replace('"', '\\"')

    body = f"""---
title: "{safe_title}"
date: {date}
authors:
{yaml_authors}
venue: "{venue_short}"
{award_line}publication_type: "{rec['type']}"
pdf: "{rec['pdf']}"
{abs_line}draft: false
---

Published in *{venue_long}*.{(' **' + rec['award'] + '.**') if rec['award'] else ''}

<!-- Canonical citation sourced from Maxim Likhachev's CMU publications page
(https://www.cs.cmu.edu/~maxim/publications.html). If you spot an error, edit
this file's frontmatter and submit a PR. -->
"""
    with open(path, 'w') as f:
        f.write(body)

# Process matches
updated, created, unmatched_hugo, unmatched_record = [], [], [], []

# 1) Direct slug match: hugo file basename == normalized record slug
record_used = set()
for hugo_stem, hugo_path in hugo_files.items():
    if hugo_stem in records:
        write_md(hugo_path, records[hugo_stem], hugo_stem)
        record_used.add(hugo_stem)
        updated.append(hugo_stem)
        continue
    # Hand-curated mapping
    if hugo_stem in HAND_CURATED_MAP:
        target = HAND_CURATED_MAP[hugo_stem]
        if target in records:
            write_md(hugo_path, records[target], hugo_stem)
            record_used.add(target)
            updated.append(hugo_stem + ' (via map)')
            continue
    unmatched_hugo.append(hugo_stem)

# 2) Records in Maxim's page that don't correspond to any existing stub
#    -> create a new file for each (these are papers I missed)
for slug, rec in records.items():
    if slug in record_used:
        continue
    # Generate a Hugo filename from the slug; the slug is already normalized
    out_path = os.path.join(PUB_DIR, f"{slug}.md")
    if os.path.exists(out_path):
        # Some duplicate due to mapping; skip
        continue
    write_md(out_path, rec, slug)
    created.append(slug)

print(f'\n--- summary ---')
print(f'Updated   : {len(updated)}')
print(f'Created   : {len(created)}')
print(f'Unmatched (Hugo files without a record on Maxim\'s page): {len(unmatched_hugo)}')
for s in unmatched_hugo:
    print(f'   ?  {s}')
print(f'\nCreated new (papers we did not have stubs for): {len(created)}')
for s in sorted(created):
    print(f'   +  {s}')
