import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point
from math import cos, sin, atan2


class PlanVisualizer(Node):
    def __init__(self):
        super().__init__('plan_visualizer')

        self.plan_sub = self.create_subscription(Path, '/plan', self.plan_callback, 10)

        self.marker_pub = self.create_publisher(MarkerArray, '/visualization_footprints', 10)

        self.footprint_points = [
            {'x': -1.22, 'y':  0.22}, {'x': -0.24, 'y':  0.22},
            {'x': -0.24, 'y':  0.27}, {'x':  0.24, 'y':  0.27},
            {'x':  0.24, 'y': -0.27}, {'x': -0.24, 'y': -0.27},
            {'x': -0.24, 'y': -0.22}, {'x': -1.22, 'y': -0.22}
        ]

        self.previous_marker_count = 0

    def plan_callback(self, msg):
        marker_array = MarkerArray()

        for i in range(self.previous_marker_count):
            marker = Marker()
            marker.header = msg.header
            marker.ns = "footprint_markers"
            marker.id = i
            marker.action = Marker.DELETE
            marker_array.markers.append(marker)

        for i, pose_stamped in enumerate(msg.poses):
            pose = pose_stamped.pose

            orientation_q = pose.orientation
            yaw = self.quaternion_to_yaw(orientation_q)

            # Transformar el footprint según la posición y orientación del punto del plan
            transformed_points = self.transform_footprint(pose.position.x, pose.position.y, yaw)

            # Crear un marcador para el footprint transformado
            marker = Marker()
            marker.header = msg.header
            marker.ns = "footprint_markers"
            marker.id = i
            marker.type = Marker.LINE_STRIP
            marker.action = Marker.ADD
            marker.scale.x = 0.05  # Grosor de la línea
            marker.color.r = 0.0
            marker.color.g = 0.5
            marker.color.b = 1.0
            marker.color.a = 0.8

            # Añadir los puntos transformados al marcador
            marker.points = transformed_points

            # Cerrar el polígono del footprint
            marker.points.append(transformed_points[0])

            marker_array.markers.append(marker)

        # Actualizar la cuenta de marcadores
        self.previous_marker_count = len(msg.poses)

        # Publicar los marcadores
        self.marker_pub.publish(marker_array)
        self.get_logger().info(f"Visualización actualizada con {len(msg.poses)} footprints.")

    def transform_footprint(self, x, y, yaw):
        """Transforma el footprint según la posición y orientación (yaw)."""
        transformed_points = []
        for point in self.footprint_points:
            # Rotación
            new_x = point['x'] * cos(yaw) - point['y'] * sin(yaw)
            new_y = point['x'] * sin(yaw) + point['y'] * cos(yaw)

            # Traslación
            new_x += x
            new_y += y

            transformed_points.append(Point(x=new_x, y=new_y, z=0.0))

        return transformed_points

    def quaternion_to_yaw(self, q):
        """Convierte un quaternion en un ángulo yaw."""
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        return atan2(siny_cosp, cosy_cosp)


def main(args=None):
    rclpy.init(args=args)
    node = PlanVisualizer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
