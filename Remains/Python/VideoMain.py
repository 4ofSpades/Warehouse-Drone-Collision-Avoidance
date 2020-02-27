import BeamDetector
import DistanceEstimator
import cv2.cv2 as cv2
import numpy as np
import tellopy
import av
import traceback
import time
import sys
from CollisionDetector import CollisionDetector

"""
    Used for testing purposes by replacing a stream with an existing video
"""
def main(file_path: str, lower_bound, upper_bound, is_save_file: bool):
    #Set the input to webcam if file_path is empty
    if not file_path.strip():
        file_path = 0

    detector = BeamDetector.BeamEdgeDetector(lower_bound, upper_bound)
    dst = DistanceEstimator.DistanceEstimator(20, 75, 1)
    cap = cv2.VideoCapture(file_path)
    bg_learning_rate = 50
    augmented_frames = []

    #Collision class
    coldec = CollisionDetector(debug=True)
    train_data = []
    while(cap.isOpened()):
        _, frame = cap.read()

        if frame is None:
            break
        height, width, _ = frame.shape
        
        #Teach the bg subtractor
        if bg_learning_rate > 0:
            height, width, _ = frame.shape
            train_data.append(frame)
            bg_learning_rate -= 1
            continue

        #Set the variables and pretrain
        if coldec.safety_area_threshold == 0:
            coldec.safety_area_threshold = (height * width) / 10
            coldec.train(train_data)
        
        _, result = coldec.check_collision_safety(frame)
        augmented_frames.append(result)
        #frame = frame[200:550, 350:550]
        
        #Beam detection
        '''
        morph = detector.morph_segmentation(frame)
        coordinates = detector.get_hough(morph)
        if coordinates is not None:
            lines = detector.estimate_lines(coordinates)
            line_image = np.copy(frame)*0
            cv2.line(frame, (0, int(lines[0])), (int(
                cap.get(3)), int(lines[0])), (255, 0, 0))
            cv2.line(frame, (0, int(lines[1])), (int(
                cap.get(3)), int(lines[1])), (255, 0, 0))
            distance = dst.calculate_distance(abs(lines[0] - lines[1]), 1)
            #cv2.imshow("Estimated lines", line_image)
            #augmented_frames.append(line_image)
            print("Distance is {} cm".format(distance))
            string_distance = "Distance: {} cm".format(int(distance))
            cv2.putText(frame, string_distance, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,0), 2)
            center = dst.center_of_beam(width, lines[0], lines[1])
            cv2.circle(frame, (int(center[0]), int(center[1])), 1, (0,255,0), 5)
            cv2.arrowedLine(frame, (int(width/2), int(height/2)),
                            (int(center[0]), int(center[1])), (0, 255, 0), 2)
            center_offset  = dst.distance_from_center(cap.get(3), cap.get(4), lines[0], lines[1])
            string_offset = "Center offset: {} pixels".format(int(center_offset))
            cv2.putText(frame, string_offset, (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            augmented_frames.append(frame)

        
        else:
            break
        '''
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if is_save_file and len(augmented_frames) > 0:
        save_file(augmented_frames, width, height)
    cap.release()
    cv2.destroyAllWindows()

def save_file(augmented_frames, width : int, height : int):
    print("Saving file")
    size = (width, height)
    out = cv2.VideoWriter('Output/bg_sub_forklift.mp4', cv2.VideoWriter_fourcc(*"mp4v"), 30, size)
    for output_frame in augmented_frames:
        #output_frame = cv2.cvtColor(output_frame, cv2.COLOR_RGB2BGR)
        out.write(output_frame)
    out.release()

if __name__ == "__main__":
    lower_orange = np.array([0, 220, 0])
    upper_orange = np.array([70, 255, 255])
    file_path = 'Videos/forklift.mp4'
    is_save_file = True
    main(file_path, lower_orange, upper_orange, is_save_file)
