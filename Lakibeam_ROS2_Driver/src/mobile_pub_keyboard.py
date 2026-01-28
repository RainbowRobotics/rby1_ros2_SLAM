#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import termios
import tty
import select
import signal

class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__('keyboard_teleop')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.timer = self.create_timer(0.02, self.loop)  # 50 Hz

        self.pressed_keys = set()

        # target velocity
        self.target = {'x': 0.0, 'y': 0.0, 'w': 0.0}

        # filtered velocity
        self.vel = {'x': 0.0, 'y': 0.0, 'w': 0.0}

        self.max_v = 0.3
        self.max_w = 0.6
        self.alpha = 0.15  # LPF 

        # terminal 설정
        self.old_term = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

        signal.signal(signal.SIGINT, self.shutdown)

        self.get_logger().info(
            "w/s: linear_x ±\n"
            "a/d: linear_y ±\n"
            "q/e: angular_z ±\n"
            "Ctrl-C to exit"
        )

    def shutdown(self, sig, frame):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_term)
        rclpy.shutdown()
        sys.exit(0)

    def get_key(self):
        if select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.read(1)
        return None

    def update_keys(self):
        key = self.get_key()
        if key:
            self.pressed_keys.add(key)

    def compute_target(self):
        self.target = {'x': 0.0, 'y': 0.0, 'w': 0.0}

        if 'w' in self.pressed_keys:
            self.target['x'] += self.max_v
        if 's' in self.pressed_keys:
            self.target['x'] -= self.max_v

        if 'd' in self.pressed_keys:
            self.target['y'] += self.max_v
        if 'a' in self.pressed_keys:
            self.target['y'] -= self.max_v

        if 'q' in self.pressed_keys:
            self.target['w'] += self.max_w
        if 'e' in self.pressed_keys:
            self.target['w'] -= self.max_w

        self.pressed_keys.clear()

    def lpf(self):
        for k in self.vel:
            self.vel[k] += self.alpha * (self.target[k] - self.vel[k])

    def loop(self):
        self.update_keys()
        self.compute_target()
        self.lpf()

        msg = Twist()
        msg.linear.x = self.vel['x']
        msg.linear.y = self.vel['y']
        msg.angular.z = self.vel['w']
        self.pub.publish(msg)

def main():
    rclpy.init()
    node = KeyboardTeleop()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
