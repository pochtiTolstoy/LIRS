from math import pi

from geometry_msgs.msg import Twist
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from traffic_light_interfaces.action import CrossIntersection
from traffic_light_interfaces.msg import TrafficLight
from traffic_light_project.turtle_logic import axis_position
from traffic_light_project.turtle_logic import desired_heading
from traffic_light_project.turtle_logic import has_cleared_center
from traffic_light_project.turtle_logic import should_request_crossing
from traffic_light_project.turtle_logic import should_reverse
from traffic_light_project.turtle_logic import should_stop
from turtlesim.msg import Pose
from turtlesim.srv import Spawn, TeleportAbsolute


INTERSECTION = 5.0
LINEAR_SPEED = 1.6
ANGULAR_GAIN = 5.0
REQUEST_DISTANCE = 1.2
STOP_DISTANCE = 0.7
LIGHT_BUFFER_DISTANCE = 1.1
CLEAR_DISTANCE = 0.5
MIN_POSITION = 0.8
MAX_POSITION = 10.2


def normalize_angle(angle: float) -> float:
    while angle > pi:
        angle -= 2.0 * pi
    while angle < -pi:
        angle += 2.0 * pi
    return angle


class TurtleDriverNode(Node):
    def __init__(self) -> None:
        super().__init__('turtle_driver_node')

        self.light_state = {
            'active_axis': TrafficLight.AXIS_HORIZONTAL,
            'color': TrafficLight.COLOR_GREEN,
        }
        self.poses = {}
        self.turtles = {
            'turtle1': {
                'axis': TrafficLight.AXIS_HORIZONTAL,
                'direction': 1,
                'request_pending': False,
                'permission_granted': False,
            },
            'turtle2': {
                'axis': TrafficLight.AXIS_VERTICAL,
                'direction': 1,
                'request_pending': False,
                'permission_granted': False,
            },
        }

        self.cmd_publishers = {
            'turtle1': self.create_publisher(Twist, '/turtle1/cmd_vel', 10),
            'turtle2': self.create_publisher(Twist, '/turtle2/cmd_vel', 10),
        }
        self.create_subscription(Pose, '/turtle1/pose', self.pose_callback('turtle1'), 10)
        self.create_subscription(Pose, '/turtle2/pose', self.pose_callback('turtle2'), 10)
        self.create_subscription(
            TrafficLight,
            '/traffic_light/state',
            self.light_callback,
            10,
        )

        self.crossing_client = ActionClient(
            self,
            CrossIntersection,
            '/traffic_light/request_crossing',
        )
        self.spawn_client = self.create_client(Spawn, '/spawn')
        self.teleport_client = self.create_client(
            TeleportAbsolute,
            '/turtle1/teleport_absolute',
        )

        self.did_setup = False
        self.setup_timer = self.create_timer(0.5, self.setup_turtles)
        self.control_timer = self.create_timer(0.05, self.control_turtles)
        self.get_logger().info('turtle driver started')

    def pose_callback(self, turtle_name: str):
        def callback(msg: Pose) -> None:
            self.poses[turtle_name] = msg

        return callback

    def light_callback(self, msg: TrafficLight) -> None:
        self.light_state = {
            'active_axis': msg.active_axis,
            'color': msg.color,
        }

    def setup_turtles(self) -> None:
        if self.did_setup:
            return

        if not self.spawn_client.service_is_ready():
            self.spawn_client.wait_for_service(timeout_sec=0.1)
            return

        if not self.teleport_client.service_is_ready():
            self.teleport_client.wait_for_service(timeout_sec=0.1)
            return

        teleport = TeleportAbsolute.Request()
        teleport.x = 1.0
        teleport.y = INTERSECTION
        teleport.theta = 0.0
        self.teleport_client.call_async(teleport)

        spawn = Spawn.Request()
        spawn.x = INTERSECTION
        spawn.y = 1.0
        spawn.theta = pi / 2.0
        spawn.name = 'turtle2'
        self.spawn_client.call_async(spawn)

        self.did_setup = True
        self.setup_timer.cancel()
        self.get_logger().info('turtles positioned on crossing paths')

    def control_turtles(self) -> None:
        for turtle_name, turtle in self.turtles.items():
            pose = self.poses.get(turtle_name)
            if pose is None:
                continue

            position = axis_position(turtle['axis'], pose.x, pose.y)
            if should_reverse(position, turtle['direction'], MIN_POSITION, MAX_POSITION):
                turtle['direction'] *= -1
                turtle['request_pending'] = False
                turtle['permission_granted'] = False

            if turtle['permission_granted'] and has_cleared_center(
                position,
                turtle['direction'],
                INTERSECTION,
                CLEAR_DISTANCE,
            ):
                turtle['permission_granted'] = False

            if should_request_crossing(
                turtle,
                position,
                INTERSECTION,
                REQUEST_DISTANCE,
            ):
                self.request_crossing(turtle_name, turtle)

            stop = should_stop(
                turtle,
                self.light_state,
                position,
                INTERSECTION,
                STOP_DISTANCE,
                LIGHT_BUFFER_DISTANCE,
                TrafficLight.COLOR_GREEN,
            )
            twist = self.build_twist(pose, turtle['axis'], turtle['direction'], stop)
            self.cmd_publishers[turtle_name].publish(twist)

    def request_crossing(self, turtle_name: str, turtle: dict) -> None:
        if not self.crossing_client.server_is_ready():
            self.crossing_client.wait_for_server(timeout_sec=0.0)
            return

        goal = CrossIntersection.Goal()
        goal.turtle_name = turtle_name
        goal.axis = turtle['axis']

        turtle['request_pending'] = True
        send_goal_future = self.crossing_client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback(turtle_name),
        )
        send_goal_future.add_done_callback(self.goal_response_callback(turtle_name))

    def feedback_callback(self, turtle_name: str):
        def callback(feedback_msg) -> None:
            feedback = feedback_msg.feedback
            self.get_logger().debug(
                turtle_name + ' ' + feedback.status + ' ' + str(feedback.seconds_waiting)
            )

        return callback

    def goal_response_callback(self, turtle_name: str):
        def callback(future) -> None:
            turtle = self.turtles[turtle_name]
            goal_handle = future.result()
            if not goal_handle.accepted:
                turtle['request_pending'] = False
                return

            result_future = goal_handle.get_result_async()
            result_future.add_done_callback(self.crossing_result_callback(turtle_name))

        return callback

    def crossing_result_callback(self, turtle_name: str):
        def callback(future) -> None:
            turtle = self.turtles[turtle_name]
            turtle['request_pending'] = False
            result = future.result().result
            turtle['permission_granted'] = result.allowed

        return callback

    def build_twist(
        self,
        pose: Pose,
        axis: str,
        direction: int,
        stop: bool,
    ) -> Twist:
        target_heading = desired_heading(axis, direction)
        angle_error = normalize_angle(target_heading - pose.theta)

        twist = Twist()
        twist.angular.z = ANGULAR_GAIN * angle_error

        if abs(angle_error) < 0.15 and not stop:
            twist.linear.x = LINEAR_SPEED
        else:
            twist.linear.x = 0.0

        return twist


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TurtleDriverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
