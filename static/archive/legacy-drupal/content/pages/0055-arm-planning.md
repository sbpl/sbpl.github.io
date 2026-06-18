# Arm Planning

#  sbpl_arm_planning

##  <u>Repositories</u>

 **ROS Diamondback**

 Arm Navigation

 svn co [https://mediabox.grasp.upenn.edu/svn/penn-ros-pkgs/sbpl_arm_planning/branches/diamondback/](https://mediabox.grasp.upenn.edu/svn/penn-ros-pkgs/sbpl_arm_planning/branches/diamondback/)

 **ROS Electric**

 Arm Navigation

 svn co [https://mediabox.grasp.upenn.edu/svn/penn-ros-pkgs/sbpl_arm_planning/branches/electric/](https://mediabox.grasp.upenn.edu/svn/penn-ros-pkgs/sbpl_arm_planning/branches/electric/)

 **ROS Fuerte**

 Arm Navigation

 svn co [https://mediabox.grasp.upenn.edu/svn/penn-ros-pkgs/sbpl_arm_planning/branches/fuerte_arm_navigation/](https://mediabox.grasp.upenn.edu/svn/penn-ros-pkgs/sbpl_arm_planning/branches/fuerte_arm_navigation/)

 (install documentation below)

 MoveIt! (only compatible with June 2012)

 svn co [https://mediabox.grasp.upenn.edu/svn/penn-ros-pkgs/sbpl_arm_planning/trunk/](https://mediabox.grasp.upenn.edu/svn/penn-ros-pkgs/sbpl_arm_planning/trunk/)

 **ROS Groovy**

 C++ API

 git clone https://github.com/bcohen/sbpl_manipulation.git

 [install documentation](https://github.com/bcohen/sbpl_manipulation)

 MoveIt!

 Coming soon!

##  <u>How to get started (ROS Fuerte):</u>

<u>**Download & Compile:**</u>

 0) Install prerequisites:

 sudo apt-get install ros-fuerte-pr2-kinematics ros-fuerte-arm-navigation ros-fuerte-arm-navigation-experimental

 1) Get the Arm Planner:

 svn co [https://mediabox.grasp.upenn.edu/svn/penn-ros-pkgs/sbpl_arm_planning/branches/fuerte_arm_navigation/](https://mediabox.grasp.upenn.edu/svn/penn-ros-pkgs/sbpl_arm_planning/branches/fuerte_arm_navigation/) sbpl_arm_planning

 2) Get the SBPL:

 git clone [https://github.com/sbpl/sbpl.git](https://github.com/sbpl/sbpl.git)

 3) Build the SBPL. Follow the directions here:

 [https://github.com/sbpl/sbpl/blob/master/README.txt](https://github.com/sbpl/sbpl/blob/master/README.txt)

 4) Build the Arm Planner:

 rosmake sbpl_arm_planner_node

 5) Build the test package (for testing the planner):

 rosmake simple_arm_utils

**<u>Run Demo:</u>**

 Make sure you added this to your bashrc: export ROBOT=sim

 **Terminal 1 - Bring up Gazebo & Right Arm Navigation Stack**

 roslaunch simple_arm_control gazebo_with_right_arm_nav.launch

 **Terminal 2 - Bring up RViz** (add display for visualization markers)

 rosrun rviz rviz

 **Terminal 3 - Launch the planner for the right arm**

 roslaunch sbpl_arm_planner_node sbpl_planning_right_arm.launch

 **Terminal 4 - Request a motion plan**

 roslaunch simple_arm_control goal1.launch
