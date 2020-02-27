import numpy as np
import cv2.cv2 as cv2
import numpy as np
import statistics


# Constants for color bounds
#HSV_LOWER_GREEN = np.array([30,0,0])
#HSV_UPPER_GREEN = np.array([60,255,255])

class BeamEdgeDetector:
    """
        Provides functionality for detecting the beam edges
    """

    def __init__(self, color_lower_bound, color_upper_bound):
        self.lower_bound = color_lower_bound
        self.upper_bound = color_upper_bound

    def morph_segmentation(self, frame):
        grey = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        gaussian = cv2.GaussianBlur(grey, (5,5), 0)
        _, binary = cv2.threshold(gaussian, 0, 255, cv2.THRESH_OTSU)
        binary = cv2.bitwise_not(cv2.morphologyEx(
            binary, cv2.MORPH_CLOSE, None, iterations=5))
        return binary


    def segment_hsv(self, frame, color_lower_bound, color_upper_bound):
        clean = cv2.bilateralFilter(frame, 5, 255, 255)
        color = cv2.cvtColor(clean, cv2.COLOR_BGR2HSV)
        kernel = np.ones((25, 25), np.uint8)
        erosion = cv2.erode(color, kernel, iterations=1)

        mask = cv2.inRange(erosion, color_lower_bound, color_upper_bound)
        applied_mask = cv2.bitwise_and(frame, frame, mask=mask)

        return applied_mask


    def get_hough(self, frame):
        """Performs Canny, MORPH_CLOSE, and HoughLinesP on the input frame

        Arguments:
            frame {[type]} -- a video frame or image

        Returns:
            [array] -- An array containing all the start and end coordinates of all hough lines
        """

        canny = cv2.Canny(frame, 500, 800)
        kernel = np.ones((5, 5), np.uint8)
        closing = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel, iterations=5)

        # Get all line coordinates in 'voting' order
        lines = cv2.HoughLinesP(closing, 1, np.pi/180, 125,
                                minLineLength=1, maxLineGap=100)
        coordinates = None
        empty = np.copy(frame)*0
        # If no lines are present
        if lines is None:
            lines = np.array([])
        for x in range(0, len(lines)):
            for x1, y1, x2, y2 in lines[x]:
                # Get all start-end coordinates of the lines
                start = [x1, y1]
                end = [x2, y2]
                if coordinates is None:
                    coordinates = np.array([start])
                else:
                    coordinates = np.append(coordinates, [start], axis=0)

                cv2.line(empty, (x1, y1), (x2, y2), [255, 255, 255])

                coordinates = np.append(coordinates, [end], axis=0)
        return coordinates


    def estimate_lines(self, coordinates: list):
        """Creates 2 lines by splitting and grouping all coordinates by a pivot and finding the average.
        The lines are ordered ascendingly

        Arguments:
            coordinates {list} -- The begin and end coordinates of all Hough-lines

        Returns:
            [array] -- An array containing the average Y coordinate estimate of the upper part and lower part, respectively
        """
        # Get the mean Y coordinate
        pivot = statistics.mean(coordinates[:][:, 1])

        upper_line = None
        lower_line = None
        # Sort all points according to the pivot
        for value in coordinates[:][:, 1]:
            if value < pivot:
                if upper_line is None:
                    upper_line = np.array([value])
                else:
                    upper_line = np.append(upper_line, [value], axis=0)
            elif value > pivot:
                if lower_line is None:
                    lower_line = np.array([value])
                else:
                    lower_line = np.append(lower_line, [value], axis=0)

        # Find the averages of the lower and upper parts
        result = np.empty(2)

        # What if only 1 line of the beam gets detected? eg [159 159]🤔🤔🤔
        # What if no beam get detected🤔🤔🤔
        if upper_line is not None and lower_line is not None:
            result[0] = round(statistics.mean(upper_line))
            result[1] = round(statistics.mean(lower_line))
        return result


    def draw_line(self, frame, x1, y1, x2, y2, color):
        """Draws one line onto a frame.

        Arguments:
            frame {np array} -- The frame on which the lines are drawn on.
            lines {list} -- A list with each entry containing a x and y coordinate.
        """
        cv2.line(frame, (x1, y1), (x2, y2), color)
        # augmented_frames.append(line_image)
        return frame
