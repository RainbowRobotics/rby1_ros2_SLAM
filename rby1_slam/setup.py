from setuptools import setup

package_name = 'rby1_slam'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/slam_toolbox_online.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    description='rby1 slam integration launch',
    license='Apache License 2.0',
)
