'''
Controls the drone using commands. The key bindings are found in the ~DroneController.TelloController.init_controls function.

- The int value for commands equal the amount of centimeters it should move
'''
import os
import datetime
from FPS import FPS
from simple_pid import PID
import logging
import tellopy
import time
import av
from pynput import keyboard
import cv2.cv2 as cv2
import sys
import DistanceEstimator
from math import atan2, pi, isnan
from BeamDetector import BeamEdgeDetector
from CollisionDetector import CollisionDetector

class TelloController(object):
    """
    TelloController builds keyboard controls on top of TelloPy as well
    as generating images from the video stream and enabling opencv support
    """
    def __init__(self, object_tracker_distance = 20,
                object_tracker_height = 1,
                object_tracker_pixels = 75,
                 kbd_layout="QWERTY",
                 write_log_data=False,
                 media_directory="media",
                 child_cnx=None,
                 log_level=None):

        self.log = logging.getLogger("Warehouse Tello")
        self.log_level = log_level
        self.debug = log_level is not None
        self.kbd_layout = kbd_layout
        # Flight data
        self.is_flying = False
        self.battery = None
        self.fly_mode = None
        self.throw_fly_timer = 0

        self.keydown = False
        self.date_fmt = '%Y-%m-%d_%H%M%S'
        self.drone = tellopy.Tello()
        self.axis_command = {
            "yaw": self.drone.clockwise,
            "roll": self.drone.right,
            "pitch": self.drone.forward,
            "throttle": self.drone.up
        }
        self.axis_speed = {"yaw": 0, "roll": 0, "pitch": 0, "throttle": 0}
        self.cmd_axis_speed = {"yaw": 0, "roll": 0, "pitch": 0, "throttle": 0}
        self.prev_axis_speed = self.axis_speed.copy()
        self.def_speed = {"yaw": 50, "roll": 30, "pitch": 30, "throttle": 40}

        #Setup for CA here
        self.object_tracker_pixels = object_tracker_pixels
        self.object_tracker_distance = object_tracker_distance
        self.object_tracker_height = object_tracker_height
        self.distance_estimator = DistanceEstimator.DistanceEstimator(object_tracker_distance, 
            object_tracker_pixels, object_tracker_height)

        self.beam_detector = BeamEdgeDetector([0, 220, 0], [70, 255, 255])

        self.train_data = []
        self.collision_detector = CollisionDetector()

        self.state = None

        #Drone center
        self.center_width = 0
        self.center_height = 0 

        self.current_distance = 0
        self.beam_center = 0

        self.in_position = False
        self.starting_yaw = 0
        self.z_offset = 0
        self.y_offset = 0

        #PID controllers for providing speed commands
        self.pid_pitch = PID(0.5, 0, 0, setpoint=0,
                             output_limits=(-20, 20))
        self.pid_throttle = PID(
            0.5, 0, 0, setpoint=0, output_limits=(-10, 10))

        self.write_log_data = write_log_data
        self.reset()
        self.media_directory = media_directory
        if not os.path.isdir(self.media_directory):
            os.makedirs(self.media_directory)

        if self.write_log_data:
            path = 'tello-%s.csv' % datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
            self.log_file = open(path, 'w')
            self.write_header = True

        self.init_drone()
        self.init_controls()

        # container for processing the packets into frames
        self.container = av.open(self.drone.get_video_stream())
        self.vid_stream = self.container.streams.video[0]
        self.out_file = None
        self.out_stream = None
        self.out_name = None
        self.start_time = time.time()

        self.fps = FPS()

        self.exposure = 0

        # Logging
        self.log_level = log_level
        if log_level is not None:
            if log_level == "info":
                log_level = logging.INFO
            elif log_level == "debug":
                log_level = logging.DEBUG
            self.log.setLevel(log_level)
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(log_level)
            ch.setFormatter(logging.Formatter(fmt='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
                                              datefmt="%H:%M:%S"))
            self.log.addHandler(ch)

    def set_video_encoder_rate(self, rate):
        self.drone.set_video_encoder_rate(rate)
        self.video_encoder_rate = rate

    def reset(self):
        """
            Reset global variables before a fly
        """
        self.log.debug("RESET")
        self.ref_pos_x = -1
        self.ref_pos_y = -1
        self.ref_pos_z = -1
        self.pos_x = -1
        self.pos_y = -1
        self.keep_distance = 30
        self.pos_z = -1
        self.yaw = 0
        self.tracking = False
        self.yaw_to_consume = 0
        self.timestamp_keep_distance = time.time()
        self.timestamp_take_picture = None
        self.state = None

        #Drone center
        self.center_width = 0
        self.center_height = 0 

        self.current_distance = 0
        self.beam_center = 0

        self.in_position = False
        self.z_offset = 0
        self.y_offset = 0

        self.train_data = []
        

    def init_drone(self):
        """
            Connect to the drone, start streaming and subscribe to events
        """
        if self.log_level:
            self.drone.log.set_level(2)
        self.drone.connect()
        self.drone.wait_for_connection(60.0)
        self.set_video_encoder_rate(2)
        self.drone.start_video()

        self.drone.subscribe(self.drone.EVENT_FLIGHT_DATA,
                             self.flight_data_handler)
        #self.drone.subscribe(self.drone.EVENT_LOG, self.log_data_handler)
        self.drone.subscribe(self.drone.EVENT_LOG_DATA,
                             self.log_data_handler)

    def on_press(self, keyname):
        """
            Handler for keyboard listener
        """
        if self.keydown:
            return
        try:
            self.keydown = True
            keyname = str(keyname).strip('\'')
            self.log.info('KEY PRESS ' + keyname)
            if keyname == 'Key.esc':
                self.drone.land()
                time.sleep(2)
                self.drone.quit()
                cv2.destroyAllWindows()
                os._exit(0)
            if keyname in self.controls_keypress:
                self.controls_keypress[keyname]()
        except AttributeError:
            self.log.debug(f'special key {keyname} pressed')

    def on_release(self, keyname):
        """
            Reset on key up from keyboard listener
        """
        self.keydown = False
        keyname = str(keyname).strip('\'')
        self.log.info('KEY RELEASE ' + keyname)
        if keyname in self.controls_keyrelease:
            key_handler = self.controls_keyrelease[keyname]()

    def set_speed(self, axis, speed):
        self.log.info(f"set speed {axis} {speed}")
        self.cmd_axis_speed[axis] = speed

    def lock_on(self, frame):
        coordinates = self.beam_detector.get_hough(
            self.beam_detector.morph_segmentation(frame))
        if coordinates is not None:
            lines = self.beam_detector.estimate_lines(coordinates)
            for line in lines:
                cv2.line(frame, (0, int(line)),
                            (self.center_width*2, int(line)), (255, 0, 0), 2)

            self.beam_center = int(self.distance_estimator.center_of_beam(self.center_width,
                lines[0], lines[1])[1])
            self.current_distance = self.distance_estimator.calculate_distance(
                abs(lines[0] - lines[1]), 1)

            self.z_offset = self.current_distance - self.object_tracker_distance
            self.y_offset = self.center_height - self.beam_center
            if isnan(self.z_offset) | isnan(self.y_offset):
                print("NaN value detected, disabling distancing mode")
                self.in_position = False
                return
            self.__center_beam()
            self.__maintain_distance()

            cv2.arrowedLine(frame, (self.center_width, self.center_height),
                (self.center_width, self.beam_center),(0, 0, 0), 3, cv2.LINE_AA)
            #cv2.imshow("Debug", frame)


    def __center_beam(self):
        """Adjusts altitude based on offset
        
        Arguments:
            y_offset {int} -- How many cm the drone is off the center of the beam
        """
        #TODO: use image with known altitude diff to recalc focal length
        #This is necessary for converting pixels to cm
        if self.y_offset > 20:
            self.y_offset = 20
        elif self.y_offset < -20:
            self.y_offset = -20
        if self.y_offset > 10 or self.y_offset < -10:
            self.set_speed('throttle', self.y_offset *0.5)
        '''
        if self.y_offset > 0:
            self.drone.up(int(self.y_offset*0.5))
        else:
            self.drone.down(abs(int(self.y_offset*0.5)))
        '''

    def __maintain_distance(self):
        """Adjusts pitch based on offset
        
        Arguments:
            z_offset {int} -- Amount of cm the drone is off the desired distance
        """
        if self.z_offset > 10: 
            self.z_offset = 10
        elif self.z_offset < -10:
            self.z_offset = -10
        if self.z_offset > 5 or self.z_offset < -5:
            self.set_speed('pitch', self.z_offset * 0.5)
        '''
        if self.z_offset > 0:
            self.drone.forward(int(self.z_offset*0.5))
        else:
            self.drone.backward(abs(int(self.z_offset*0.5)))
        '''

    def train_background_subtractor(self):
        """
            Trains the background detector to distinguish between back- and foreground using a
            training set
        """
        self.collision_detector.train(self.train_data)
    
    def detect_collision(self, frame):
        return self.collision_detector.check_collision_safety(frame)

    def avoid_collision(self):
        #TODO: Check if avoidable else land
        self.drone.land()
        print("Collision unavoidable!")
        self.drone.quit()

        
    def init_controls(self):
        """
            Define keys and add listener
        """

        controls_keypress_QWERTY = {
            'w': lambda: self.set_speed("pitch", self.def_speed["pitch"]),
            's': lambda: self.set_speed("pitch", -self.def_speed["pitch"]),
            'a': lambda: self.set_speed("roll", -self.def_speed["roll"]),
            'd': lambda: self.set_speed("roll", self.def_speed["roll"]),
            'q': lambda: self.set_speed("yaw", -self.def_speed["yaw"]),
            'e': lambda: self.set_speed("yaw", self.def_speed["yaw"]),
            'i': lambda: self.drone.flip_forward(),
            'k': lambda: self.drone.flip_back(),
            'j': lambda: self.drone.flip_left(),
            'l': lambda: self.drone.flip_right(),
            'Key.left': lambda: self.set_speed("yaw", -1.5*self.def_speed["yaw"]),
            'Key.right': lambda: self.set_speed("yaw", 1.5*self.def_speed["yaw"]),
            'Key.up': lambda: self.set_speed("throttle", self.def_speed["throttle"]),
            'Key.down': lambda: self.set_speed("throttle", -self.def_speed["throttle"]),
            'Key.tab': lambda: self.drone.takeoff(),
            'Key.backspace': lambda: self.drone.land(),
            'Key.enter': lambda: self.take_picture(),
            'c': lambda: self.clockwise_degrees(360),
            '0': lambda: self.drone.set_video_encoder_rate(0),
            '1': lambda: self.drone.set_video_encoder_rate(1),
            '2': lambda: self.drone.set_video_encoder_rate(2),
            '3': lambda: self.drone.set_video_encoder_rate(3),
            '4': lambda: self.drone.set_video_encoder_rate(4),
            '5': lambda: self.drone.set_video_encoder_rate(5),

            '7': lambda: self.set_exposure(-1),
            '8': lambda: self.set_exposure(0),
            '9': lambda: self.set_exposure(1)
        }

        controls_keyrelease_QWERTY = {
            'w': lambda: self.set_speed("pitch", 0),
            's': lambda: self.set_speed("pitch", 0),
            'a': lambda: self.set_speed("roll", 0),
            'd': lambda: self.set_speed("roll", 0),
            'q': lambda: self.set_speed("yaw", 0),
            'e': lambda: self.set_speed("yaw", 0),
            'Key.left': lambda: self.set_speed("yaw", 0),
            'Key.right': lambda: self.set_speed("yaw", 0),
            'Key.up': lambda: self.set_speed("throttle", 0),
            'Key.down': lambda: self.set_speed("throttle", 0)
        }

        controls_keypress_AZERTY = {
            'z': lambda: self.set_speed("pitch", self.def_speed["pitch"]),
            's': lambda: self.set_speed("pitch", -self.def_speed["pitch"]),
            'q': lambda: self.set_speed("roll", -self.def_speed["roll"]),
            'd': lambda: self.set_speed("roll", self.def_speed["roll"]),
            'a': lambda: self.set_speed("yaw", -self.def_speed["yaw"]),
            'e': lambda: self.set_speed("yaw", self.def_speed["yaw"]),
            'i': lambda: self.drone.flip_forward(),
            'k': lambda: self.drone.flip_back(),
            'j': lambda: self.drone.flip_left(),
            'l': lambda: self.drone.flip_right(),
            'Key.left': lambda: self.set_speed("yaw", -1.5*self.def_speed["yaw"]),
            'Key.right': lambda: self.set_speed("yaw", 1.5*self.def_speed["yaw"]),
            'Key.up': lambda: self.set_speed("throttle", self.def_speed["throttle"]),
            'Key.down': lambda: self.set_speed("throttle", -self.def_speed["throttle"]),
            'Key.tab': lambda: self.drone.takeoff(),
            'Key.backspace': lambda: self.drone.land(),
            'Key.enter': lambda: self.take_picture(),
            'c': lambda: self.clockwise_degrees(360),
            '0': lambda: self.drone.set_video_encoder_rate(0),
            '1': lambda: self.drone.set_video_encoder_rate(1),
            '2': lambda: self.drone.set_video_encoder_rate(2),
            '3': lambda: self.drone.set_video_encoder_rate(3),
            '4': lambda: self.drone.set_video_encoder_rate(4),
            '5': lambda: self.drone.set_video_encoder_rate(5),

            '7': lambda: self.set_exposure(-1),
            '8': lambda: self.set_exposure(0),
            '9': lambda: self.set_exposure(1)
        }

        controls_keyrelease_AZERTY = {
            'z': lambda: self.set_speed("pitch", 0),
            's': lambda: self.set_speed("pitch", 0),
            'q': lambda: self.set_speed("roll", 0),
            'd': lambda: self.set_speed("roll", 0),
            'a': lambda: self.set_speed("yaw", 0),
            'e': lambda: self.set_speed("yaw", 0),
            'Key.left': lambda: self.set_speed("yaw", 0),
            'Key.right': lambda: self.set_speed("yaw", 0),
            'Key.up': lambda: self.set_speed("throttle", 0),
            'Key.down': lambda: self.set_speed("throttle", 0)
        }

        if self.kbd_layout == "AZERTY":
            self.controls_keypress = controls_keypress_AZERTY
            self.controls_keyrelease = controls_keyrelease_AZERTY
        else:
            self.controls_keypress = controls_keypress_QWERTY
            self.controls_keyrelease = controls_keyrelease_QWERTY
        self.key_listener = keyboard.Listener(on_press=self.on_press,
                                              on_release=self.on_release)
        self.key_listener.start()

    def quat_to_yaw_deg(self, qx, qy, qz, qw):
        """
            Calculate yaw from quaternion
        """
        degree = pi/180
        sqy = qy*qy
        sqz = qz*qz
        siny = 2 * (qw*qz+qx*qy)
        cosy = 1 - 2*(qy*qy+qz*qz)
        yaw = int(atan2(siny, cosy)/degree)
        return yaw
    
    def take_picture(self):
        """
            Tell drone to take picture, image sent to file handler
        """
        self.drone.take_picture()

    def toggle_in_position(self):
        self.in_position = not self.in_position
        self.starting_yaw = self.yaw
        #cv2.destroyAllWindows()


    def set_exposure(self, expo):
        """
            Change exposure of drone camera
        """
        if expo == 0:
            self.exposure = 0
        elif expo == 1:
            self.exposure = min(9, self.exposure+1)
        elif expo == -1:
            self.exposure = max(-9, self.exposure-1)
        self.drone.set_exposure(self.exposure)
        self.log.info(f"EXPOSURE {self.exposure}")

    def clockwise_degrees(self, degrees):
        self.yaw_to_consume = degrees
        self.yaw_consumed = 0
        self.prev_yaw = self.yaw

    def flight_data_handler(self, event, sender, data):
        """
            Listener to flight data from the drone.
        """
        self.battery = data.battery_percentage
        self.fly_mode = data.fly_mode
        self.throw_fly_timer = data.throw_fly_timer
        self.throw_ongoing = data.throw_fly_timer > 0

        # print("fly_mode",data.fly_mode)
        # print("throw_fly_timer",data.throw_fly_timer)
        # print("em_ground",data.em_ground)
        # print("em_sky",data.em_sky)
        # print("electrical_machinery_state",data.electrical_machinery_state)
        #print("em_sky",data.em_sky,"em_ground",data.em_ground,"em_open",data.em_open)
        #print("height",data.height,"imu_state",data.imu_state,"down_visual_state",data.down_visual_state)
        if self.is_flying != data.em_sky:
            self.is_flying = data.em_sky
            self.log.debug(f"FLYING : {self.is_flying}")
            if not self.is_flying:
                self.reset()

        self.log.debug(
            f"MODE: {self.fly_mode} - Throw fly timer: {self.throw_fly_timer}")

    def log_data_handler(self, event, sender, data):
        """
            Listener to log data from the drone.
        """
        '''
        pos_x = -data.mvo.pos_x
        pos_y = -data.mvo.pos_y
        pos_z = -data.mvo.pos_z
        if abs(pos_x)+abs(pos_y)+abs(pos_z) > 0.07:
            if self.ref_pos_x == -1:  # First time we have meaningful values, we store them as reference
                self.ref_pos_x = pos_x
                self.ref_pos_y = pos_y
                self.ref_pos_z = pos_z
            else:
                self.pos_x = pos_x - self.ref_pos_x
                self.pos_y = pos_y - self.ref_pos_y
                self.pos_z = pos_z - self.ref_pos_z
        '''

        qx = data.imu.q1
        qy = data.imu.q2
        qz = data.imu.q3
        qw = data.imu.q0
        self.yaw = self.quat_to_yaw_deg(qx, qy, qz, qw)

        if self.write_log_data:
            if self.write_header:
                self.log_file.write('%s\n' % data.format_cvs_header())
                self.write_header = False
            self.log_file.write('%s\n' % data.format_cvs())

    def handle_flight_received(self, event, sender, data):
        """
            Create a file in local directory to receive image from the drone
        """
        path = f'{self.media_directory}/tello-{datetime.datetime.now().strftime(self.date_fmt)}.jpg'
        with open(path, 'wb') as out_file:
            out_file.write(data)
        self.log.info('Saved photo to %s' % path)
