import rospy
import math
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32
 
wheel_radius = 0.03
robot_radius = 0.115
#changed to be correct can find these on gazebo


pub = rospy.Publisher("/cmd_vel_mux/input/teleop", Twist, queue_size = 10)


def callback(data):
    print "callback start"
    (v, a) = forward_kinematics(data.data, 0)#veloctiies

    t = Twist()
    t.linear.x = v #linear move forwards for robot calculated once passed into forward kinematics
    t.angular.z = a #turning
    pub.publish(t)

    (w_l, w_r) = inverse_kinematics(1.0, 0.0)
    print "w_l = %f,\tw_r = %f" % (w_l, w_r)
    
    (v, a) = forward_kinematics(w_l, w_r)
    print "v = %f,\ta = %f" % (v, a)

    (w_l, w_r) = inverse_kinematics_from_twist(t)
    print "w_l = %f,\tw_r = %f" % (w_l, w_r)

def listener():
    print "listener start"
    #subscribe to wheel velocity left
    rospy.Subscriber("/wheel_vel_left", Float32, callback)
    print "listener spinning"
    rospy.spin()
    print "listener end"

 # computing the forward kinematics for a differential drive
def forward_kinematics(w_l, w_r):
    c_l = wheel_radius * w_l 
    c_r = wheel_radius * w_r 
    v = (c_l + c_r) / 2 
    a = (c_r - c_l) / robot_radius 
    return (v, a)
 
# computing the inverse kinematics for a differential drive
def inverse_kinematics(v, a):
    c_l = v + (robot_radius * a) /2
    c_r = v - (robot_radius * a) /2
    w_l = c_l / wheel_radius
    w_r = c_r / wheel_radius
    return (w_l, w_r)

# inverse kinematics from a Twist message (This is what a ROS robot has to do)
def inverse_kinematics_from_twist(t):
    return inverse_kinematics(t.linear.x, t.angular.z)

if __name__ == '__main__':
    rospy.init_node('kinematics', anonymous=True)
    listener()
