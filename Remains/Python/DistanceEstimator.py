import cv2.cv2 as cv2

class DistanceEstimator:
    '''
    DistanceEstimator calculates the real distance from the amount of pixels by using an example frame at a
    known distance to find a ratio, which can then be used to recalculate the distance.
    '''

    def __init__(self, distance_from_beam, pixels, height_beam):
        self.distance_from_beam = distance_from_beam
        self.pixels = pixels
        self.height_beam = height_beam
        self.focal_length = self.calculate_focal_length(distance_from_beam, pixels, height_beam)

    def calculate_focal_length(self, distance: float, pixels: int, height: float):
        """Calculates the focal length by using a frame at a known distance
        
        Arguments:
            distance {float} -- The distance between the camera and the beam
            pixels {int} -- The amount of pixels in between the edges of the beam
            height {float} -- The real height of the beam
        
        Returns:
            float -- The focal length 
        """
        return (distance * pixels) / height

    def calculate_distance(self, pixels : int, height : float):
        """Estimates the distance from the drone to the beam
        
        Arguments:
            focal_length {float} -- The focal length that can be calculated by putting the camera at a known distance
            pixels {int} -- The amount of pixels in between the edges of the beam
            height {float} -- The real height of the beam
        
        Returns:
            float -- the distance in the same unit as the height parameter
        """
        return (height * self.focal_length) / pixels

    def distance_from_center(self, frame_width, frame_height, min_y_coordinate, max_y_coordinate):
        """Estimates the center position of the beam and finds the offset from the camera center point
        
        Arguments:
            frame_width {int} -- The width of the frame window
            frame_height {int} -- The height of the frame window
            min_y_coordinate {int} -- The Y coordinate of the top of the beam 
            max_y_coordinate {int} -- The Y coordinate of the bottom of the beam
        """
        #Get the diff in Y
        screen_center_color = (0,255,0) #Green
        screen_center_location = (frame_width / 2, frame_height / 2)

        beam_center_color = (255,0,0) #Red
        beam_center_location = (frame_width / 2 , (min_y_coordinate + max_y_coordinate) / 2)

        print("Center offset is {} pixels".format(screen_center_location[1] - beam_center_location[1]))
        return screen_center_location[1] - beam_center_location[1]

    def center_of_beam(self, frame_width, min_y_coordinate, max_y_coordinate):
        return (frame_width / 2, (min_y_coordinate + max_y_coordinate) / 2)