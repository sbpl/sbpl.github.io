# Building, Installing, and Using SBPL

#  **Building, Installing, and Using SBPL**

SBPL is available as a standalone software library. SBPL itself has no dependencies other than the C/C++ standard library.

These build and install instructions are primarily for Linux. For other operating systems, CMake can generate the platform-specific build and project files necessary for building SBPL.

Versions of ROS older than Fuerte may contain packages that depend on a ROS package version of SBPL. The recommended method to install SBPL is to install it as a standard system library. However, if you wish to use the old ROS package version of SBPL, you may follow[ these instructions](#ROS Package Instructions).

##  **1. Building and Installing SBPL from source**

###  **1.1 Build SBPL**

SBPL uses git as its version control system. From the directory where you want the SBPL source to reside, clone the latest source from https://github.com/sbpl/sbpl:

```

git clone https://github.com/sbpl/sbpl.git
```

In the source directory, build the SBPL library using standard CMake build conventions:

```

mkdir build
cd build
cmake ..
make

```

###  **1.2 Install SBPL**

Install the built library and headers onto your local system (usually into /usr/local):

```

sudo make install
```

##  **2. Installing SBPL from pre-built binary package**

A pre-built Debian package exists on Linux for ROS distributions Fuerte and newer. To install the Debian, run:

```

sudo apt-get install ros-*distro*-sbpl
```

where *distro* is the name of your ROS distribution. This will install the SBPL library and associated development headers alongside other ROS components (in /opt/ros/*distro* on Ubuntu distributions). A pkg-config file is also included to allow you to locate the SBPL library components in your build system.

##  **3. Build your (ROS) package with SBPL as a dependency (CMake)**

In the CMakeLists.txt for your (ROS) package, the following lines are needed to find the installed SBPL files:

```

find_package(PkgConfig REQUIRED)
pkg_check_modules(SBPL REQUIRED sbpl)
include_directories(${SBPL_INCLUDE_DIRS})
link_directories(${SBPL_LIBRARY_DIRS})

```

Then, after you've declared your binaries, you need to link them against SBPL with the following line:

```

target_link_libraries(*your-binary-here* ${SBPL_LIBRARIES})
```

##  **[]()4. Installing and Using SBPL as a ROS package**

The ROS package version of SBPL was deprecated with the release of ROS Fuerte. However, packages in ROS Electric may still require the ROS package version of SBPL.

###  **4.1 Install SBPL**

####  **4.1.1 Source install**

SBPL uses git as its version control system. From the directory where you want the SBPL source to reside, clone the latest source from https://github.com/sbpl/sbpl:

```

git clone https://github.com/sbpl/sbpl.git
```

In the source directory, checkout the *electric* branch of the repository to revert to the old ROS package version:

```

git checkout electric
```

Ensure that SBPL is on your ROS_PACKAGE_PATH and type:

```

rosmake sbpl
```

####  **4.1.2 Binary install**

SBPL is also available as a pre-built Debian in ROS Electric. To instal the Debian, run:

```

sudo apt-get install ros-electric-arm-navigation
```

###  **4.2 Build your ROS package with SBPL as a depency (rosbuild)**

In the manifest.xml for your package, you need to add the following line to declare the SBPL package as a dependency:

```

<depend package="sbpl"/>
```
