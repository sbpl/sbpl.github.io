# SBPL overview

This tutorial will describe how SBPL is set up. For background information, [click here](http://victor.hwanger.com/post/47051626618/primer-to-the-search-based-planning-library-sbpl).

**Environments**

As described in the previous tutorial, planning with search-based methods have two parts - representing the problem as a graph, then solving the graph with graph-search methods. SBPL has two objects it uses for these two roles - the environment and the planner. Unless you're fiddling with the actual graph search algorithm, the environment object will be the thing you interact most with.

In a nutshell, the environment handles domain specific details and translates them into a generic form for the planner to handle. For example, the environment handles the translation between the (x, y, theta) position of a robot into a graph composed of generic state IDs. The planner then solves the graph without having to know about the domain. (This doesn't actually happen in one step - the graph is generated on demand by the planner. As a result, the planner often calls the environment object to retrieve information on demand).

The environment also implements the heuristic computation. This is domain dependent, since the heuristic for guiding a robotic arm to an object will be different from navigating a car close to its goal.

There already exists many environments and planners in SBPL, but they might not cover a custom scenario. In this case, you will have to implement your own environment (a very involved topic that might be covered in the future).

- Environment2D - for robots navigating in (x, y) coordinates
- EnvironmentXYTHETALAT - for robots navigating in (x, y, theta) coordinates
- EnvironmentXYTHETALEVLAT - for robots navigating in (x, y, theta) but alsohandles collision checking and cost computations for a given set of footprints.
- Environment_robarm - motion planning for a 7D (7 joint angles) robotic arm.

These can all be found in sbpl/src/discrete_space_information.

Other environments that have successfully been implemented (but not included in SBPL):

-  pushing a cart with the PR2 (x, y, theta, theta of the cart)
-  opening a door with the PR2 (x, y, theta, door interval)
-  quadrotor path planning (x, y, z)
-  time dependent planning (x, y, z, time)

**Planners**

There are a number of planners that are available in sbpl/src/planners

-  ARA*
-  Anytime D*
-  R*
