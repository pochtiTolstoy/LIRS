import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from std_msgs.msg import Int32


def is_prime(number):
    if number < 2:
        return False

    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 1

    return True


class PrimeFilter(Node):

    def __init__(self):
        super().__init__('prime_filter')
        self.subscription = self.create_subscription(
            Int32,
            'NaturalNumbersTopic',
            self.listener_callback,
            10)
        self.subscription

        self.publisher_ = self.create_publisher(String, 'PrimeNumberTopic', 10)
        self.publisher_


    def listener_callback(self, msg):
        number = msg.data
        filtered_msg = String()


        if is_prime(number):
            filtered_msg.data = 'prime'
            self.get_logger().info(f'Received: {number} (prime)')
        else:
            filtered_msg.data = 'not prime'
            self.get_logger().info(f'Received: {number} (not a prime)')

        self.publisher_.publish(filtered_msg)



def main(args=None):
    rclpy.init(args=args)

    prime_filter = PrimeFilter()
    rclpy.spin(prime_filter)

    prime_filter.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
