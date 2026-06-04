import time

import rclpy
from rclpy.action import ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import ExternalShutdownException
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from traffic_light_interfaces.action import CrossIntersection
from traffic_light_interfaces.msg import TrafficLight
from traffic_light_interfaces.srv import SetTrafficLight
from traffic_light_project.light_logic import TrafficLightCycle


class TrafficLightNode(Node):
    def __init__(self) -> None:
        super().__init__('traffic_light_node')
        self.callback_group = ReentrantCallbackGroup()

        self.declare_parameter('green_duration', 5.0)
        self.declare_parameter('yellow_duration', 1.5)

        self.cycle = TrafficLightCycle(
            horizontal_axis=TrafficLight.AXIS_HORIZONTAL,
            vertical_axis=TrafficLight.AXIS_VERTICAL,
            green_color=TrafficLight.COLOR_GREEN,
            yellow_color=TrafficLight.COLOR_YELLOW,
            green_duration=self.get_parameter('green_duration').value,
            yellow_duration=self.get_parameter('yellow_duration').value,
        )
        self.started_at = self.get_clock().now()
        # Topic = continuously publish the current traffic light state.
        self.publisher = self.create_publisher(
            TrafficLight,
            '/traffic_light/state',
            10,
        )
        # Service = quick reconfiguration with an immediate response.
        self.service = self.create_service(
            SetTrafficLight,
            '/traffic_light/configure',
            self.configure_traffic_light,
            callback_group=self.callback_group,
        )
        # Action = a turtle may need to wait several seconds for permission.
        self.action_server = ActionServer(
            self,
            CrossIntersection,
            '/traffic_light/request_crossing',
            self.handle_crossing_request,
            callback_group=self.callback_group,
        )
        self.timer = self.create_timer(
            0.2,
            self.publish_state,
            callback_group=self.callback_group,
        )

        self.get_logger().info('traffic light publisher started')

    def elapsed_seconds(self) -> float:
        delta = self.get_clock().now() - self.started_at
        return delta.nanoseconds / 1_000_000_000.0

    def publish_state(self) -> None:
        state = self.current_state()

        message = TrafficLight()
        message.header.stamp = self.get_clock().now().to_msg()
        message.header.frame_id = 'intersection'
        message.active_axis = state['active_axis']
        message.color = state['color']
        message.seconds_remaining = float(state['seconds_remaining'])
        message.cycle_count = state['cycle_count']

        self.publisher.publish(message)

    def current_state(self) -> dict:
        return self.cycle.get_state(self.elapsed_seconds())

    def is_axis_allowed(self, axis: str) -> bool:
        state = self.current_state()
        return state['active_axis'] == axis and state['color'] == TrafficLight.COLOR_GREEN

    def configure_traffic_light(self, request, response):
        try:
            message = self.cycle.configure(
                request.manual,
                request.active_axis,
                request.green_duration,
                request.yellow_duration,
            )
        except ValueError as error:
            response.accepted = False
            response.message = str(error)
            return response

        # Restart time counting so the updated automatic sequence begins from
        # its first phase.
        self.started_at = self.get_clock().now()
        response.accepted = True
        response.message = message
        return response

    def handle_crossing_request(self, goal_handle):
        result = CrossIntersection.Result()
        turtle_name = goal_handle.request.turtle_name
        axis = goal_handle.request.axis

        if not self.cycle.is_valid_axis(axis):
            result.allowed = False
            result.message = 'axis must be horizontal or vertical'
            goal_handle.abort()
            return result

        waiting_started = self.elapsed_seconds()
        feedback = CrossIntersection.Feedback()

        while rclpy.ok():
            if self.is_axis_allowed(axis):
                result.allowed = True
                result.message = turtle_name + ' may cross now'
                try:
                    # During shutdown the action transport can disappear before the
                    # goal is marked as succeeded, so we exit quietly instead.
                    goal_handle.succeed()
                except Exception:
                    result.allowed = False
                    result.message = 'request stopped during shutdown'
                return result

            # Feedback tells the client that the request is still alive and
            # waiting for the matching green phase.
            feedback.status = 'waiting for green on ' + axis
            feedback.seconds_waiting = float(self.elapsed_seconds() - waiting_started)
            try:
                goal_handle.publish_feedback(feedback)
            except Exception:
                break
            time.sleep(0.2)

        result.allowed = False
        result.message = 'request stopped before green'
        try:
            goal_handle.abort()
        except Exception:
            pass
        return result


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TrafficLightNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
