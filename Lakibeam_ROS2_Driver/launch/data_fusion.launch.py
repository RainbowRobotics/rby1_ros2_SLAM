# <?xml version="1.0"?>
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, LogInfo
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# base_link → laser (LiDAR 위치 관계)
# left lidar
static_tf_pub_lidar1 = Node(
    package='tf2_ros',
    executable='static_transform_publisher',
    name='static_tf_pub_lidar1',
    arguments=['0.228', '0.1765', '0.22282', '0.0', '0.0', '0.4617486', '0.8870110', 'base_scan', 'laser0']
)

# right lidar
static_tf_pub_lidar0 = Node(
    package='tf2_ros',
    executable='static_transform_publisher',
    name='static_tf_pub_lidar0',
    arguments=['0.228', '-0.1765', '0.22282', '0.0', '0.0', '-0.4617486', '0.8870110', 'base_scan', 'laser1']
)

# map odom 임시 TF
static_tf_pub_map_odom = Node(
    package='tf2_ros',
    executable='static_transform_publisher',
    name='static_tf_pub_map_odom',
    arguments=['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', 'map', 'odom']
)

# # base link
# static_tf_pub_odom_to_base = Node(
#     package='tf2_ros',
#     executable='static_transform_publisher',
#     name='static_tf_pub_odom_to_base',
#     arguments=['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', 'odom', 'base_link']
# )

# base link
static_tf_pub_base_to_scan = Node(
    package='tf2_ros',
    executable='static_transform_publisher',
    name='static_tf_pub_base_to_scan',
    arguments=['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', 'base_link', 'base_scan']
)

def generate_launch_description():
    # frame_id = LaunchConfiguration('frame_id')
    frame_id0 = LaunchConfiguration('frame_id0')
    frame_id1 = LaunchConfiguration('frame_id1')
    output_topic0 = LaunchConfiguration('output_topic0')
    output_topic1 = LaunchConfiguration('output_topic1')
    inverted = LaunchConfiguration('inverted')
    hostip = LaunchConfiguration('hostip')
    port0 = LaunchConfiguration('port0')
    port1 = LaunchConfiguration('port1')
    angle_offset = LaunchConfiguration('angle_offset')
    scanfreq = LaunchConfiguration('scanfreq')
    filter = LaunchConfiguration('filter')
    laser_enable = LaunchConfiguration('laser_enable')
    scan_range_start = LaunchConfiguration('scan_range_start')
    scan_range_stop = LaunchConfiguration('scan_range_stop')
    sensorip0 = LaunchConfiguration('sensorip0')
    sensorip1 = LaunchConfiguration('sensorip1')
    

    declare_frame_id0_cmd = DeclareLaunchArgument(
    'frame_id0',
    default_value='laser0',
    )
    declare_frame_id1_cmd = DeclareLaunchArgument(
    'frame_id1',
    default_value='laser1',
    )
    declare_output_topic0_cmd = DeclareLaunchArgument(
    'output_topic0',
    default_value='scan0',
    )
    declare_output_topic1_cmd = DeclareLaunchArgument(
    'output_topic1',
    default_value='scan1',
    )
    declare_inverted_cmd = DeclareLaunchArgument(
    'inverted',
    default_value='false',
    )
    declare_hostip_cmd = DeclareLaunchArgument(
    'hostip',
    default_value='0.0.0.0',
    )
    declare_port0_cmd = DeclareLaunchArgument(
    'port0',
    default_value='"2367"',
    )
    declare_port1_cmd = DeclareLaunchArgument(
    'port1',
    default_value='"2368"',
    )
    declare_angle_offset_cmd = DeclareLaunchArgument(
    'angle_offset',
    default_value='0',
    )
    declare_filter_cmd = DeclareLaunchArgument(
    'filter',
    default_value='"3"',
    )
    declare_scanfreq_cmd = DeclareLaunchArgument(
    'scanfreq',
    default_value='"30"',
    )
    declare_laser_enable_cmd = DeclareLaunchArgument(
    'laser_enable',
    default_value='"true"',
    )
    declare_scan_range_start_cmd = DeclareLaunchArgument(
    'scan_range_start',
    default_value='"45"',
    )
    declare_scan_range_stop_cmd = DeclareLaunchArgument(
    'scan_range_stop',
    default_value='"315"',
    )
    declare_sensorip0_cmd = DeclareLaunchArgument(
    'sensorip0',
    default_value='192.168.30.10',
    )
    declare_sensorip1_cmd = DeclareLaunchArgument(
    'sensorip1',
    default_value='192.168.30.11',
    )

    # left lidar
    richbeam_lidar_node0 = Node(
        package='lakibeam1',
        name='richbeam_lidar_node0',
        executable='lakibeam1_scan_node',
        parameters=[{
            'frame_id':frame_id0,
            'output_topic':output_topic0,
            'inverted':inverted,
            'hostip':hostip,
            'port':port0,
            'sensorip':sensorip0,
            'angle_offset':angle_offset
        }],
        output='screen'
    )
    # right lidar
    richbeam_lidar_node1 = Node(
        package='lakibeam1',
        name='richbeam_lidar_node1',
        executable='lakibeam1_scan_node',
        parameters=[{
            'frame_id':frame_id1,
            'output_topic':output_topic1,
            'inverted':inverted,
            'hostip':hostip,
            'sensorip':sensorip1,
            'port':port1,
            'angle_offset':angle_offset
        }],
        output='screen'
    )
    lakibeam1_pcd_dir = get_package_share_directory('lakibeam1')
    rviz_config_dir = os.path.join(lakibeam1_pcd_dir,'rviz','lakibeam1_scan_dual.rviz')
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
 
    rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_dir],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen')
    
    sdk_node = Node(
        package='lakibeam1',
        executable='rby1_sdk_publisher.py',
        name='rby1_sdk_publisher',
        parameters=[{
            'address': '192.168.30.1:50051',
            'model': 'a',
            'power': '.*',
        }],
        output='screen'
    )
    
    data_merge_node = Node(
        package='lakibeam1',
        executable='merge_laserscan_tf.py',
        name='data_fusion_publisher',
        output='screen'
    )
    
    
    start_data_publisher = TimerAction(period=1.0, actions=[data_merge_node])
    start_sdk_publisher = TimerAction(period=1.0, actions=[sdk_node])
    
    ld = LaunchDescription()


    ld.add_action(static_tf_pub_lidar0)
    ld.add_action(static_tf_pub_lidar1)
    # ld.add_action(static_tf_pub_odom_to_base)
    ld.add_action(static_tf_pub_map_odom)
    ld.add_action(static_tf_pub_base_to_scan)
    ld.add_action(declare_frame_id0_cmd)
    ld.add_action(declare_frame_id1_cmd)
    ld.add_action(declare_output_topic0_cmd)
    ld.add_action(declare_output_topic1_cmd)
    ld.add_action(declare_inverted_cmd)
    ld.add_action(declare_hostip_cmd)
    ld.add_action(declare_port0_cmd)
    ld.add_action(declare_port1_cmd)
    ld.add_action(declare_angle_offset_cmd)
    ld.add_action(declare_filter_cmd)
    ld.add_action(declare_scanfreq_cmd)
    ld.add_action(declare_laser_enable_cmd)
    ld.add_action(declare_scan_range_start_cmd)
    ld.add_action(declare_scan_range_stop_cmd)
    ld.add_action(declare_sensorip0_cmd)
    ld.add_action(declare_sensorip1_cmd)
    ld.add_action(richbeam_lidar_node0)
    ld.add_action(richbeam_lidar_node1)
    ld.add_action(start_data_publisher)
    ld.add_action(start_sdk_publisher)
    ld.add_action(rviz_node)
    return ld
