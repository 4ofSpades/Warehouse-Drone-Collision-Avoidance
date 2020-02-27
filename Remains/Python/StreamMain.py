'''
Class for testing the camera stream with the augmenter
'''

import sys
import traceback
import tellopy
import av
from CollisionDetector import CollisionDetector
import cv2.cv2 as cv2 
import numpy as np
import time
import BeamDetector
import DistanceEstimator

#Connect to drone ->  Get camera stream -> Define control channels -> Liftoff -> Position -> Start stabilizer

def main(color_upper_bound, color_lower_bound):
    drone = tellopy.Tello()

    try:
        #Connect to the drone
        drone.connect()
        drone.wait_for_connection(60.0)

        container = None
        retry = 3
        while container is None and 0 < retry:
            retry -= 1
            try:
                container = av.open(drone.get_video_stream())
            except av.AVError as ave:
                print(ave)
                print('retry...')

        #Initialize the augmenter and create an empty array for storing
        aug = BeamDetector.BeamEdgeDetector(color_lower_bound, color_upper_bound)
        dst = DistanceEstimator.DistanceEstimator(20, 75, 1)
        augmented_frames = []

        #Obtain focal length from average
        focal_length = dst.calculate_focal_length(30.0, 75.0, 1.0)
        #Skip the first couple of frames
        frame_skip = 300

        #Setup for calibration
        calibration_frames = 30
        calibration_pixels = []

        coldec = CollisionDetector(debug=True)
        train_data = []
        bg_learning_rate = 25
        while True:
            for frame in container.decode(video=0):
                if 0 < frame_skip:
                    frame_skip = frame_skip - 1
                    continue
                start_time = time.time()

                width = frame.width
                height = frame.height
                frame_time_base = frame.time_base

                image = cv2.cvtColor(np.array(frame.to_image()), cv2.COLOR_RGB2BGR)

                if bg_learning_rate > 0:
                    height, width, _ = image.shape
                    train_data.append(image)
                    bg_learning_rate -= 1
                    continue

                #Set the variables and pretrain
                if coldec.safety_area_threshold == 0:
                    coldec.safety_area_threshold = (height * width) / 10
                    coldec.train(train_data)

                is_safe = coldec.check_collision_safety(image)


                '''
                morph = aug.morph_segmentation(image)
                coordinates = aug.get_hough(morph)
                cv2.imshow("Regular", image)
                if coordinates is not None:
                    lines = aug.estimate_lines(coordinates)
                    line_image = np.copy(image)*0
                    cv2.line(image, (0, int(lines[0])), (int(
                        width), int(lines[0])), (255, 255, 255))
                    cv2.line(image, (0, int(lines[1])), (int(
                        width), int(lines[1])), (255, 255, 255))
                    augmented_frames.append(image)
                    cv2.imshow("Estimation", image)
                    distance = dst.calculate_distance(abs(lines[0] - lines[1]), 1)
                    print("Distance is {} cm".format(distance))
                    dst.distance_from_center(width, height, lines[0], lines[1])
                else:
                    print("Frame augmentation skipped")
                '''
                cv2.waitKey(1)

                if frame_time_base < 1.0/60:
                    time_base = 1.0/60
                else:
                    time_base = frame_time_base
                frame_skip = int((time.time() - start_time)/time_base)
    except Exception as ex:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print(ex)
    finally:
        drone.quit()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    lower_orange = np.array([0, 220, 0])
    upper_orange = np.array([70, 255, 255])
    main(lower_orange, upper_orange)
