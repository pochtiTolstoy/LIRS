# Homework 2

## Description

This workspace contains the ROS 2 Python package `my_package`.

The package includes two nodes:

- `talker` publishes natural numbers from `1` to `N` into the topic `/NaturalNumbersTopic`
- `listener` subscribes to `/NaturalNumbersTopic`, checks whether each number is prime, and publishes only the status `prime` or `not prime` into `/PrimeNumberTopic`

The upper bound `N` is passed to the publisher as a ROS 2 parameter.

## Requirements

- ROS 2 Jazzy
- `colcon`
- ROS 2 Python dependencies: `rclpy`, `std_msgs`

## Build

```bash
cd HW2/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select my_package
source install/setup.bash
```

## Run

Open three terminals.

Terminal 1:

```bash
cd HW2/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run my_package talker --ros-args -p N:=10
```

Terminal 2:

```bash
cd HW2/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run my_package listener
```

Terminal 3:

```bash
cd HW2/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 topic echo /PrimeNumberTopic
```