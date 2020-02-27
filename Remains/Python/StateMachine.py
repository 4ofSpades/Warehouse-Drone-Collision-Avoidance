from transitions import Machine
from DroneController import TelloController

import time
from random import randint

class Drone(object):
    """
        Class responsible for handling the state and state transitions. The actual implementation 
        of the actions of the drone is handled in DroneController.py, with StateMachineActions.py
        being the bridge class responsible for handling transitions and setting conditionals. As a
        safety measure for other programmers extending/replacing parts however, the necessary 
        conditions for state transitions are also added here.

        [Notes]
        Note 1: The condition parameter in the add transition function only accepts callables, hence
        why a separate get bool function is required instead of directly passing the instace variable

        Note 2: Debug mode adds an extra state called test. This state does nothing, but is necessary
        as a first state because of the way the time_stamp function works. From there the function
        <<instance>>.set_state(statename) can be used to transition freely.

        [Naming conventions]
        In order for the current implementation to work, it is important to uphold the following
        naming conventions:
            State: Verb in continuous (-ing) form
            Action: Verb in present simple first person form
            Condition bool: Must start with "is"
            Condition func: "get_" + boolean name
    """

    def __init__(self, tello : TelloController, debug = False):
        self.tello = tello

        #Placed to remove errors
        self.state = None

        #Conditional bools
        self.debug = debug

        self.is_locked_on = False #Beam centering
        self.is_distance_interval_reached = True #Advancing
        self.is_trained = False #Detecting collision

        self.start_time = time.time()
        self.end_time = None
        self.states = ['facing_beam', 'detecting_collision', 'avoiding_collision',
            'advancing', 'locking_on', 'rotating_hall', 'rotating_beam']
        if self.debug:
            self.states.append('testing')
        self.machine = Machine(model=self, states=self.states, initial='facing_beam', 
            before_state_change='time_stamp')
        self.__add_transitions()
    
    def __add_transitions(self):
        """
            Adds transitions to states, which can be invoked using object.<<trigger_name>>()

            For clarity, it is recommended to group the transitions per source state
        """
        #Source facing_beam
        self.machine.add_transition('lock_on', source='facing_beam', dest='locking_on')
        self.machine.add_transition('rotate_to_hall', source='facing_beam', dest='rotating_hall',
                                    conditions=['get_is_locked_on', 'get_is_distance_interval_reached'])
        self.machine.add_transition('increase_roll', source='facing_beam', dest='advancing',
                                    conditions='get_is_locked_on', unless='get_is_distance_interval_reached')

        #Source locking on
        self.machine.add_transition('hold_position', source='locking_on', dest='facing_beam',
                                    conditions='get_is_locked_on')
        
        #Source advancing
        self.machine.add_transition('make_stationary', source='advancing', dest='facing_beam', 
                                    conditions='get_is_distance_interval_reached')
        
        #Source rotating_hall
        self.machine.add_transition('detect_collision', source='rotating_hall', 
                                    dest='detecting_collision', 
                                    conditions=['get_is_locked_on', 'get_is_distance_interval_reached'])

        #Source detecting collision
        self.machine.add_transition('avoid_collision', source='detecting_collision',
                                    dest='avoiding_collision', 
                                    conditions=['get_is_locked_on', 'get_is_distance_interval_reached'])

        #Source avoiding collision
        self.machine.add_transition('rotate_to_beam', source='avoiding_collision', dest='rotating_beam',
                                    conditions=['get_is_locked_on', 'get_is_distance_interval_reached'])

        #Source rotating beam
        self.machine.add_transition('stop_rotate_for_beam', source='rotating_beam', dest='facing_beam')

        #if self.debug:
            #for state in self.states:
                #enter_name = "test_to_" + state
                #exit_name = state + "_to_test"
                #self.machine.add_transition(enter_name, source='test', dest=state)
                #self.machine.add_transition(exit_name, source=state, dest='test')



    def time_stamp(self):
        """
            Sets the start time to the current time
        """
        self.start_time = time.time()

    def get_is_locked_on(self):
        return self.is_locked_on

    def get_is_distance_interval_reached(self):
        return self.is_distance_interval_reached

    def get_is_trained(self):
        return self.is_trained


'''
def test_case_movement():
    print("==TESTING MOVEMENT==")
    drone = Drone(None)
    drone.increase_roll()
    print(drone.state != 'advancing')
    drone.lock_on()
    print(drone.state == 'locking_on')
    drone.hold_position()
    print(drone.state != 'facing_beam')
    drone.is_locked_on = True
    drone.hold_position()
    print(drone.state == 'facing_beam')

def test_case_rotation():
    print("==TESTING ROTATION==")
    drone = Drone(None)
    drone.is_locked_on = True
    drone.is_distance_interval_reached = False
    drone.rotate_to_hall()
    print(drone.state != 'rotating_hall')
    drone.is_distance_interval_reached = True
    drone.is_locked_on = False
    drone.rotate_to_hall()
    print(drone.state != 'rotating_hall')
    drone.is_locked_on = True
    drone.rotate_to_hall()
    print(drone.state == 'rotating_hall')

def test_case_collision_avoidance():
    print("==TESTING COLLISION AVOIDANCE==")
    drone = Drone(None)
    drone.is_locked_on = True
    drone.is_distance_interval_reached = True
    drone.rotate_to_hall()
    drone.detect_collision()
    print(drone.state == 'detecting_collision')
    drone.avoid_collision()
    print(drone.state == 'avoiding_collision')
    drone.is_locked_on = False
    drone.rotate_to_beam()
    print(drone.state != 'rotating_beam')
    drone.is_locked_on = True
    drone.rotate_to_beam()
    print(drone.state == 'rotating_beam')
    drone.stop_rotate_for_beam()
    print(drone.state == 'facing_beam')

    

    

test_case_movement()
test_case_rotation()
test_case_collision_avoidance()
'''