#!/usr/bin/env python3

import rclpy
import numpy as np
from rclpy.node import Node
# from control_msgs.msg import JointTrajectoryControllerState
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray
import time
import argparse
import rby1_sdk
import rclpy
import sys

D2R = np.pi / 180



class GlobalVariable:
    ready = False
    torso_position_data = np.zeros(6)
    right_position_data = np.zeros(7)
    left_position_data = np.zeros(7)
    head_position_data = np.zeros(2)
    mobile_data = np.zeros(2)    
    

class SimpleSubscriber(Node):
    def __init__(self):
        super().__init__('simple_subscriber')
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        GlobalVariable.mobile_data = msg.linear.x, msg.linear.y, msg.angular.z
        GlobalVariable.ready = True

def main(address, model):
    rclpy.init()
    subscriber = SimpleSubscriber()
    
    from threading import Thread
    ros_thread = Thread(target=rclpy.spin, args=(subscriber,))
    ros_thread.start()
    
    robot = rby1_sdk.create_robot(address, model)
    robot.connect()

    print(robot.set_parameter("joint_position_command.cutoff_frequency", "5"))
    print(robot.set_parameter("default.acceleration_limit_scaling", "0.8"))

    robot.power_on(".*")
    robot.servo_on(".*")
    # robot.servo_on("^(right_wheel|left_wheel)$")
    # robot.servo_on("^(right_wheel|left_wheel|torso_[0-5]|right_arm[0-6]|left_arm[0-6])$")
    robot.reset_fault_control_manager()
    robot.enable_control_manager()

    def initial_joint_position_command(robot):
        print("example ready")

        # Initialize joint positions
        q_joint_waist = np.zeros(6)
        q_joint_right_arm = np.zeros(7)
        q_joint_left_arm = np.zeros(7)

        # Set specific joint positions
        q_joint_waist = [0, 60 * D2R, -120 * D2R, 60 * D2R, 0, 0] 
        q_joint_right_arm = [0, -5 * D2R, 0, -120 * D2R, 0, 30 * D2R, 0]
        q_joint_left_arm = [0, 5 * D2R, 0, -120 * D2R, 0, 30 * D2R, 0]
    
        rc = rby1_sdk.RobotCommandBuilder().set_command(
            rby1_sdk.ComponentBasedCommandBuilder()
            .set_body_command(rby1_sdk.JointPositionCommandBuilder()
                .set_command_header(rby1_sdk.CommandHeaderBuilder()
                .set_control_hold_time(2))
                .set_minimum_time(3)
                .set_position(q_joint_waist + q_joint_right_arm + q_joint_left_arm)
                )
        )

        rv = robot.send_command(rc, 10).get()
        return 0

    def example_SE2_x_forward_command(robot):
        print("forward ready")
    
        rc = rby1_sdk.RobotCommandBuilder().set_command(
            rby1_sdk.ComponentBasedCommandBuilder()
            .set_mobility_command(rby1_sdk.SE2VelocityCommandBuilder()
                .set_command_header(rby1_sdk.CommandHeaderBuilder().set_control_hold_time(3))
                .set_velocity(np.array([0.3, 0]), 0)) ## 선속도, 각속도, heading angle [rad]
        )
        
        rv = robot.send_command(rc, 10).get()
        return 0

    def example_joint_vel_x_backward_command(robot):
        print("backwrard ready")
        
        rc = rby1_sdk.RobotCommandBuilder().set_command(
            rby1_sdk.ComponentBasedCommandBuilder()
            .set_mobility_command(rby1_sdk.JointVelocityCommandBuilder()
                .set_command_header(rby1_sdk.CommandHeaderBuilder().set_control_hold_time(3))
                .set_velocity([np.pi] * 2) # wheel joint velocity [rad/s]
            )
        )
        
        rv = robot.send_command(rc, 10).get()
        return 0
    
    if not initial_joint_position_command(robot):
        print("finish motion")

    stream = robot.create_command_stream()

    try:
        while True:
            while not GlobalVariable.ready:
                time.sleep(0.001)

            rc = rby1_sdk.RobotCommandBuilder().set_command(
                rby1_sdk.ComponentBasedCommandBuilder()
                .set_mobility_command(rby1_sdk.SE2VelocityCommandBuilder()
                    .set_command_header(rby1_sdk.CommandHeaderBuilder().set_control_hold_time(100))
                    .set_minimum_time(0.0202)
                    .set_velocity(np.array([GlobalVariable.mobile_data[0], GlobalVariable.mobile_data[1]]), GlobalVariable.mobile_data[2])) ## 선속도, 각속도, heading angle [rad]
            )
            
            rv = stream.send_command(rc)
            GlobalVariable.ready = False



    except KeyboardInterrupt:
        print("Stopping robot control...")

    finally:
        subscriber.destroy_node()
        rclpy.shutdown()
        ros_thread.join()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="mobile_command")
    parser.add_argument("--address", type=str, required=True, help="Robot address")
    parser.add_argument(
        "--model", type=str, default="a", help="Robot Model Name (default: 'a')"
    )
    args = parser.parse_args()
    main(
        address=args.address,
        model=args.model
    )
