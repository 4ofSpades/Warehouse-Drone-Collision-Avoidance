import cv2.cv2 as cv2
import numpy as np 


class CollisionDetector(object):
    """
        Makes use of a background subtractor to find the contour of the foreground object, which can
        then be used to determine how close an object is.

        [setup]
        - Initialize before running the loop with frames using default values
        - Take the first y frames and put them in an iterable object (eg list).  
        - Set frame_width, frame_height, and safety_area_threshold: A simple solution is to 
        check if the contour takes up 1/X of the total frame area. In the example the formula 
        (frame_width * frame_height) / 10 is used.
        - Train the detector using the aggregated frames
        - The detector can now be used using the check_collision_safety function
    """

    def __init__(self, safety_area_threshold = 0, amount_of_training_data = 25, threshold = 150, debug = False):
        """
            safety_area_threshold: The max pixel area size of the foreground object that is allowed
            before it will be considered a collidable object
            amount_of_training_data: The amount of frames the background subtractor will use to learn the
            difference between the back- and foreground
            threshold: See Opencv documentation on createBackgroundSubtractorKNN at dist2Threshold
            debug: Option to draw and display the image for testing/demo
        """
        self.amount_of_training_data = amount_of_training_data
        self.knn = cv2.createBackgroundSubtractorKNN(history = self.amount_of_training_data, 
            dist2Threshold = threshold, detectShadows = False)
        self.safety_area_threshold = safety_area_threshold
        self.debug = debug
        self.status = "Safe"
        
    def train(self, train_frames):
        self.amount_of_training_data = len(train_frames)
        for frame in train_frames:
            self.knn.apply(frame)

    def check_collision_safety(self, frame):
        """
            Checks whether the contour area of the foreground object is bigger than the threshold.
            Returns True if there is no contour found or it is smaller than the threshold, else
            False.
        """
        fg_mask = self.knn.apply(frame)
        contours = self.get_contours(fg_mask)
        result = None
        if contours is not None:
            if self.debug:
                debug_window = np.copy(frame)*0
                result = self.display_contours(debug_window, contours)
            if cv2.contourArea(contours) > self.safety_area_threshold:
                print("Danger")
                self.status = "Danger"
                return False, result
            else:
                print("Safe")
                self.status = "Safe"
                return True, result
        else:
            print("Safe?")
            self.status = "Safe?"
            return True, result

        

    def display_contours(self, frame, contours):
        """
            Displays the contours on the input frame
        """
        cv2.drawContours(frame, contours, -1, (255,255,255), 2)
        cv2.putText(frame, self.status, (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.imshow("Debug", frame)
        return frame

    def get_contours(self, mask):
        if mask is None:
            pass

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if contours:
            contours = max(contours, key=cv2.contourArea)
        return contours










        



        




