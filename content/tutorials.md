---
title: "Tutorials"
lead: "Historical SBPL tutorials preserved from the legacy sbpl.net site."
date: 2014-01-01
---

The tutorials below were authored for SBPL roughly 2012–2015. The
content of each tutorial is preserved in the legacy snapshot under
`/archive/legacy-drupal/`. They reference older versions of SBPL but
the underlying concepts (graph search, lattice planning, motion
primitives) are still current.

## [Primer to Search-Based Motion Planning](/archive/legacy-drupal/content/pages/0050-primer-to-search-based-motion-planning.html)

The theoretical background: state spaces, graph search,
A\* / weighted A\* / ARA\*, heuristics, motion primitives, and how
search-based planning compares with sampling-based approaches.

## [Primer to the Search-Based Planning Library (SBPL)](/archive/legacy-drupal/content/pages/0049-primer-to-the-search-based-planning-library-sbpl.html)

A walk-through of how the SBPL C++ library is organised: planners,
environments, motion primitives, and how to write your own
`SBPLPlanner`/`DiscreteSpaceInformation` pair.

## [SBPL Overview](/archive/legacy-drupal/content/pages/0047-sbpl-overview.html)

A brief overview of how the SBPL repository is structured and which
files implement which planners.

## [Planning with SBPL: Example in (x, y, θ) State Space](/archive/legacy-drupal/content/pages/0051-planning-with-sbpl-example-in-x-y-theta-state-space.html)

Worked example of planning for a 2-D footprint robot in (x, y, θ).

## [Navigation with SBPL in (x, y, θ)](/archive/legacy-drupal/content/pages/0046-navigation-with-sbpl-in-x-y-theta.html)

Builds on the previous tutorial to handle exploration of an
unknown environment.

## [Kinematic Constraints and Motion Primitives](/archive/legacy-drupal/content/pages/0048-kinematic-constraints-and-motion-primitives.html)

How kinematic constraints are encoded in SBPL.

## [Generating Motion Primitives](/archive/legacy-drupal/content/pages/0052-generating-motion-primitives-with-sbpl.html)

How to use the Matlab scripts in SBPL to generate custom motion
primitives.

## [Forward Arc Motion Primitives](/archive/legacy-drupal/content/pages/0053-forward-arc-motion-primitives.html)

The arc-based motion primitive formulation used in SBPL.

## [Building, Installing, and Using SBPL](/archive/legacy-drupal/content/pages/0054-building-installing-and-using-sbpl.html)

Build instructions (CMake on Linux/macOS/Windows) and a minimal
example of invoking a planner.

## [Arm Planning](/archive/legacy-drupal/content/pages/0055-arm-planning.html)

Tutorials and repository links for the legacy PR2 arm planner.

---

*If any of these links is broken in the published site, the source
markdown lives under
[`archive/legacy-drupal/content/pages/`](https://github.com/sbpl/sbpl.github.io/tree/main/archive/legacy-drupal/content/pages)
in this repository.*
