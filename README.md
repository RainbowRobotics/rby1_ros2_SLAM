# 0. About rby1_ros2_slam
[참고] 본 레포지토리는 테스트용 입니다.   
- Lakibeam ros2 드라이버를 사용했습니다.
- 주요 기능은 다음과 같습니다.
    - 2D 라이다 센서 퓨전 및 좌표계 변환
    - SLAM
    - AMCL 기반 로봇 모바일 플랫폼 제어

# 1. Pre installation
- [중요!] ros2 apt 저장소가 설정되어 있지 않는 경우, 아래 경로에서 별도의 사전 설정이 필요함
    https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html
- ros2 humble 설치
    ```bash
    # apt update
    sudo apt update

    # ros2 humble 설치
    sudo apt install ros-humble-desktop
    ```

- 필요 ros2 패키지 설치
    ```bash
    # 누락된 패키지가 있다면 피드백 부탁드립니다 ^^
    sudo apt update

    sudo apt install ros-humble-slam-toolbox
    sudo apt install ros-humble-tf2-ros
    sudo apt install ros-humble-tf2
    sudo apt install ros-humble-tf2-geometry-msgs
    sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup
    ```

## 2. Create the workspace for ROS2 Driver
- 워크스페이스 만들기

    ```bash
    cd ~
    mkdir -p catkin_ws/src
    ```

- Build rby1_ros2_slam ROS2 Driver
    ```bash
    cd catkin_ws/src

    git clone https://github.com/RainbowRobotics/rby1_ros2_SLAM.git

    cd ..

    colcon build
    ```

## 3. How to Use
- [최초 1회 실행] 맵 만들기
    ``` bash
    # 터미널 1: 라이다 센서 퓨전
    ros2 launch lakibeam1 data_fusion.launch.py

    # 터미널 2: slam 실행
    ros2 launch rby1_slam slam_toolbox_online.launch.py

    # 맵 저장하기
    # 파일 경로 수정 필요,,
    ros2 run nav2_map_server map_saver_cli -f /home/nvidia/catkin_ws/src/rby1_slam/map/
    ```

- 맵 기반 로봇 제어하기
    ``` bash
    # 터미널 1: 라이다 센서 퓨전
    ros2 launch lakibeam1 data_fusion.launch.py

    # 터미널 2: nav2 실행
    ros2 launch nav2_bringup bringup_launch.py map:=/home/nvidia/catkin_ws/src/rby1_slam/map/map.yaml use_sim_time:=false

    # 실행 후, rviz 에서 로봇의 initial pose 를 정의해줘야 함 [필수!!]

    # Nav2 goal pose 넣으면 cmd_vel 나오고, 그거 input 으로 받아서 로봇 제어하는 명령어
    ros2 run lakibeam1 mobile_subscriber_test.py
    ```

    +++