# -*- coding: utf-8 -*-
"""
@author: Harry Rogers 
@studentID: 15623886
"""
import rospy
import math
import numpy as np
import cv2
from cv2 import namedWindow, imshow, destroyAllWindows, startWindowThread, waitKey
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Image


class Escape:
    
    #Initaliser
    def __init__(self):
        #publisher for twist msg
        self.pubGo = rospy.Publisher('mobile_base/commands/velocity', Twist, queue_size= 10)
        #subscriber for laser
        self.laser_sub = rospy.Subscriber("/scan", LaserScan, self.laser_callback)
        #image subscriber for colours
        self.image_sub = rospy.Subscriber("/camera/rgb/image_raw", Image, self.image_callback)
        #cv bridge needed for image data
        self.bridge = CvBridge()
    
    #Movement function
    def Movement(self, right, left, middle):
        ninety_left = math.radians(1.5707963268) #small turn to keep centered
        #set refresh rate to 5hz
        rospy.Rate(5)
        #rename twist to go
        Go = Twist() 
        #print laser data 
        print(left, middle, right)
        Go.angular.z = math.pi
        self.pubGo.publish(Go)
        #if middle is low wall in front so turn away
        if(middle <=0.5):
            Go.angular.z = math.pi
            #publish twist
            self.pubGo.publish(Go)
        #if left is low wall on left so turn 
        if(left <=0.6):
            Go.angular.z = -math.pi/2
            #publish twist
            self.pubGo.publish(Go)
        #if right is low wall on right so turn away
        if(right <=0.6):
            Go.angular.z = math.pi/2
            #publish twist
            self.pubGo.publish(Go)
        #if middle and right have space drive into it
        if (middle >0.5 and right > 0.5):
            Go.linear.x = 0.2
            #publish twist
            self.pubGo.publish(Go)
        #if middle and left are low spin 
        if(middle > 0.5 and left > 0.5):
            Go.angular.z = math.pi
            #publish twist
            self.pubGo.publish(Go)
        #if right is bigger than left spin 
        if(right > left):
            Go.angular.z = -math.pi/2
            #publish spin
            self.pubGo.publish(Go)
        #if left is bigger then right spin
        if(left> right):
            Go.angular.z = math.pi/2
            #publish spin
            self.pubGo.publish(Go)
        #else they're equal spin other way
        else:
            Go.angular.z = -math.pi/2
            #publish spin
            self.pubGo.publish(Go)
        #if middle and left have lots of space spin into more space slightly and go forward
        if((middle and left) > 1):
            Go.angular.z = ninety_left
            Go.linear.x = 0.2
            #publish twist
            self.pubGo.publish(Go)
        #if middle left and right are all below 0.5 could be facing corner or wall so spin
        if((middle and left and right) < 0.5):
            Go.angular.z = math.pi/2
            #publish twist
            self.pubGo.publish(Go)
       
    #laser callback
    def laser_callback(self, data):
        self.alldata = data.ranges
        #for some reason data seems to be read in backwards so that 0 is on right 
        right = data.ranges[0]
        #middle = length of array/2
        middle = data.ranges[len(self.alldata)/2]
        #left = length of array -1
        left = data.ranges[len(self.alldata)-1]
        #pass movement data
        self.Movement(right, left, middle)
    
    #image callback from workshop 3
    def image_callback(self, data):
        #show what robot sees
        namedWindow("Image")
        #bridge data 
        image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        #hue saturation and intesity
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        #lower red and upper red values 
        lower_red = np.array([0, 50, 50])
        upper_red = np.array([10, 255, 255])
        #mask1 of the range of upper and lower red
        mask1 = cv2.inRange(hsv,lower_red,upper_red)

        #lower and upper values for hsv values hue saturation and intensity
        lower_red = np.array([170, 50, 50])
        upper_red = np.array([180, 255, 255])
        #mask2 of the range of the hsv values set
        mask2 = cv2.inRange(hsv,lower_red,upper_red)

        #combine both masks 
        mask = mask1 + mask2

        lower_green = np.array([45, 50, 50])
        upper_green = np.array([65, 255, 255])
        mask3 = cv2.inRange(hsv, lower_green, upper_green)

        cv2.bitwise_and(image, image, mask = mask3)[380:480,:]
        cv2.imshow("Green Winodw", mask3)

        #create mask window and original window
        cv2.bitwise_and(image, image, mask = mask)[380:480,:]
        cv2.imshow("Red window", mask)

        #publish the mean values of hsv for bgr
        hue = np.mean(hsv[380,480,:])
        Go = Twist()
        if(hue >=130 and hue <145):
            print("trap")
            Go.angular.z = (math.pi)*2
            self.pubGo.publish(Go)
        if(hue >=150):
            print("Exit")
            Go.linear.x = 0.5
            self.pubGo.publish(Go)

        imshow("Image", image)
        waitKey(1)

rospy.init_node('Escape')  
Escape()
rospy.spin()