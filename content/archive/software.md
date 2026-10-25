---
title: "Software"
lead: "Planning libraries, ROS packages, and utilities released by the lab."
layout: "software"
archive_tab: "software"
# /archive/ itself redirects here (the first tab)
aliases: ["/software/", "/archive/"]
# Each group is a section of cards on /software/. Every item takes a name,
# a short description and any number of links ({label, url}).
groups:
  - name: "Core Libraries"
    items:
      - name: "SBPL — Search-Based Planning Library"
        description: "The core planning library, written in C++ with no required dependencies. Implements ARA*, AD*, Anytime D*, R*, weighted A*, SIPP, Experience Graphs, and lattice-based planners."
        links:
          - { label: "GitHub", url: "https://github.com/sbpl/sbpl" }
          - { label: "ROS Wiki", url: "https://wiki.ros.org/sbpl" }
      - name: "SBPL Geometry Utilities"
        description: "Geometry helpers used across SBPL packages."
        links:
          - { label: "GitHub", url: "https://github.com/sbpl/sbpl_geometry_utils" }

  - name: "ROS Planners and Plugins"
    items:
      - name: "SBPL MoveIt! Plugin"
        description: "Generic SBPL planner plugin for MoveIt!."
        links:
          - { label: "Core", url: "https://github.com/aurone/moveit_planners_sbpl" }
          - { label: "Manipulation", url: "https://github.com/aurone/sbpl_manipulation" }
          - { label: "Leatherman", url: "https://github.com/aurone/leatherman" }
          - { label: "PR2 config", url: "https://github.com/aurone/pr2_sbpl_interface_config" }
      - name: "Lattice Planner (3-D Navigation)"
        description: "A global planner for move_base based on motion primitives."
        links:
          - { label: "GitHub", url: "https://github.com/ros-planning/navigation_experimental" }
          - { label: "ROS Wiki", url: "https://wiki.ros.org/sbpl_lattice_planner" }
          - { label: "Paper (RSS 2008)", url: "https://www.cs.cmu.edu/~maxim/files/planlongdynfeasmotions_rss08.pdf" }
      - name: "3-D Navigation with Full-Body Collision Checking (PR2)"
        description: "A move_base global planner that performs full-body collision checks. PR2 specific."
        links:
          - { label: "ROS Wiki", url: "https://wiki.ros.org/sbpl_3dnav_planner" }
      - name: "Single-Arm Planning"
        description: "Can be used with the ROS arm_navigation stack (move_arm). PR2 support plus an experimental “Any Robot” branch."
        links:
          - { label: "ROS Wiki", url: "https://wiki.ros.org/sbpl_arm_planner" }
          - { label: "Paper (ICRA 2010)", url: "https://www.cs.cmu.edu/~maxim/files/SBPlanningwithMotionPrims_icra10.pdf" }
          - { label: "Paper (ICRA 2011)", url: "https://www.cs.cmu.edu/~maxim/files/armplanwithadaptmprim_icra11.pdf" }
      - name: "Dual-Arm Planning (PR2)"
        links:
          - { label: "Paper (ICRA 2012)", url: "https://www.cs.cmu.edu/~maxim/files/dualarmplanning_icra12.pdf" }
      - name: "Navigation in Dynamic Environments (SIPP)"
        links:
          - { label: "ROS Wiki", url: "https://wiki.ros.org/sbpl_dynamic_env" }
          - { label: "Paper (ICRA 2011)", url: "https://www.cs.cmu.edu/~maxim/files/sipp_icra11.pdf" }
          - { label: "Paper (AAAI 2011)", url: "https://www.cs.cmu.edu/~maxim/files/cfdaa_aaai11.pdf" }
      - name: "Cart Planning"
        links:
          - { label: "ROS Wiki", url: "https://wiki.ros.org/sbpl_cart_planner" }
      - name: "Experience Graphs (E-Graphs)"
        description: "E-Graphs are built from experience (previously planned paths or user demonstrations). The planner reuses parts of these prior paths to plan faster."
        links:
          - { label: "Paper (RSS 2012)", url: "https://www.cs.cmu.edu/~maxim/files/egraph_rss12.pdf" }
          - { label: "Paper (ICRA 2013)", url: "https://www.cs.cmu.edu/~maxim/files/anytimeincrementalegraphs_icra13.pdf" }

  - name: "Utilities"
    items:
      - name: "PViz"
        description: "PR2 visualisation library. With one function call you can visualise the PR2 in RViz with any joint configuration; the original meshes are drawn as visualisation markers."
        links:
          - { label: "GitHub", url: "https://github.com/bcohen/pviz" }
---

For setup help with the libraries below, see the [Tutorials](/archive/tutorials/)
page. The most maintained software is hosted on the lab's
[GitHub organisation](https://github.com/sbpl). Historical SVN/Mercurial
links and ROS Diamondback/Electric/Fuerte branches are on the
[Old Software](/archive/old-software/) page.
