import rospy
import cv2
from cv2 import namedWindow, cvtColor, imshow
from cv2 import destroyAllWindows, startWindowThread
from cv2 import COLOR_BGR2GRAY, COLOR_BGR2HSV, waitKey
from cv2 import blur, Canny
import cv2
from numpy import mean
import numpy as np
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge


class image_class:

    def __init__(self):

        self.bridge = CvBridge()
        self.img_sub = rospy.Subscriber("/camera/rgb/image_raw", Image, self.cb)

        self.p = rospy.Publisher("/result_topic", String)
    
    def cb(self, data):
        namedWindow("Image")
        namedWindow("Filtered")

        image = self.bridge.imgmsg_to_cv2(data, "bgr8")

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

        #create mask window and original window
        cv2.bitwise_and(image, image, mask = mask)
        cv2.imshow("Image window", mask)
        cv2.imshow("Original", image)

        #publish the mean values of hsv for bgr
        blue = np.mean(hsv[:,:,0])
        green = np.mean(hsv[:,:,1])
        red = np.mean(hsv[:,:,2])

        #output values and publish
        finalout = str((blue,green,red))
        self.p.publish(finalout)

        
        imshow("Image", image)
        imshow("Filtered", mask)
        waitKey(1)
        
image_class()
rospy.init_node("image_class", anonymous= True)
rospy.spin()
cv2.destroyAllWindows()