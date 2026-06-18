---
title: "Software"
lead: "Planning libraries, ROS packages, and utilities released by the lab."
date: 2014-01-01
---

For setup help with the libraries below, see the
[Tutorials](/tutorials/) page. The most maintained software is
hosted on the lab's [GitHub organisation](https://github.com/sbpl).

## Core Libraries

### SBPL — Search-Based Planning Library

The core planning library, written in C++ with no required
dependencies. Implements ARA\*, AD\*, Anytime D\*, R\*, weighted A\*,
SIPP, Experience Graphs, and lattice-based planners.

- Repository: [github.com/sbpl/sbpl](https://github.com/sbpl/sbpl.git)
- ROS Wiki: [ros.org/wiki/sbpl](http://wiki.ros.org/sbpl)

### SBPL Geometry Utilities

Geometry helpers used across SBPL packages.

- Repository: [github.com/sbpl/sbpl_geometry_utils](https://github.com/sbpl/sbpl_geometry_utils.git)

## ROS Planners and Plugins

### SBPL MoveIt! Plugin

Generic SBPL planner plugin for MoveIt!.

- Core: [aurone/moveit_planners_sbpl](https://github.com/aurone/moveit_planners_sbpl.git)
- Manipulation: [aurone/sbpl_manipulation](https://github.com/aurone/sbpl_manipulation.git)
- Leatherman utilities: [aurone/leatherman](https://github.com/aurone/leatherman.git)
- PR2 config: [aurone/pr2_sbpl_interface_config](https://github.com/aurone/pr2_sbpl_interface_config.git)

### Lattice Planner (3-D Navigation)

A global planner for `move_base` based on motion primitives.

- ROS source: [ros-planning/navigation_experimental](https://github.com/ros-planning/navigation_experimental.git)
- ROS Wiki: [ros.org/wiki/sbpl_lattice_planner](http://wiki.ros.org/sbpl_lattice_planner)
- Paper: [Likhachev & Ferguson, RSS 2008](http://www.cs.cmu.edu/~maxim/files/planlongdynfeasmotions_rss08.pdf)

### 3-D Navigation with Full-Body Collision Checking (PR2)

A `move_base` global planner that performs full-body collision
checks. PR2 specific.

- ROS Wiki: [ros.org/wiki/sbpl_3dnav_planner](http://wiki.ros.org/sbpl_3dnav_planner)

### Single-Arm Planning

Can be used with the ROS `arm_navigation` stack (`move_arm`). PR2
support plus an experimental "Any Robot" branch.

- ROS Wiki: [ros.org/wiki/sbpl_arm_planner](http://wiki.ros.org/sbpl_arm_planner)
- Papers: [ICRA 2010](http://www.seas.upenn.edu/~maximl/files/SBPlanningwithMotionPrims_icra10.pdf),
  [ICRA 2011](http://www.cs.cmu.edu/~maxim/files/armplanwithadaptmprim_icra11.pdf)

### Dual-Arm Planning (PR2)

- Paper: [ICRA 2012](http://www.cs.cmu.edu/~maxim/files/dualarmplanning_icra12.pdf)

### Navigation in Dynamic Environments (SIPP)

- ROS Wiki: [ros.org/wiki/sbpl_dynamic_env](http://wiki.ros.org/sbpl_dynamic_env)
- Papers: [ICRA 2011](http://www.cs.cmu.edu/~maxim/files/sipp_icra11.pdf),
  [AAAI 2011](http://www.cs.cmu.edu/~maxim/files/cfdaa_aaai11.pdf)

### Cart Planning

- ROS Wiki: [ros.org/wiki/sbpl_cart_planner](http://wiki.ros.org/sbpl_cart_planner)

### Experience Graphs (E-Graphs)

E-Graphs are built from experience (previously planned paths or user
demonstrations). The planner reuses parts of these prior paths to
plan faster.

- Papers: [RSS 2012](http://www.cs.cmu.edu/~maxim/files/egraph_rss12.pdf),
  [ICRA 2013](http://www.cs.cmu.edu/~maxim/files/anytimeincrementalegraphs_icra13.pdf)

## Utilities

### PViz

PR2 visualisation library. With one function call you can visualise
the PR2 in RViz with any joint configuration; the original meshes are
drawn as visualisation markers.

- Repository: [bcohen/pviz](https://github.com/bcohen/pviz.git)

---

See also: [**Old Software**](/old-software/) — historical SVN/Mercurial
links and ROS Diamondback/Electric/Fuerte branches from the
sbpl.net era.
