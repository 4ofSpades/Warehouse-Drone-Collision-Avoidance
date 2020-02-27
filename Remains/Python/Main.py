from DroneController import TelloController
from HUD import process_frame
from StateMachineActions import StateMachineActions

from math import isnan
import time
from multiprocessing import Process

import cv2.cv2 as cv2
import numpy as np

def main():
    global tello
    tello = TelloController()
    drone = StateMachineActions(tello, roll_speed=40, roll_distance=15, 
        yaw_speed=25, yaw_distance=90)
    last_state = drone.sm.state

    first_frame = True
    frame = None

    train_data_size = 25


    #Start video stream
    frame_skip = 300
    for frame in drone.tello.container.decode(video=0):
        if 0 < frame_skip:
            frame_skip = frame_skip - 1
            continue
        start_time = time.time()
        if frame.time_base < 1.0/60:
            time_base = 1.0/60
        else:
            time_base = frame.time_base

        #Get metadata from first frame
        if first_frame:
            width = frame.width
            height = frame.height
            drone.tello.center_width = int(width / 2)
            drone.tello.center_height = int(height / 2)
            drone.tello.collision_detector.safety_area_threshold = (width * height) / 10
            first_frame = False

        #Convert to Opencv
        frame = cv2.cvtColor(
            np.array(frame.to_image(), dtype=np.uint8), cv2.COLOR_RGB2BGR)

        #Gather train data
        if train_data_size > 0:
            drone.tello.train_data.append(frame)
            train_data_size -= 1
            continue

        hud_frame = process_frame(frame, drone.tello)
        cv2.circle(hud_frame, (drone.tello.center_width,
            drone.tello.center_height), 10, (255, 150, 0))

        action_interval = 0.05
        if drone.tello.in_position:
            if time.time() - drone.tello.timestamp_keep_distance > action_interval:
                if last_state != drone.sm.state:
                    #cv2.destroyWindow("Debug")
                    last_state = drone.sm.state
                drone.frame = frame
                drone.tello.state = drone.sm.state
                drone.execute()
                drone.tello.timestamp_keep_distance = time.time()
        '''
        if drone.tello.in_position:

            coordinates = drone.tello.augmenter.get_hough(  
                drone.tello.augmenter.morph_segmentation(altitude_frame))
            if coordinates is not None:
                lines = drone.tello.augmenter.estimate_lines(coordinates)
                for line in lines:
                    cv2.line(altitude_frame, (0, int(line)),
                             (width, int(line)), (255, 0, 0), 2)

                #Draw arrowline between center beam and center frame
                beam_center = drone.tello.distance_estimator.center_of_beam(width,
                                                                    lines[0], lines[1])
                cv2.arrowedLine(centering_frame, (int(width/2), int(height/2)),
                                (int(width/2), int(beam_center[1])),
                                (0, 0, 255), 3, cv2.LINE_AA)
            
                #Combine and display the output in a single frame.
                #output = cv2.bitwise_or(centering_frame, altitude_frame)
                #output = cv2.bitwise_or(output, hud_frame)
                #cv2.imshow("Output", output)

                reposition_interval = 0.25
                if time.time() - drone.tello.timestamp_keep_distance > reposition_interval:
                    #Adjust throttle and pitch every x seconds
                    #Input is the error value: desired value - current value
                    drone.tello.current_distance = drone.tello.distance_estimator.calculate_distance(
                        abs(lines[0] - lines[1]), 1)

                    #Calculate how far the drone is off the mark
                    pitch_offset = drone.tello.current_distance - drone.tello.object_tracker_distance
                    throttle_offset = beam_center[1] - (height/2)
                    drone.tello.z_offset = pitch_offset
                    drone.tello.y_offset = throttle_offset

                    print("Pitch offset: {} | throttle offset: {}".format(
                        pitch_offset, throttle_offset))
                    #Stop the beam following if no line is detected
                    if isnan(pitch_offset) | isnan(throttle_offset):
                        print("NaN value detected, disabling distancing mode")
                        drone.tello.in_position = False
                    else:
                        #Ignore small offsets TODO: make use of derivative controller instead?
                        if abs(pitch_offset) > 1:
                            drone.tello.axis_speed["pitch"] = int(drone.tello.pid_pitch(
                                pitch_offset))
                        if abs(throttle_offset) > 3:
                            drone.tello.axis_speed["throttle"] = int(drone.tello.pid_throttle(
                                throttle_offset))

                        drone.tello.timestamp_keep_distance = time.time()
        """
        if drone.tello.yaw_to_consume > 0:
            consumed = drone.tello.yaw - drone.tello.prev_yaw
            drone.tello.prev_yaw = drone.tello.yaw
            if consumed < 0:
                consumed += 360
            drone.tello.yaw_consumed += consumed
            if drone.tello.yaw_consumed > drone.tello.yaw_to_consume:
                drone.tello.yaw_to_consume = 0
                drone.tello.axis_speed["yaw"] = 0
            else:
                drone.tello.axis_speed["yaw"] = drone.tello.def_speed["yaw"]
        """
        '''
        # Send axis commands to the drone
        for axis, command in drone.tello.axis_command.items():
            if drone.tello.axis_speed[axis]is not None and drone.tello.axis_speed[axis] != drone.tello.prev_axis_speed[axis]:
                drone.tello.log.debug(f"COMMAND {axis} : {drone.tello.axis_speed[axis]}")
                command(drone.tello.axis_speed[axis])
                drone.tello.prev_axis_speed[axis] = drone.tello.axis_speed[axis]
            else:
                # This line is necessary to display current values in 'self.write_hud'
                drone.tello.axis_speed[axis] = drone.tello.prev_axis_speed[axis]
        
        #Update window stats
        drone.tello.fps.update()

        cv2.imshow("HUD", hud_frame)

        if cv2.waitKey(1) & 0xFF == ord('m'):
            print("Toggled in position")
            drone.tello.toggle_in_position()

        frame_skip = int((time.time() - start_time)/time_base)


if __name__ == "__main__":
    main()
