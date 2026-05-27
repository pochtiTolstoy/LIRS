from setuptools import find_packages, setup

package_name = 'traffic_light_project'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yui',
    maintainer_email='tolstihtimur@yandex.ru',
    description='ROS2 turtlesim traffic light intersection project.',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'traffic_light_node = traffic_light_project.traffic_light_node:main',
            'turtle_driver_node = traffic_light_project.turtle_driver_node:main',
        ],
    },
)
