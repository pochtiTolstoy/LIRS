import time

import rclpy
from rclpy.action import ActionClient
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from hw4_factorization.factor_server import FactorServer
from hw4_interfaces.action import Factorize


def spin_until_future_done(executor, future, timeout_sec):
    finish_time = time.monotonic() + timeout_sec

    while time.monotonic() < finish_time:
        executor.spin_once(timeout_sec=0.1)
        if future.done():
            return True

    return False


def test_factor_action_returns_result_and_feedback():
    rclpy.init()
    server = FactorServer()
    client_node = Node('test_factor_client')
    executor = MultiThreadedExecutor()
    executor.add_node(server)
    executor.add_node(client_node)

    feedback_numbers = []

    def feedback_callback(feedback_msg):
        feedback_numbers.append(feedback_msg.feedback.factor)

    try:
        client = ActionClient(client_node, Factorize, 'factorize_number')
        assert client.wait_for_server(timeout_sec=2.0)

        goal = Factorize.Goal()
        goal.number = 84
        goal_future = client.send_goal_async(goal, feedback_callback=feedback_callback)
        assert spin_until_future_done(executor, goal_future, 3.0)

        goal_handle = goal_future.result()
        assert goal_handle.accepted

        result_future = goal_handle.get_result_async()
        assert spin_until_future_done(executor, result_future, 5.0)

        result = result_future.result().result
        assert list(result.factors) == [2, 2, 3, 7]
        assert feedback_numbers == [2, 2, 3, 7]
    finally:
        executor.shutdown()
        server.destroy_node()
        client_node.destroy_node()
        rclpy.shutdown()
