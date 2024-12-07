import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped, TransformStamped
import tf2_ros
from tf_transformations import quaternion_from_euler

class MapToOdomPublisher(Node):
    def __init__(self):
        super().__init__('map_to_odom_publisher')
        self.declare_parameter('frame_id', 'map')
        self.declare_parameter('child_frame_id', 'odom')

        self.map_frame_id = self.get_parameter('frame_id').value
        self.odom_frame_id = self.get_parameter('child_frame_id').value

        # Initialize transform
        self.current_transform = TransformStamped()
        self.current_transform.header.frame_id = self.map_frame_id
        self.current_transform.child_frame_id = self.odom_frame_id
        self.current_transform.transform.translation.x = 0.0
        self.current_transform.transform.translation.y = 0.0
        self.current_transform.transform.translation.z = 0.0
        self.current_transform.transform.rotation.x = 0.0
        self.current_transform.transform.rotation.y = 0.0
        self.current_transform.transform.rotation.z = 0.0
        self.current_transform.transform.rotation.w = 1.0

        # Subscriber
        self.initial_pose_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/initialpose',
            self.initial_pose_callback,
            10
        )

        # TF2 broadcaster
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        # Timer to publish the transform at regular intervals
        self.timer = self.create_timer(0.1, self.publish_transform)

    def initial_pose_callback(self, msg):
        # Extract pose data
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation

        # Update the transform
        self.current_transform.transform.translation.x = position.x
        self.current_transform.transform.translation.y = position.y
        self.current_transform.transform.translation.z = 0.0  # Assuming 2D plane

        self.current_transform.transform.rotation.x = orientation.x
        self.current_transform.transform.rotation.y = orientation.y
        self.current_transform.transform.rotation.z = orientation.z
        self.current_transform.transform.rotation.w = orientation.w

        self.get_logger().info(f"Updated transform to: {self.current_transform}")

    def publish_transform(self):
        self.current_transform.header.stamp = self.get_clock().now().to_msg()
        self.tf_broadcaster.sendTransform(self.current_transform)

def main(args=None):
    rclpy.init(args=args)
    node = MapToOdomPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
