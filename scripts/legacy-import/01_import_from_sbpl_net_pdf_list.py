#!/usr/bin/env python3
"""Generate Hugo publication stubs from the legacy sbpl.net /files/ paper PDF list."""
import os, re, sys, subprocess

PDFS = """
aaprinciple_icaps06
ad_aij08_preprint
adaptastar_aamas05
ad_icaps05
aij04
airgroundexploration_iros15
anytimefootstepplanner_humanoids12
anytimeincrementalegraphs_icra13
ara_nips03
armplanwithadaptmprim_icra11
armplanwithheursearch_ijrr13
asipp_iros12
astarconnect_icra16
atd_socs13
audiosim_dafx14
authoring_i3d14
beamgraphs_icra13
brtdp_icml05
cartplanner_icra11
CBRLearn_icra02
cfdaa_aaai11
commencemultiuav_icuas14
costmapplan_icra08ws
demobasedtraining_aiide2016
demolearningwithegraphs_auro15
distopt_rss10
dlitemap_iros02
dlite_tro05
dmha_icra15
doorplanner_icra10
DPCT_icra10
dualarmplanning_icra12
egraphheur_icra15
egraph_rss12
exploreplannerformagic2010_iros2011
fastfactory_iros13
footprintoptim_iros09
gamelab_aiide12
globallocalplanning_icra12
glpa_icaps05
graspplanning_icra16
GSIPP_icra12
hsplanguide_icaps05ws
ICCV-2011-Tracking-Planning
icra2002_cbr_lm_paper
improvedmha_socs15
incplanwithadaptdim_icaps13
incsearchingames_aiide06
inctheta_ijcai09
lazyegraphs_icra15
ldog_icra09
learningtosearch_socs15
learntoplanfromdemos_rss13
loopplan_rss12
mcp_nips04
mha_ijrr15
mha_rss14
motplaninurbanenv_part1_iros08
motplaninurbanenv_part2_iros08
mtswithaa_aamas07
opportplan_iros13
parallelastar_icaps14
pathclear_iros07
pathclearwithivdscouts_icra08
pathplanforMAV_icra13
pc_ram09
pcwithgreedyscouts_asc06
perch_icra16
planfor3Dnav_icra12
planforcollabloc_icra16
planforindwrist_icra14
planforleader_icra15
planformanipuunderuncertainty_icra15
planfornarms_rss14
planforsmoothpick_icra14
planforspringloadeddoors_icra13
planfortetheredrobot_iros15
planincontspace_socs11
planlandsitesel_socs11
planlongdynfeasmotions_ijrr09
planlongdynfeasmotions_rss08
planunderuncertainhumanintentions_icra13
planwithadaptdimformm_icra12
planwithadaptdim_socs11
planwithhomotopy_aaai12_invitedpaper
planwithhomotopyconstraints3D_rss11
planwithhomotopyconstraints_aaai10
ppcp_aaai06
ppcp_aij09_preprint
ppcplandplanning_iros11
reasonframeworkforUC_iv08
RGPU_icra10
robothandwriting_iros14
rstar_aaai08
RstarGPU-NVIDIA
rtaa_aamas06
SBPlanningwithMotionPrims_icra10
searchcomesofage_aaai12_invitedpaper
searchportfoliowithsharing_icaps16
searchwithlearningforperception_rss16
searchwithmanyheuristics_ijcai15
sipp_icra11
slc_iros14
Spatio
tblattice_icra09
treerestoringastar_socs14
truncatedincsearch_aij16
truncincsearch_aaai13
webdemos_icra15
""".strip().splitlines()

# Skip files I've already added by hand earlier, and non-paper files.
ALREADY_DONE = {
    'planlongdynfeasmotions_rss08': 'lattice-rss-2008.md',
    'SBPlanningwithMotionPrims_icra10': 'sbpl-manipulation-icra-2010.md',
    'armplanwithadaptmprim_icra11': 'arm-adaptive-primitives-icra-2011.md',
    'dualarmplanning_icra12': 'dual-arm-icra-2012.md',
    'sipp_icra11': 'sipp-icra-2011.md',
    'cfdaa_aaai11': 'cfdaa-aaai-2011.md',
    'egraph_rss12': 'egraphs-rss-2012.md',
    'anytimeincrementalegraphs_icra13': 'anytime-egraphs-icra-2013.md',
}

# Venue code → human-readable label
VENUE = {
    'rss': 'RSS', 'icra': 'ICRA', 'iros': 'IROS', 'aaai': 'AAAI',
    'aamas': 'AAMAS', 'nips': 'NIPS', 'icaps': 'ICAPS', 'ijcai': 'IJCAI',
    'ijrr': 'IJRR', 'tro': 'T-RO', 'aij': 'AIJ', 'ram': 'RA-M',
    'icml': 'ICML', 'iccv': 'ICCV', 'iv': 'IV', 'auro': 'Autonomous Robots',
    'humanoids': 'Humanoids', 'socs': 'SoCS', 'aiide': 'AIIDE',
    'dafx': 'DAFx', 'i3d': 'I3D', 'icuas': 'ICUAS', 'asc': 'ASCC',
}
# Approx month for each conference (for ordering only; not authoritative)
VENUE_MONTH = {
    'rss': '07', 'icra': '05', 'iros': '10', 'aaai': '07',
    'aamas': '05', 'nips': '12', 'icaps': '06', 'ijcai': '08',
    'ijrr': '01', 'tro': '01', 'aij': '01', 'ram': '03',
    'icml': '07', 'iccv': '10', 'iv': '06', 'auro': '01',
    'humanoids': '11', 'socs': '07', 'aiide': '10',
    'dafx': '09', 'i3d': '03', 'icuas': '05', 'asc': '12',
}

# Try to expand short slug fragments into readable words
TITLE_WORDS = [
    ('planlongdynfeasmotions', 'Planning Long Dynamically-Feasible Motions'),
    ('armplanwithadaptmprim', 'Arm Planning with Adaptive Motion Primitives'),
    ('armplanwithheursearch', 'Arm Planning with Heuristic Search'),
    ('searchportfoliowithsharing', 'Search Portfolios with Sharing'),
    ('searchwithlearningforperception', 'Search with Learning for Perception'),
    ('searchwithmanyheuristics', 'Search with Many Heuristics (MHA*)'),
    ('truncatedincsearch', 'Truncated Incremental Search'),
    ('truncincsearch', 'Truncated Incremental Search'),
    ('demolearningwithegraphs', 'Demonstration-Based Learning with Experience Graphs'),
    ('demobasedtraining', 'Demonstration-Based Training'),
    ('anytimefootstepplanner', 'Anytime Footstep Planner'),
    ('anytimeincrementalegraphs', 'Anytime Incremental Experience Graphs'),
    ('exploreplannerformagic', 'Exploration Planner for MAGIC'),
    ('costmapplan', 'Costmap-Based Planning'),
    ('motplaninurbanenv_part1', 'Motion Planning in Urban Environments, Part 1'),
    ('motplaninurbanenv_part2', 'Motion Planning in Urban Environments, Part 2'),
    ('reasonframeworkforUC', 'Reasoning Framework for Urban Challenge'),
    ('pathclearwithivdscouts', 'Path Clearance with Independent Variable Discretisation Scouts'),
    ('pathclear', 'Path Clearance'),
    ('pcwithgreedyscouts', 'Path Clearance with Greedy Scouts'),
    ('planwithhomotopyconstraints3D', 'Planning with Homotopy Constraints in 3D'),
    ('planwithhomotopyconstraints', 'Planning with Homotopy Constraints'),
    ('planwithhomotopy', 'Planning with Homotopy'),
    ('planforspringloadeddoors', 'Planning for Spring-Loaded Doors'),
    ('planforsmoothpick', 'Planning for Smooth Pick-and-Place'),
    ('planformanipuunderuncertainty', 'Planning for Manipulation Under Uncertainty'),
    ('planforcollabloc', 'Planning for Collaborative Localization'),
    ('planforindwrist', 'Planning for an Industrial Wrist'),
    ('planfortetheredrobot', 'Planning for a Tethered Robot'),
    ('planunderuncertainhumanintentions', 'Planning Under Uncertain Human Intentions'),
    ('planforleader', 'Planning for a Leader'),
    ('planfornarms', 'Planning for N Arms'),
    ('planfor3Dnav', 'Planning for 3D Navigation'),
    ('planlandsitesel', 'Planning + Landing-Site Selection'),
    ('planincontspace', 'Planning in Continuous Space'),
    ('planwithadaptdimformm', 'Planning with Adaptive Dimensionality for Mobile Manipulation'),
    ('planwithadaptdim', 'Planning with Adaptive Dimensionality'),
    ('globallocalplanning', 'Global + Local Planning'),
    ('improvedmha', 'Improved Multi-Heuristic A*'),
    ('mha', 'Multi-Heuristic A* (MHA*)'),
    ('dmha', 'Dynamic Multi-Heuristic A* (DMHA*)'),
    ('lazyegraphs', 'Lazy Experience Graphs'),
    ('egraphheur', 'Experience-Graph Heuristic'),
    ('egraph', 'Experience Graphs (E-Graphs)'),
    ('cartplanner', 'Cart Planner'),
    ('doorplanner', 'Door Planner'),
    ('graspplanning', 'Grasp Planning'),
    ('audiosim', 'Audio Simulation'),
    ('authoring', 'Authoring (Animation)'),
    ('robothandwriting', 'Robot Handwriting'),
    ('searchcomesofage', '“Search Comes of Age”'),
    ('parallelastar', 'Parallel A*'),
    ('treerestoringastar', 'Tree-Restoring A*'),
    ('astarconnect', 'A*-Connect'),
    ('rstar', 'R*'),
    ('ara', 'ARA*'),
    ('adaptastar', 'Adaptive A* (Adapt A*)'),
    ('aaprinciple', 'Anytime/Anywhere Search Principle'),
    ('atd', 'Anytime Truncated D*'),
    ('ad_aij08', 'AD* Algorithm (AIJ 2008)'),
    ('ad_icaps05', 'AD*: Anytime Dynamic A*'),
    ('aij04', 'Likhachev AIJ 2004'),
    ('mcp', 'Modular Component Planner'),
    ('brtdp', 'Bounded Real-Time Dynamic Programming'),
    ('rtaa', 'Real-Time Adaptive A*'),
    ('asipp', 'Anytime SIPP'),
    ('GSIPP', 'Generalized SIPP'),
    ('beamgraphs', 'Beam Graphs'),
    ('fastfactory', 'Fast Factory Planning'),
    ('opportplan', 'Opportunistic Planning'),
    ('loopplan', 'Loop Planning'),
    ('webdemos', 'Web-Based Planner Demos'),
    ('learntoplanfromdemos', 'Learning to Plan from Demonstrations'),
    ('learningtosearch', 'Learning to Search'),
    ('incplanwithadaptdim', 'Incremental Planning with Adaptive Dimensionality'),
    ('incsearchingames', 'Incremental Search in Games'),
    ('inctheta', 'Incremental Theta*'),
    ('tblattice', 'Time-Bounded Lattice Planning'),
    ('dlitemap', 'D* Lite with Map Updates'),
    ('dlite', 'D* Lite'),
    ('ldog', 'LDOG'),
    ('ppcplandplanning', 'PPCP for Land Planning'),
    ('ppcp_aaai06', 'PPCP (AAAI 2006)'),
    ('ppcp_aij09', 'PPCP (AIJ 2009)'),
    ('cfdaa', 'Cost-Function-Driven Algorithm Adaptation'),
    ('hsplanguide', 'Heuristic Search Planning Guide'),
    ('glpa', 'GLPA*'),
    ('distopt', 'Distributed Optimization'),
    ('SBPlanningwithMotionPrims', 'Search-Based Planning with Motion Primitives'),
    ('dualarmplanning', 'Dual-Arm Planning'),
    ('pathplanforMAV', 'Path Planning for MAVs'),
    ('exploreplannerformagic2010', 'Exploration Planner for MAGIC 2010'),
    ('mtswithaa', 'Moving Target Search with Adaptive A*'),
    ('footprintoptim', 'Robot Footprint Optimization'),
    ('slc', 'State-Lattice Controllers'),
    ('RGPU', 'A* on GPU'),
    ('RstarGPU-NVIDIA', 'R* on NVIDIA GPU'),
    ('DPCT', 'DPCT'),
    ('commencemultiuav', 'Multi-UAV Mission Planning'),
    ('CBRLearn', 'Case-Based Reasoning for Learning'),
    ('icra2002_cbr_lm_paper', 'CBR/Likhachev (ICRA 2002)'),
    ('gamelab', 'GameLab'),
    ('pc_ram', 'Path Clearance (RA-M)'),
    ('ICCV-2011-Tracking-Planning', 'Joint Tracking and Planning (ICCV 2011)'),
    ('airgroundexploration', 'Air-Ground Cooperative Exploration'),
    ('Spatio', 'Spatio (unknown paper)'),
]

def title_from_slug(slug):
    """Best-effort heuristic title."""
    # Strip the trailing _<venue><year> suffix
    body = slug
    for code in VENUE:
        m = re.search(rf'_{code}\d{{2,4}}$', body, re.IGNORECASE)
        if m:
            body = body[:m.start()]
            break
    # Hand-curated mapping first
    for stem, nice in TITLE_WORDS:
        if body.lower().startswith(stem.lower()):
            return nice + body[len(stem):].replace('_',' ').replace('-',' ').strip()
    # Fallback: split on underscores/camelCase
    body = re.sub('([a-z])([A-Z])', r'\1 \2', body)
    body = body.replace('_',' ').replace('-',' ').strip()
    return body.title() if body else slug

def parse_venue(slug):
    """Return (venue_label, year, month_str) or None."""
    m = re.search(r'_([a-zA-Z]+)(\d{2,4})(_.*)?$', slug)
    if not m:
        return None
    code = m.group(1).lower()
    if code not in VENUE:
        return None
    y_raw = int(m.group(2))
    if y_raw < 50: year = 2000 + y_raw
    elif y_raw < 100: year = 1900 + y_raw
    else: year = y_raw
    month = VENUE_MONTH.get(code, '06')
    label = f"{VENUE[code]} {year}"
    # Some slugs have suffixes like _ws (workshop), _invitedpaper, _preprint, _abs
    suffix = (m.group(3) or '').lower()
    if 'ws' in suffix:        label += " (Workshop)"
    if 'invited' in suffix:   label += " (Invited)"
    if 'preprint' in suffix:  label += " (Preprint)"
    return label, year, month

def filename_to_filebase(slug):
    """Hugo filename: lowercased, hyphens for underscores."""
    name = slug.lower().replace('_','-')
    # remove parens and dots
    name = re.sub(r'[^a-z0-9-]', '-', name)
    name = re.sub(r'-+', '-', name).strip('-')
    return name

SKIP_AS_PAPER = {
    'maxim_fullcv', 'thesis', 'research',
}
# These are in the watchdog hits but not strictly papers; keep only files matching our pattern
# (already excluded by the list above)

OUTDIR = '/home/necromancer/Desktop/newsite/sbpl.github.io/content/publications'

created = 0
skipped = 0
for slug in PDFS:
    slug = slug.strip()
    if not slug: continue
    if slug in ALREADY_DONE:
        skipped += 1
        continue
    if slug in SKIP_AS_PAPER:
        skipped += 1
        continue
    parsed = parse_venue(slug)
    title = title_from_slug(slug)
    if parsed:
        venue_label, year, month = parsed
        date = f"{year}-{month}-01"
    else:
        venue_label = "Imported from legacy sbpl.net (year unknown)"
        date = "2010-01-01"  # placeholder

    fname = filename_to_filebase(slug)
    out = os.path.join(OUTDIR, f"{fname}.md")
    if os.path.exists(out):
        skipped += 1
        continue

    pdf_url_sbpl = f"http://sbpl.net/files/{slug}.pdf"
    pdf_url_cmu  = f"http://www.cs.cmu.edu/~maxim/files/{slug}.pdf"

    body = f"""---
title: "{title}"
date: {date}
authors:
  - "Maxim Likhachev"
venue: "{venue_label}"
description: "Imported from the legacy sbpl.net /files/ catalogue. Title and authors are best-effort heuristics; please update from the source PDF."
project_page: "{pdf_url_cmu}"
draft: false
---

This entry was auto-generated from the legacy `sbpl.net/files/{slug}.pdf` URL
recovered from the old Drupal site's access logs. The title above is a
heuristic expansion of the filename slug — please replace it with the
canonical citation when convenient. Co-authors beyond Maxim Likhachev
need to be added from the source PDF.

Original (defunct) link: <{pdf_url_sbpl}>
Mirrored on Maxim's CMU page (live): <{pdf_url_cmu}>
"""
    with open(out, 'w') as f:
        f.write(body)
    created += 1

print(f"Created {created} stubs, skipped {skipped} (already present / non-paper).")
