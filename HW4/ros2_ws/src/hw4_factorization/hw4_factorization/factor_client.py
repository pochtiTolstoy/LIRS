import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from hw4_interfaces.action import Factorize


class FactorClient(Node):

    def __init__(self):
        super().__init__('factor_client')
        self.client = ActionClient(self, Factorize, 'factorize_number')

    def send_goal(self, number):
        self.client.wait_for_server()

        goal = Factorize.Goal()
        goal.number = number

        return self.client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback)

    def feedback_callback(self, feedback_msg):
        factor = feedback_msg.feedback.factor
        self.get_logger().info('Feedback factor: ' + str(factor))


def main(args=None):
    rclpy.init(args=args)
    node = FactorClient()

    number = 84
    if len(sys.argv) > 1:
        number = int(sys.argv[1])

    send_goal_future = node.send_goal(number)
    rclpy.spin_until_future_complete(node, send_goal_future)

    goal_handle = send_goal_future.result()
    if not goal_handle.accepted:
        node.get_logger().info('Goal rejected')
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        return

    result_future = goal_handle.get_result_async()
    rclpy.spin_until_future_complete(node, result_future)

    result = result_future.result().result
    node.get_logger().info('Factors: ' + str(list(result.factors)))

    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
