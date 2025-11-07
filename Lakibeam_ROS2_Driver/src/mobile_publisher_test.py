#!/usr/bin/env python3

import sys
import threading
import signal

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt, QTimer

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class MobilityPublisher(Node):
    def __init__(self):
        super().__init__('mobility_publisher_gui')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 50)
        self.linear_x = 0.0
        self.angular_z = 0.0
        self.timer = self.create_timer(0.05, self.timer_callback)

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = self.linear_x
        msg.angular.z = self.angular_z
        self.publisher_.publish(msg)


class ControlWidget(QWidget):
    def __init__(self, ros_node):
        super().__init__()
        self.setWindowTitle("Mobile Robot Control GUI")
        self.node = ros_node
        layout = QVBoxLayout()

        self.linear_label = QLabel("Linear X: 0.00")
        layout.addWidget(self.linear_label)

        self.linear_slider = QSlider(Qt.Horizontal)
        self.linear_slider.setRange(-100, 100)
        self.linear_slider.valueChanged.connect(self.update_linear)
        layout.addWidget(self.linear_slider)

        self.angular_label = QLabel("Angular Z: 0.00")
        layout.addWidget(self.angular_label)

        self.angular_slider = QSlider(Qt.Horizontal)
        self.angular_slider.setRange(-100, 100)
        self.angular_slider.valueChanged.connect(self.update_angular)
        layout.addWidget(self.angular_slider)

        self.setLayout(layout)

    def update_linear(self, value):
        self.node.linear_x = value / 100.0
        self.linear_label.setText(f"Linear X: {self.node.linear_x:.2f}")

    def update_angular(self, value):
        self.node.angular_z = value / 100.0
        self.angular_label.setText(f"Angular Z: {self.node.angular_z:.2f}")


def ros_spin(node):
    rclpy.spin(node)


def main():
    rclpy.init()
    node = MobilityPublisher()

    ros_thread = threading.Thread(target=ros_spin, args=(node,), daemon=True)
    ros_thread.start()

    app = QApplication(sys.argv)
    widget = ControlWidget(node)
    widget.show()

    def shutdown_handler(signum, frame):
        print("Shutting down gracefully...")
        node.destroy_node()
        rclpy.shutdown()
        app.quit()

    signal.signal(signal.SIGINT, shutdown_handler)

    timer = QTimer()
    timer.start(100)
    timer.timeout.connect(lambda: None)

    app.exec()


if __name__ == '__main__':
    main()
