cmake_minimum_required(VERSION 3.8)
project(lakibeam1)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(rclpy REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(CURL REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()

include_directories(
# include
  ${ament_INCLUDE_DIRS}
)

link_directories(/usr/local/lib)

add_executable(${PROJECT_NAME}_scan_node 
  src/lakibeam1_scan.cpp 
  src/remote.cpp)
  
target_link_libraries(${PROJECT_NAME}_scan_node ${ament_LIBRARIES} curl rby1-sdk)
ament_target_dependencies(${PROJECT_NAME}_scan_node 
  rclcpp rclpy sensor_msgs 
  tf2 
  tf2_ros 
  tf2_geometry_msgs 
  std_msgs 
  CURL)

install(PROGRAMS
  src/rby1_sdk_publisher.py
  src/mobile_publisher_test.py
  src/mobile_subscriber_test.py
  src/merge_laserscan_tf.py
  DESTINATION lib/${PROJECT_NAME}
)

install(TARGETS ${PROJECT_NAME}_scan_node
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch rviz
  DESTINATION share/${PROJECT_NAME}
)
