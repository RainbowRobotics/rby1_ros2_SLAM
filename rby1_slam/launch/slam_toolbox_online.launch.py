# <?xml version="1.0"?>

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
    Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[{
            'use_sim_time': False,
            'odom_frame': 'base_link',
            'map_frame': 'map',
            'base_frame': 'base_link',
            'scan_topic': '/scan_merged',
            'resolution': 0.05,
            'max_laser_range': 20.0,
            'sensor_data_queue_size': 100,  # 🧩 큐 용량 확장
            'throttle_scans': 1             # 2로 하면 2개 중 1개만 처리
        }],
    )
    ,
    ])
