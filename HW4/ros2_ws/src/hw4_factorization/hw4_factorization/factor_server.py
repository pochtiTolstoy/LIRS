import time

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node

from hw4_factorization.factor_logic import factorize
from hw4_interfaces.action import Factorize


class FactorServer(Node):

    def __init__(self):
        super().__init__('factor_server')
        self.action_server = ActionServer(
            self,
            Factorize,
            'factorize_number',
            self.execute_callback)
        self.get_logger().info('Factorization action server is ready')

    def execute_callback(self, goal_handle):
        number = goal_handle.request.number
        result = Factorize.Result()
        feedback = Factorize.Feedback()

        for factor in factorize(number):
            feedback.factor = factor
            goal_handle.publish_feedback(feedback)
            result.factors.append(factor)
            self.get_logger().info('Factor: ' + str(factor))
            time.sleep(0.2)

        goal_handle.succeed()
        return result


def main(args=None):
    rclpy.init(args=args)
    node = FactorServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
