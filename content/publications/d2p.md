---
title: "Discriminatively-Guided Deliberative Perception for Pose Estimation of Multiple 3D Object Instances"
date: 2016-05-15
authors:
  - "Venkatraman Narayanan"
  - "Maxim Likhachev"
venue: "Imported from legacy sbpl.net — venue unverified (circa 2016)"
description: "A search-based perception paradigm (D2P) that integrates exhaustive global reasoning with discriminatively-trained algorithms for robust 3D pose estimation of multiple object instances, with provable bounded suboptimality."
code: "https://github.com/venkatrn/perception/"
draft: false
---

**Abstract.** We introduce a novel paradigm for model-based multi-object
recognition and 3-DoF pose estimation from 3D sensor data that
integrates exhaustive global reasoning with discriminatively-trained
algorithms in a principled fashion. Typical approaches for this task
are based on scene-to-model feature matching or regression by
statistical learners trained on a large database of annotated scenes.
These approaches are fast but sensitive to occlusions, features,
and/or training data. Generative approaches, on the other hand —
e.g., methods based on rendering and verification — are robust to
occlusions and require no training, but are slow at test time. We
conjecture that robust and efficient perception can be achieved
through a combination of generative methods and discriminatively-
trained approaches. To this end, we introduce the
Discriminatively-guided Deliberative Perception (D2P) paradigm that
has the following desirable properties: (a) D2P is a single search
algorithm that looks for the "best" rendering of the scene that
matches the input, (b) can be guided by any and multiple
discriminative algorithms, and (c) generates a solution that is
provably bounded suboptimal with respect to the chosen cost function.
In addition, we introduce the notions of completeness and resolution
completeness for multi-object pose estimation problems, and show that
D2P is resolution complete. We conduct extensive evaluations on a
benchmark dataset to study various aspects of D2P in relation to
existing approaches.

**Software.** D2P is available as a ROS catkin package and requires
ROS (Hydro or later) and PCL (1.7 or later). Source code and setup
instructions are at <https://github.com/venkatrn/perception/>.

---

*Imported from the legacy sbpl.net Drupal site
(`content/pages/0069-...`). The original page was authored by
Venkatraman Narayanan on 2016-05-02. Venue / DOI / camera-ready PDF
have not been independently verified; please update the front-matter
above with the canonical citation when known.*
