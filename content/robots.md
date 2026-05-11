---
title: "Lab Robots"
lead: "The hardware platforms we use to validate our planning algorithms in the real world."
date: 2014-01-01
---

## Allen the PR2

![Allen the PR2 grasping](/archive/legacy-drupal/media/uploads/site/all/images/pr2_grasp.png)

Allen the PR2 is a mobile manipulation platform developed by
[Willow Garage](http://www.willowgarage.com/pages/pr2/overview). The robot
has two 7-degree-of-freedom arms for manipulating objects and an
omni-directional base for navigation. It carries an array of sensors
including two Hokuyo laser range finders and seven cameras for building
3-D maps of its surroundings and identifying objects. In our lab we use
Allen to test a variety of planners including single-arm, dual-arm,
navigation (in position and orientation), and full-body mobile manipulation.

## Man-Hack the Hexacopter

<p style="text-align:center;">
  <img src="/archive/legacy-drupal/media/uploads/site/all/images/hexarotor.png" alt="Hexacopter top view" style="max-height:220px;">
  <img src="/archive/legacy-drupal/media/images/IMG_2895_small.jpeg" alt="Hexacopter in flight" style="max-height:220px;">
  <img src="/archive/legacy-drupal/media/images/MC-UAV-1-2_small.jpeg" alt="Hexacopter side view" style="max-height:220px;">
</p>

Man-Hack the Hexacopter is our lab unmanned aerial vehicle (UAV). The
base is a Mikrokopter Hexa XL frame with a custom-made carbon fiber
computer carrier and blade guard. Onboard processing is performed by an
i7 COM Express module running ROS, allowing the hexacopter to operate
without any off-board connectivity. Like Melvin, it uses two
orthogonally mounted Hokuyo laser range finders as the primary
localization sensors, augmented by GPS and two wide-angle camera
systems. Total system weight is approximately 4.3 kg with over 15
minutes of flight time.

The hexacopter is used for 3-D planning research including planning
under uncertainty, planning in the presence of 3-D dynamic obstacles,
and visual servoing in conjunction with planning.

## Melvin the Segbot

<p style="text-align:center;">
  <img src="/archive/legacy-drupal/media/images/segbot_small.png" alt="Segbot" style="max-height:220px;">
  <img src="/archive/legacy-drupal/media/images/IMG_2896_small.jpeg" alt="Segbot side" style="max-height:220px;">
  <img src="/archive/legacy-drupal/media/images/IMG_2897_small.jpeg" alt="Segbot front" style="max-height:220px;">
</p>

Melvin the Segbot is based on a Segway RMP 200 platform with a
custom-made rear trailer allowing it to operate in a variety of
environments both indoors and outdoors. The custom computer system
consists of an 8-core server and a 2-core controller, giving Melvin the
highest computational capability of any of our lab robots. Like all of
our robots, Melvin uses ROS running on Kubuntu for the software
infrastructure. For sensing the environment, Melvin relies on two
Hokuyo laser range finders, supplemented by GPS or vision systems
when required.

Melvin is used primarily for ground navigation research, including
research in exploration, planning in the presence of dynamic obstacles,
and multi-robot planning.

---

*This page describes the hardware platforms used during the sbpl.net
era of the lab (~2012–2015). For the lab's current robotic platforms,
see the People page and recent publications.*
