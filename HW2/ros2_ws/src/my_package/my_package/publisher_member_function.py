import rclpy
from rclpy.node import Node

from std_msgs.msg import Int32


class NumberPublisher(Node):

  def __init__(self):
    super().__init__('number_publisher')
      
    self.declare_parameter('N', 10)
    self.N = self.get_parameter('N').value

    self.publisher_ = self.create_publisher(Int32, 'NaturalNumbersTopic', 10)
    self.timer = self.create_timer(0.5, self.timer_callback)
    self.i = 1

  def timer_callback(self):
    if self.i > self.N:
      self.get_logger().info(f'Finished publishing up to {self.N}')
      self.timer.cancel()
      return

    msg = Int32()
    msg.data = self.i
    self.publisher_.publish(msg)
    self.get_logger().info(f'Publishing: {msg.data}')
    self.i += 1


def main(args=None):
  rclpy.init(args=args)

  number_publisher = NumberPublisher()

  rclpy.spin(number_publisher)

  number_publisher.destroy_node()
  rclpy.shutdown()


if __name__ == '__main__':
  main()
