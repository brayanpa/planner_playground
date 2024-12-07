import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from threading import Timer

class GoalPoseRepublisher(Node):
    def __init__(self):
        super().__init__('goal_pose_republisher')
        
        # Suscriptor al tópico /goal_pose_pre
        self.subscription = self.create_subscription(
            PoseStamped,
            '/goal_pose_pre',
            self.goal_pose_callback,
            10
        )
        
        # Publicador al tópico /goal_pose
        self.publisher = self.create_publisher(
            PoseStamped,
            '/goal_pose',
            10
        )
        
        # Inicializar pose
        self.current_goal_pose = None
        
        # Temporizador para publicar cada 5 segundos
        self.timer = self.create_timer(5.0, self.publish_goal_pose)
        self.get_logger().info('Node initialized and ready to receive messages.')

    def goal_pose_callback(self, msg):
        """Callback que actualiza la pose actual."""
        self.current_goal_pose = msg
        self.get_logger().info(f'Received new goal pose: {msg.pose.position.x}, {msg.pose.position.y}, {msg.pose.position.z}')
        
    def publish_goal_pose(self):
        """Publica la última pose recibida cada 5 segundos."""
        if self.current_goal_pose:
            self.current_goal_pose.header.stamp = self.get_clock().now().to_msg()
            self.publisher.publish(self.current_goal_pose)
            self.get_logger().info('Republished goal pose.')
        else:
            self.get_logger().warn('No goal pose available to publish.')
            
def main(args=None):
    rclpy.init(args=args)
    node = GoalPoseRepublisher()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
