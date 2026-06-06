import rclpy
from rclpy.node import Node

from hw3_interfaces.srv import CheckPalindrome
from hw3_palindrome.palindrome_logic import is_palindrome


class PalindromeServer(Node):

    def __init__(self):
        super().__init__('palindrome_server')
        self.service = self.create_service(
            CheckPalindrome,
            'check_palindrome',
            self.check_palindrome_callback)
        self.get_logger().info('Palindrome service is ready')

    def check_palindrome_callback(self, request, response):
        response.is_palindrome = is_palindrome(request.number)
        self.get_logger().info(
            'Number ' + str(request.number) + ': ' + str(response.is_palindrome))
        return response


def main(args=None):
    rclpy.init(args=args)
    node = PalindromeServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
