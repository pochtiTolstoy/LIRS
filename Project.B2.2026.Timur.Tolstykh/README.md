# Commands

## Build

```bash
source /opt/ros/jazzy/setup.zsh
colcon build --symlink-install
source install/setup.zsh
```

## Clean Rebuild

```bash
rm -rf build install log
source /opt/ros/jazzy/setup.zsh
colcon build --symlink-install
source install/setup.zsh
```

## Run Demo

Terminal 1:

```bash
source /opt/ros/jazzy/setup.zsh
ros2 run turtlesim turtlesim_node
```

Terminal 2:

```bash
source /opt/ros/jazzy/setup.zsh
source install/setup.zsh
ros2 run traffic_light_project traffic_light_node
```

Terminal 3:

```bash
source /opt/ros/jazzy/setup.zsh
source install/setup.zsh
ros2 run traffic_light_project turtle_driver_node
```

## Watch Traffic Light

```bash
source /opt/ros/jazzy/setup.zsh
source install/setup.zsh
ros2 topic echo /traffic_light/state
```

## Run Tests

```bash
source /opt/ros/jazzy/setup.zsh
source install/setup.zsh
colcon test --event-handlers console_direct+
colcon test-result --verbose
```
