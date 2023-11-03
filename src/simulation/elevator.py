# // -------- Elevator Simulator --------
import random
import enum
import math
import json
from turtle import position

# to do implement elevator inside buttons


class Elevator:

    class States(enum.Enum):
        Idle = 0
        Travelling = 1
        Loading = 2
        Offloading = 3



    class Directions(enum.Enum):
        Up = 0
        Down = 1
        Neutral = 3

    def __init__(self, id, sp):
        self.id = id
        floor_num = random.randint(0, sp['floors'] - 1)
        self.position = floor_num * sp['floor_height']
        self.current = floor_num
        self.target = floor_num
        self.speed = sp['floor_height'] / sp['time_per_floor']
        self.onload = sp['loading_time']
        self.offload = sp['offloading_time']
        self.state = self.States.Idle
        self.floor_height = sp['floor_height']
        self.offload_timer = 0
        self.onload_timer = 0
        self.weight = 0
        self.doorsOpen = False
        self.passengers = []
        self.direction = self.Directions.Neutral
        self.distance = 0
        self.buttons = [False] * sp['floors']
        self.maxWeight = 1200


    def dump(self):
        
        return dict({
        'id': int(self.id),
        'position': float(self.position),
        'current': int(self.current),
        'target': int(self.target),
        'speed': self.speed,
        'state': self.state.name,
        'offload_timer': self.offload_timer,
        'onload_timer': self.onload_timer,
        'weight': self.weight,
        'passengers': int(len(self.passengers)),
        'distance': self.distance,
        'floor_buttons': list(self.buttons)
    })

    # to String
    def __repr__(self):
        return "id:{}, direction:{}, position:{}, current:{}, target:{}, speed:{}, onload:{}, offload:{}, state:{}, floor_height:{}, offload_timer:{}, onload_timer:{}, weight:{}, passengers:{}, distance:{}".format(
            self.id, self.direction, self.position, self.current, self.target, self.speed,
            self.onload, self.offload, self.state, self.floor_height,
            self.offload_timer, self.onload_timer, self.weight,
            len(self.passengers), self.distance)

    def __str__(self):
         return "id:{}, direction:{}, position:{}, current:{}, target:{}, speed:{}, onload:{}, offload:{}, state:{}, floor_height:{}, offload_timer:{}, onload_timer:{}, weight:{}, passengers:{}, distance:{}".format(
            self.id, self.direction, self.position, self.current, self.target, self.speed,
            self.onload, self.offload, self.state, self.floor_height,
            self.offload_timer, self.onload_timer, self.weight,
            len(self.passengers), self.distance)

    def toJSON(self):
        return json.dumps(self,
                          default=lambda o: o.__dict__,
                          sort_keys=True,
                          indent=4)


    

    # interface for people board the elevator
    def board(self, person):
        if (self.state == self.States.Loading):
            # check if there is space on the elevator
            if(len(self.passengers) > 14): return False
            if(self.weight + person.weight > self.maxWeight): return False
            self.weight += person.weight
            self.passengers.append(person)
            return True
        else:
            return False

    # interface for people to leave the elevator
    def leave(self, person):
        # allow for offloading in loading state
        if (self.state == self.States.Offloading or self.state == self.States.Loading):
            self.weight -= person.weight
            self.passengers.remove(person)
            return True
        else:
            return False

    # interface for controller to accept passengers
    def loadPassengers(self, direction):
        if self.state == self.States.Idle and self.current == self.target:
            self.state = self.States.Loading
            self.direction = direction
            return True
        else:
            return False

    # interface for controller to release passengers
    def offloadPassengers(self):
        if self.state == self.States.Idle and self.current == self.target:
            self.state = self.States.Offloading
            self.buttons[self.current] = False
            return True
        else:
            return False

    def setTarget(self, target):
        self.target = target

    def update(self, dt):

        # update passengers
        for passenger in self.passengers:
            passenger.update(dt)

        # Check if offloading
        if self.state == self.States.Offloading:
            self.offload_timer = self.offload_timer + dt
            if self.offload_timer >= self.offload:
                self.state = self.States.Idle
                self.offload_timer = 0

        # Check if loading
        elif self.state == self.States.Loading:
            self.onload_timer = self.onload_timer + dt
            if self.onload_timer >= self.onload:
                self.state = self.States.Idle
                self.onload_timer = 0

        elif self.state == self.States.Idle:
            # Check if need to move
            if self.current != self.target:
                self.state = self.States.Travelling

        # Update position of travelling elevator
        elif self.state == self.States.Travelling:
            if self.target > self.current: direction = 1
            else: direction = -1

            # Move closer to target
            self.position = self.position + (direction * dt * self.speed)
            self.distance += dt * self.speed  # update the total distance travelled

            # Update the current floor (has to move past floor)
            if direction > 0:  # if moving up use floor
                self.current = math.floor(self.position / self.floor_height)
            else:
                self.current = math.ceil(self.position / self.floor_height)

            # Lastly check if elevator has reached the target (and within 2 times dt*speed of the floor position)
            if self.current == self.target and abs(self.position - (
                    self.floor_height * self.target)) < (2 * dt * self.speed):
                # set the elevator to the correct position
                self.position = self.floor_height * self.target

                self.state = self.States.Idle
