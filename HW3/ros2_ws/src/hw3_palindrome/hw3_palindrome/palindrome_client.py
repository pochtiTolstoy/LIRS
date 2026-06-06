import sys

import rclpy
from rclpy.node import Node

from hw3_interfaces.srv import CheckPalindrome


class PalindromeClient(Node):

    def __init__(self):
        super().__init__('palindrome_client')
        self.client = self.create_client(CheckPalindrome, 'check_palindrome')

    def send_request(self, number):
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for service...')

        request = CheckPalindrome.Request()
        request.number = number
        return self.client.call_async(request)


def main(args=None):
    rclpy.init(args=args)
    node = PalindromeClient()

    number = 12321
    if len(sys.argv) > 1:
        number = int(sys.argv[1])

    future = node.send_request(number)
    rclpy.spin_until_future_complete(node, future)

    result = future.result()
    node.get_logger().info(str(number) + ' palindrome: ' + str(result.is_palindrome))

    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
