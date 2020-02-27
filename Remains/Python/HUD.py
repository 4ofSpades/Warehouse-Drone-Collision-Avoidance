import cv2.cv2 as cv2
import datetime
import threading
import time
from DroneController import TelloController

def process_frame(raw_frame, tello : TelloController):
        """
            Analyze the frame and return the frame with information (HUD) drawn on it
        """

        frame = raw_frame.copy()
        h, w, _ = frame.shape

        tello.axis_speed = tello.cmd_axis_speed.copy()

        # If we are on the point to take a picture, the tracking is temporarily desactivated (2s)
        if tello.timestamp_take_picture:
            if time.time() - tello.timestamp_take_picture > 2:
                tello.timestamp_take_picture = None
                tello.drone.take_picture()
        else:

            # If we are doing a 360, where are we in our 360 ?
            if tello.yaw_to_consume > 0:
                consumed = tello.yaw - tello.prev_yaw
                tello.prev_yaw = tello.yaw
                if consumed < 0:
                    consumed += 360
                tello.yaw_consumed += consumed
                if tello.yaw_consumed > tello.yaw_to_consume:
                    tello.yaw_to_consume = 0
                    tello.axis_speed["yaw"] = 0
                else:
                    tello.axis_speed["yaw"] = tello.def_speed["yaw"]

        # Write the HUD on the frame
        frame = __write_hud(frame, tello)
        return frame

def __write_hud(frame, tello : TelloController):
        """
            Draw drone info on frame
        """

        class HUD:
            def __init__(self, def_color=(255, 170, 0)):
                self.def_color = def_color
                self.infos = []

            def add(self, info, color=None):
                if color is None:
                    color = self.def_color
                self.infos.append((info, color))

            def draw(self, frame):
                i = 0
                for (info, color) in self.infos:
                    cv2.putText(frame, info, (0, 30 + (i * 30)),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.75, color, 2)  # lineType=30)
                    i += 1

        hud = HUD()

        if tello.debug:
            hud.add(datetime.datetime.now().strftime('%H:%M:%S'))
        hud.add(f"FPS {tello.fps.get():.2f}")
        if tello.debug:
            hud.add(f"VR {tello.video_encoder_rate}")

        hud.add(f"BAT {tello.battery}")
        hud.add(f"YAW {tello.yaw}")
        if tello.is_flying:
            hud.add("FLYING", (0, 255, 0))
        else:
            hud.add("NOT FLYING", (0, 0, 255))
        hud.add(f"TRACKING {'ON' if tello.in_position else 'OFF'}",
                (0, 255, 0) if tello.in_position else (0, 0, 255))
        hud.add(f"EXPO {tello.exposure}")

        if tello.axis_speed['yaw'] > 0:
            hud.add(f"CW {tello.axis_speed['yaw']}", (0, 255, 0))
        elif tello.axis_speed['yaw'] < 0:
            hud.add(f"CCW {-tello.axis_speed['yaw']}", (0, 0, 255))
        else:
            hud.add(f"CW 0")
        if tello.axis_speed['roll'] > 0:
            hud.add(f"RIGHT {tello.axis_speed['roll']}", (0, 255, 0))
        elif tello.axis_speed['roll'] < 0:
            hud.add(f"LEFT {-tello.axis_speed['roll']}", (0, 0, 255))
        else:
            hud.add(f"RIGHT 0")
        if tello.axis_speed['pitch'] > 0:
            hud.add(f"FORWARD {tello.axis_speed['pitch']}", (0, 255, 0))
        elif tello.axis_speed['pitch'] < 0:
            hud.add(f"BACKWARD {-tello.axis_speed['pitch']}", (0, 0, 255))
        else:
            hud.add(f"FORWARD 0")
        if tello.axis_speed['throttle'] > 0:
            hud.add(f"UP {tello.axis_speed['throttle']}", (0, 255, 0))
        elif tello.axis_speed['throttle'] < 0:
            hud.add(f"DOWN {-tello.axis_speed['throttle']}", (0, 0, 255))
        else:
            hud.add(f"UP 0")

        hud.add(f"Target distance: {tello.keep_distance}", (0, 255, 0))
        if tello.in_position:
            hud.add(f"State: {tello.state}")
            if tello.current_distance is not None:
                hud.add(
                    f"Current distance: {round(tello.current_distance, 1)}", (0, 255, 0))
        if tello.timestamp_take_picture:
            hud.add("Taking a picture", (0, 255, 0))

        hud.draw(frame)
        return frame
