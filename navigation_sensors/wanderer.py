#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from kobuki_msgs.msg import BumperEvent 

class Scan_msg:

    
    def __init__(self):
        #self.pub = rospy.Publisher('/cmd_vel_mux/input/navi',Twist)
        self.pub = rospy.Publisher('/wanderer_cmd_vel',Twist)
        self.msg = Twist()
        self.sect_1 = 0
        self.sect_2 = 0
        self.sect_3 = 0
        self.ang = {0:0,001:-1.2,10:-1.2,11:-1.2,100:1.5,101:1.0,110:1.0,111:1.2}
        self.fwd = {0:.25,1:0,10:0,11:0,100:0.1,101:0,110:0,111:0}
        self.dbgmsg = {0:'Move forward',1:'Veer right',10:'Veer right',11:'Veer right',100:'Veer left',101:'Veer left',110:'Veer left',111:'Veer right'}
        self.laser_cnt = 0

        rospy.Subscriber('/mobile_base/events/bumper', BumperEvent, self.bumper_callback)

        self.bumper = False

    def bumper_callback(self, msg):
        if self.bumper == True:
            return
	if msg.state == 0:
            return 
        self.bumper = True
        msg = Twist()
        msg.linear.x = -0.15
        msg.angular.z = 0 

        for i in range(3):
            print 'BUMPER'
            rospy.sleep(0.5)
            self.pub.publish(msg)
	msg = Twist()
	msg.angular.z = 1.2 
	rospy.sleep(0.5)
        self.pub.publish(msg)
        self.bumper = False

    def reset_sect(self):
        self.sect_1 = 0
        self.sect_2 = 0
        self.sect_3 = 0

    def sort(self, laserscan):
        entries = len(laserscan.ranges)
        for entry in range(0,entries):
            if 0.4 < laserscan.ranges[entry] < 0.75:
                self.sect_1 = 1 if (0 < entry < entries/3) else 0 
                self.sect_2 = 1 if (entries/3 < entry < entries/2) else 0
                self.sect_3 = 1 if (entries/2 < entry < entries) else 0
        rospy.loginfo("sort complete,sect_1: " + str(self.sect_1) + " sect_2: " + str(self.sect_2) + " sect_3: " + str(self.sect_3))

    def movement(self, sect1, sect2, sect3):
        sect = int(str(self.sect_1) + str(self.sect_2) + str(self.sect_3))
        rospy.loginfo("Sect = " + str(sect)) 

        if self.fwd[sect] != 0 or self.ang[sect] != 0:
            self.msg.angular.z = self.ang[sect]
            self.msg.linear.x = self.fwd[sect]
            rospy.loginfo(self.dbgmsg[sect])
            self.pub.publish(self.msg)
        self.reset_sect()
 
    def for_callback(self,laserscan):
        self.laser_cnt = (self.laser_cnt + 1) % 25
        if self.bumper == True:
            return
        if self.laser_cnt != 0:
            return
        self.sort(laserscan)
        self.movement(self.sect_1, self.sect_2, self.sect_3)

def call_back(scanmsg):
    sub_obj.for_callback(scanmsg)

def listener():
    rospy.init_node('navigation_sensors')
    rospy.loginfo("Subscriber Starting")
    sub = rospy.Subscriber('/scan', LaserScan, call_back)
    rospy.spin()

if __name__ == "__main__":
    '''A Scan_msg class object called sub_obj is created and listener
    function is run''' 
    sub_obj = Scan_msg()
    listener()
