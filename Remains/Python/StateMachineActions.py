from StateMachine import Drone
from DroneController import TelloController
from random import randint
import time

class StateMachineActions(object):
    """
        Class responsible for invoking the transitions and checking/setting the conditional bools
        accordingly. As the name implies, this class is responsible for invoking the actions of
        states.

        [Usage]
        The instance should only call execute (see description of execute)

        [Notes]
        Note 1: state actions cannot contain parameters with the current implementation. Instead,
        add the necessary variable as instance variable at __init__
        Note 2: Bool values such as going_right or is_safe are placed here instead of in the state
        machine declaration because those values do not affect transitions, only the actions.

        [Naming conventions]
        In order for the execute function to work properly, it is essential to name according to the
        following conventions:
            State actions/functions called in "execute": "action_" + state name 

    """

    def __init__(self, tello: TelloController, roll_speed: int,
                 roll_distance: int, yaw_speed: int = 30, yaw_distance: int = 90,
                 debug = False):
        """
            tello: Instance of the TelloController class that is connected with the drone
            roll_speed: The speed (0-100) in cm/s that the drone should use to move sideways
            roll_distance: The distance (cm) the drone should move sideways per interval
            yaw_speed: The speed (0-100) in TODO that the drone should use to rotate
            yaw_distance: The amount (0-100) the drone should rotate
        """
        self.sm = Drone(tello, debug)
        self.tello = tello
        self.start_time = 0
        self.frame = None

        self.amount_checking_frames = 20

        self.going_right = True
        self.is_safe = True

        self.roll_speed = roll_speed
        self.roll_distance = roll_distance
        self.yaw_speed = yaw_speed
        self.yaw_distance = yaw_distance

        self.states = {}
        for state in self.sm.states:
            self.states[state] = getattr(self, 'action_' + state)


    def execute(self):
        """
            Main method that executes an action depending on the state.
        """
        for state in self.states:
            if state == self.sm.state:
                self.states[self.sm.state]()

    def action_testing(self):
        print("Test")
    

    def action_facing_beam(self):
        print("facing beam")
        locked_on = self.sm.is_locked_on
        reached = self.sm.is_distance_interval_reached

        if not locked_on:
            self.sm.lock_on()
        elif locked_on and not reached:
            self.sm.increase_roll()
        elif locked_on and reached:
            self.sm.rotate_to_hall()
    
    def action_locking_on(self):
        print("Locking on")
        self.tello.lock_on(self.frame)
        if abs(self.tello.y_offset) < 10 and abs(self.tello.z_offset) < 5:
            self.sm.is_locked_on = True 
        self.sm.hold_position()
    
    def action_advancing(self):
        print("Advancing")
        #Enter
        duration = self.roll_distance / self.roll_speed 
        if self.going_right:
            self.tello.set_speed('roll', self.roll_speed)
        else:
            self.tello.set_speed('roll', -self.roll_speed)
        
        #Exit
        if time.time() - self.sm.start_time >= duration:
            print("Stopping roll")
            self.tello.set_speed('roll', 0)
            self.sm.is_locked_on = False
            self.sm.is_distance_interval_reached = True
            self.sm.make_stationary()

    def action_rotating_hall(self):
        #TODO: See rotating beam todo
        print("Rotating to hall")
        #Enter
        '''
        self.tello.set_speed('yaw', self.yaw_speed)
        if self.tello.yaw >= self.tello.starting_yaw + 90:
            print("Stopping rotation")
            self.tello.set_speed('yaw', 0)
            self.sm.detect_collision()
        '''
        
        duration = self.yaw_distance / self.yaw_speed
        self.tello.set_speed('yaw', self.yaw_speed)
        #Exit
        print(time.time() - self.sm.start_time)
        if time.time() - self.sm.start_time >= duration:
            print(time.time() - self.sm.start_time)
            print("Stopping rotation")
            self.tello.set_speed('yaw', 0)
            self.sm.detect_collision()
        

    def action_detecting_collision(self):
        print("Detecting collision")
        #Enter
        if not self.sm.is_trained:
            self.tello.train_background_subtractor()
            self.sm.is_trained = True
        else:
            self.is_safe, _ = self.tello.detect_collision(self.frame)
            #Exit
            self.sm.avoid_collision()

    def action_avoiding_collision(self):
        print("Avoiding collision")
        #TODO Remove
        self.is_safe = True
        if not self.is_safe:
            #Enter
            self.tello.avoid_collision()
            #Exit
            self.sm.rotate_to_beam()
        else:
            #Exit
            self.sm.rotate_to_beam()

    def action_rotating_beam(self):
        #TODO: Replace with yaw log measuring
        print("Rotating to beam")
        #Enter
        duration = (self.yaw_distance + 15) / self.yaw_speed
        self.tello.set_speed('yaw', -self.yaw_speed)
        #Exit
        print(time.time() - self.sm.start_time)
        if time.time() - self.sm.start_time >= duration:
            print(time.time() - self.sm.start_time)
            print("Stopping rotation")
            self.tello.set_speed('yaw', 0)
            self.sm.is_locked_on = False
            self.sm.is_distance_interval_reached = False
            self.sm.stop_rotate_for_beam()

#Uncomment for testing
'''
class test_get_attr(object):
    def increment_value(value):
        return value + 1

    def decrement_value(value):
        return value - 1

if __name__ == "__main__":
    value = 5
    states = {}
    increment = 'increment'
    decrement = 'decrement'
    states[increment] = getattr(test_get_attr, increment + '_value')(value)
    states[decrement] = getattr(test_get_attr, decrement + '_value')(value)
    curState = 'increment'
    for state in states:
        if state == curState:
            value = states[curState]
            print(value)
    curState = 'decrement'
    for state in states:
        if state == curState:
            value = states[curState]
            print(value)
'''
