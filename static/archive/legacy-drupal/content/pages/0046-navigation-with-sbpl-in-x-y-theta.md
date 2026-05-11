# Navigation with SBPL (in X, Y, Theta)

In the [previous article](http://sbpl.net/node/51), we showed how to plan on a static map. In the context of robot navigation, we don't have the luxury of a static map. Instead, the map of the environment updates as the robot moves towards its goal. In this article, we'll show a few code snippets on how to change the previous example to react to an updating environment with two different kinds of planners: ARA* (anytime planning) and AD* (incremental planning).

In the sbpl/src/test/main.cpp file, there is a section of code in the planandnavigatexythetalat function that simulates an updating environment. It's not necessary to understand this code - it is simply a framework for generating an unknown environment. The important portions of this code are the ones that inform the planners about the changed environment.

In the example, simulating the environment is rather contrived - an empty environment is create and uses the real map as its "sensors" (let's call this the sim_environment). Basically, the true values of the map are slowly fed into this duplicated environment.

In the snippet above, we look at the newly sensed cells and determine which ones have changed. Since sim_environment has empty cells for areas it doesn't know about, there will be a difference in the costs for a particular cell once it has "sensed" new information about it. In the loop, we inform the environment to update its map using the *UpdateCost* function. We also push all cells that have been changed into the *changedcellsV* vector.

Once the vector is built, we inform the planner about the cells that have been changed. For the ARA* planner, we use *costs_changed()* to inform the planner that the environment has updated.

For the AD* planner, we have to do a little more work in order to update the internal search tree. AD* needs more information than just the changed cells to update. To do this, we feed the changed cells into *GetPredsofChangedEdges*. The output of this is then fed into *update_preds_of_changededges*.

With those steps completed, the planner will now compute paths with the updated environment.
