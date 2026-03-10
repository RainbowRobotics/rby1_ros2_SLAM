# 0. About rby1_ros2_slam
[Note] This repository is for testing purposes.   
- Uses the Lakibeam ROS 2 driver.
- Main features are as follows.
    - 2D LiDAR sensor fusion and coordinate frame transformation
    - SLAM
    - AMCL-based mobile robot platform control

# 1. Pre installation
- [Important!] If the ROS 2 apt repository is not configured, complete the prerequisite setup at the following link:
    https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html
- Install ROS 2 Humble
    ```bash
    # apt update
    sudo apt update

    # Install ROS 2 Humble
    sudo apt install ros-humble-desktop
    ```

- Install required ROS 2 packages
    ```bash
    # If any required packages are missing, please let us know.
    sudo apt update

    sudo apt install ros-humble-slam-toolbox
    sudo apt install ros-humble-tf2-geometry-msgs
    sudo apt install ros-humble-nav2-bringup
    ```

## 2. Create the workspace for ROS2 Driver
- Create a workspace

    ```bash
    cd ~
    mkdir -p catkin_ws/src
    ```

- Build rby1_ros2_slam ROS2 Driver
    ```bash
    cd catkin_ws/src

    git clone https://github.com/RainbowRobotics/rby1_ros2_SLAM.git .

    cd ..

    colcon build
    ```

## 3. How to Use
- [First-time setup] Create a map
    ``` bash
    # Terminal 1: LiDAR sensor fusion
    ros2 launch lakibeam1 data_fusion.launch.py

    # Terminal 2: Run SLAM
    ros2 launch rby1_slam slam_toolbox_online.launch.py

    # Save the map
    # Update the file path as needed
    ros2 run nav2_map_server map_saver_cli -f /home/nvidia/catkin_ws/src/rby1_slam/map/
    ```

- Control the robot using a map
    ``` bash
    # Terminal 1: LiDAR sensor fusion
    ros2 launch lakibeam1 data_fusion.launch.py

    # Terminal 2: Run Nav2
    ros2 launch nav2_bringup bringup_launch.py map:=/home/nvidia/catkin_ws/src/rby1_slam/map/map.yaml use_sim_time:=false

    # After launching, you must set the robot's initial pose in RViz. [Required]

    # This command receives cmd_vel generated from a Nav2 goal pose and uses it to control the robot
    ros2 run lakibeam1 mobile_subscriber_test.py
    ```
