import random
import enum
import json
# // -------- Passenger Simulator --------

class Passenger:

    class States(enum.Enum):
        Idle = 1
        Waiting = 2
        Passenger = 3
        Outside = 4


    def __init__(self, weight, route):
        self.weight = weight
        self.route = route
        self.floor = 0
        self.route_index = 0 # the current positioning the routes
        self.state = self.States.Idle
        self.waitingTime = 0
        self.rideTime = 0

    def __repr__(self):
        return "w:{}, route:{}, floor:{}, routeIndex:{}, state:{}, waiting:{}, ride:{}".format(self.weight, self.route, self.floor, self.route_index, self.state, self.waitingTime, self.rideTime)

    def __str__(self):
        return "w:{}, route:{}, floor:{}, routeIndex:{}, state:{}, waiting:{}, ride:{}".format(self.weight, self.route, self.floor, self.route_index, self.state, self.waitingTime, self.rideTime)
    
    def toJSON(self):
        return json.dumps(self,
                        default=lambda o: o.__dict__,
                        sort_keys=True,
                        indent=4)

    def update(self, dt):
        if self.state == self.States.Idle:
            pass
        
        elif self.state == self.States.Waiting:
            self.waitingTime = self.waitingTime + dt # increment timer

        elif self.state == self.States.Passenger:
            self.rideTime = self.rideTime + dt # increment timer

        elif self.state == self.States.Outside:
            pass
