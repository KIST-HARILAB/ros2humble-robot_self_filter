
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import (
    LaunchConfiguration,
    PythonExpression,
    PathJoinSubstitution,
    Command,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # ------------------------------------------------------------------
    # Launch arguments
    # ------------------------------------------------------------------
    description_name_arg = DeclareLaunchArgument(
        "description_name",
        default_value="/robot_description",
        description="ROS parameter that publishes the URDF",
    )

    zero_for_removed_points_arg = DeclareLaunchArgument(
        "zero_for_removed_points",
        default_value="true",
        description="Set removed points to (0,0,0) if true",
    )

    lidar_sensor_type_arg = DeclareLaunchArgument(
        "lidar_sensor_type",
        default_value="0",
        description="Sensor type: 0=XYZSensor, 1=XYZRGBSensor, 2=OusterSensor, …",
    )

    in_pointcloud_topic_arg = DeclareLaunchArgument(
        "in_pointcloud_topic",
        default_value="/floating_camera_pointcloud_preprocessed",
        description="Input PointCloud2 topic",
    )

    out_pointcloud_topic_arg = DeclareLaunchArgument(
        "out_pointcloud_topic",
        default_value="/pointcloud_filtered",
        description="Output PointCloud2 topic",
    )

    robot_description_path_arg = DeclareLaunchArgument(
        "robot_description_path",
        default_value="~/franka/Franka.urdf",
        description="Absolute path to the URDF file",
    )

    # Expand user path and read URDF content at runtime
    robot_description_path_expanded = PythonExpression(
        [
            "__import__('os').path.expanduser('",
            LaunchConfiguration("robot_description_path"),
            "')",
        ]
    )
    robot_description_content = Command(["cat ", robot_description_path_expanded])

    filter_config_arg = DeclareLaunchArgument(
        "filter_config",
        default_value=PathJoinSubstitution(
            [FindPackageShare("robot_self_filter"), "config", "filter_config.yaml"]
        ),
        description="Path to filter configuration YAML",
    )

    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulated /clock if true",
    )

    # ------------------------------------------------------------------
    # Log the selected filter configuration
    # ------------------------------------------------------------------
    log_config = LogInfo(msg=LaunchConfiguration("filter_config"))

    # ------------------------------------------------------------------
    # Self-filter node
    # ------------------------------------------------------------------
    self_filter_node = Node(
        package="robot_self_filter",
        executable="self_filter",
        name="self_filter",
        output="screen",
        parameters=[
            LaunchConfiguration("filter_config"),  # YAML with filter parameters
            {
                "lidar_sensor_type": LaunchConfiguration("lidar_sensor_type"),
                "robot_description": ParameterValue(
                    robot_description_content, value_type=str
                ),
                "zero_for_removed_points": LaunchConfiguration(
                    "zero_for_removed_points"
                ),
                "use_sim_time": LaunchConfiguration("use_sim_time"),
            },
        ],
        remappings=[
            ("/robot_description", LaunchConfiguration("description_name")),
            ("/cloud_in", LaunchConfiguration("in_pointcloud_topic")),
            ("/cloud_out", LaunchConfiguration("out_pointcloud_topic")),
        ],
    )

    # ------------------------------------------------------------------
    # Final launch description
    # ------------------------------------------------------------------
    return LaunchDescription(
        [
            description_name_arg,
            zero_for_removed_points_arg,
            lidar_sensor_type_arg,
            in_pointcloud_topic_arg,
            out_pointcloud_topic_arg,
            robot_description_path_arg,
            filter_config_arg,
            use_sim_time_arg,
            log_config,
            self_filter_node,
        ]
    )
