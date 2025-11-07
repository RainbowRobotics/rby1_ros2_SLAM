#!/usr/bin/env python3
import rclpy
import numpy as np
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point, Quaternion, Twist, TransformStamped
from tf2_ros import TransformBroadcaster
import rby1_sdk

class RBY1OdomNode(Node):
    def __init__(self):
        super().__init__('rby1_sdk_odom_node_debug')
        self.get_logger().info("🚀 Node initializing...")
        self.tf_broadcaster = TransformBroadcaster(self)

        self.declare_parameter('address', '192.168.30.1:50051')
        self.declare_parameter('model', 'a')
        self.declare_parameter('power', '.*')
        # self.declare_parameter('servo', '^(right_wheel|left_wheel)$')

        self.initialized = False
        self.initial_x = 0.0
        self.initial_y = 0.0
        self.initial_yaw = 0.0

        address = self.get_parameter('address').get_parameter_value().string_value
        model = self.get_parameter('model').get_parameter_value().string_value
        power = self.get_parameter('power').get_parameter_value().string_value
        # servo = self.get_parameter('servo').get_parameter_value().string_value

        self.get_logger().info(f"🔧 Connecting to robot at {address}, model={model}, power={power}")
        # self.get_logger().info(f"🔧 Connecting to robot at {address}, model={model}, power={power}, servo={servo}")

        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)

        try:
            self.robot = rby1_sdk.create_robot(address, model)
            self.robot.connect()
            if not self.robot.is_connected():
                self.get_logger().error("❌ Robot not connected.")
                return
            self.get_logger().info("✅ Robot connected successfully.")
        except Exception as e:
            self.get_logger().error(f"❌ Failed to connect: {e}")
            return

        try:
            if not self.robot.is_power_on(power):
                self.get_logger().warn("⚠️ Power is OFF, attempting power_on()...")
                if not self.robot.power_on(power):
                    self.get_logger().error("❌ Failed to power on robot")
                    return
        except Exception as e:
            self.get_logger().error(f"❌ Exception during power_on(): {e}")
            return

        # try:
        #     if not self.robot.is_servo_on(servo):
        #         self.get_logger().warn("⚠️ Servo is OFF, attempting power_on()...")
        #         if not self.robot.servo_on(servo):
        #             self.get_logger().error("❌ Failed to servo on robot")
        #             return
        # except Exception as e:
        #     self.get_logger().error(f"❌ Exception during servo_on(): {e}")
        #     return

        try:
            self.robot.start_state_update(self.state_callback, rate=10)
        except Exception as e:
            self.get_logger().error(f"❌ start_state_update() failed: {e}")
            return

        self.get_logger().info("✅ RBY1 SDK connected and streaming state")

    @staticmethod
    def yaw_to_quaternion(yaw: float) -> Quaternion:
        q = Quaternion()
        q.x = 0.0
        q.y = 0.0
        q.z = np.sin(yaw / 2.0)
        q.w = np.cos(yaw / 2.0)
        return q

    def state_callback(self, rs: rby1_sdk.RobotState_A):
        msg = Odometry()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'odom'
        msg.child_frame_id = 'base_link'
    
        
        try:
            T = np.array(rs.odometry)
            
            if not self.initialized:
                self.initial_x = T[0, 2]
                self.initial_y = T[1, 2]
                self.initial_yaw = np.arctan2(T[1, 0], T[0, 0])
                self.initialized = True
                self.get_logger().info("📍 Initial odometry set.")
                return
            
            # --- 변환 행렬에서 위치 및 자세 추출 ---
            x = T[0, 2] - self.initial_x
            y = T[1, 2] - self.initial_y
            z = 0.0
            real_yaw = np.arctan2(T[1, 0], T[0, 0])
            yaw = real_yaw - self.initial_yaw

            # --- Quaternion 변환 (yaw -> quaternion) ---
            q = self.yaw_to_quaternion(yaw)

            # --- Odometry 메시지 구성 ---
            msg.pose.pose.position = Point(x=x, y=y, z=z)
            msg.pose.pose.orientation = q
            msg.twist.twist = Twist()
            msg.twist.twist.linear.x = 0.0
            msg.twist.twist.angular.z = 0.0

            # --- TF 브로드캐스트 ---
            t = TransformStamped()
            t.header.stamp = msg.header.stamp
            t.header.frame_id = "odom"
            t.child_frame_id = "base_link"
            t.transform.translation.x = x
            t.transform.translation.y = y
            t.transform.translation.z = z
            t.transform.rotation = q  # ✅ 올바르게 설정

            self.tf_broadcaster.sendTransform(t)

            # --- Publish ---
            self.odom_pub.publish(msg)
            self.get_logger().info(f"Odom published: x={x:.3f}, y={y:.3f}, yaw={yaw:.3f}")

        except Exception as e:
            self.get_logger().error(f"⚠️ Invalid state structure: {e}")
            return

    def destroy_node(self):
        try:
            self.robot.stop_state_update()
            self.robot.disconnect()
        except Exception as e:
            self.get_logger().warn(f"⚠️ Error during disconnect: {e}")
        self.get_logger().info("🔌 Node shutdown complete")
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = RBY1OdomNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
