import time

from my_package.publisher_member_function import NumberPublisher
from my_package.subscriber_member_function import PrimeFilter
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from std_msgs.msg import String


def spin_until_messages(executor, messages, count, timeout_sec):
    finish_time = time.monotonic() + timeout_sec

    while time.monotonic() < finish_time:
        executor.spin_once(timeout_sec=0.1)
        if len(messages) >= count:
            return True

    return False


def test_topic_prime_filter_works():
    rclpy.init()
    publisher = NumberPublisher()
    prime_filter = PrimeFilter()
    test_node = Node('test_prime_topic_node')
    executor = MultiThreadedExecutor()
    executor.add_node(publisher)
    executor.add_node(prime_filter)
    executor.add_node(test_node)

    messages = []

    def callback(msg):
        messages.append(msg.data)

    try:
        test_node.create_subscription(String, 'PrimeNumberTopic', callback, 10)

        assert spin_until_messages(executor, messages, 5, 5.0)
        assert messages[:5] == [
            'not prime',
            'prime',
            'prime',
            'not prime',
            'prime',
        ]
    finally:
        executor.shutdown()
        publisher.destroy_node()
        prime_filter.destroy_node()
        test_node.destroy_node()
        rclpy.shutdown()
