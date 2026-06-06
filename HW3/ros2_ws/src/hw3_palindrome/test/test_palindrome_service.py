import time

import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from hw3_interfaces.srv import CheckPalindrome
from hw3_palindrome.palindrome_server import PalindromeServer


def spin_until_future_done(executor, future, timeout_sec):
    finish_time = time.monotonic() + timeout_sec

    while time.monotonic() < finish_time:
        executor.spin_once(timeout_sec=0.1)
        if future.done():
            return True

    return False


def test_palindrome_service_answers_true_and_false():
    rclpy.init()
    server = PalindromeServer()
    client_node = Node('test_palindrome_client')
    executor = MultiThreadedExecutor()
    executor.add_node(server)
    executor.add_node(client_node)

    try:
        client = client_node.create_client(CheckPalindrome, 'check_palindrome')
        assert client.wait_for_service(timeout_sec=2.0)

        request = CheckPalindrome.Request()
        request.number = 1221
        future = client.call_async(request)
        assert spin_until_future_done(executor, future, 3.0)
        assert future.result().is_palindrome

        request = CheckPalindrome.Request()
        request.number = 1234
        future = client.call_async(request)
        assert spin_until_future_done(executor, future, 3.0)
        assert not future.result().is_palindrome
    finally:
        executor.shutdown()
        server.destroy_node()
        client_node.destroy_node()
        rclpy.shutdown()
