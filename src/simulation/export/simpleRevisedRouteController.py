from elevator import *
from passenger import *
from controller import *


# Simple Revised Route Controller
# This controller fixes an issue where passengers are not dropped off in an optimal manner.
# To areas to optimise this controller are:
# 1) sorting the drop off queue
# 2) prioritising emptier elevators to pickup new passengers
class SimpleRevisedRouteController(Controller):
    

    def __init__(self, elevators, floors):
        super().__init__(elevators, floors)
        collection_queue = [] # a global collection queue

        # queue for each elevator 
        self.service_queue = [[] for x in range(len(elevators))] 

        # queue for the actions that each elevator should fulfil 
        self.actions_queue = [[] for x in range(len(elevators))]
        # an action takes the form ('<action>', <floor number>)



    # def update(self):
    #     # check if elevator is idle
    #     for elevator in self.elevators:
    #         if elevator.state == Elevator.States.Idle:
    #             # check if elevator needs to board people
    #             if elevator.current == next(iter(self.collection_queue), None):


    def startNextAction(self, elevator_id):
        elevator = self.elevators[elevator_id]
        nexta = next(iter(self.actions_queue[elevator_id]), None)

        if nexta is not None:
            
            # print(nexta, 'elevator:', elevator)
            # print('\n')

            if nexta[0] == 'goto':
                elevator.setTarget(nexta[1])
            elif nexta[0] == 'load':
                direction = nexta[1]
                elevator.loadPassengers(direction)
                if direction == Elevator.Directions.Up:
                    self.upButton[elevator.current] = False
                else:
                    self.downButton[elevator.current] = False
            elif nexta[0] == 'offload':
                elevator.offloadPassengers()
             # remove current action
            self.actions_queue[elevator_id].pop(0)



    def update(self):
        for elevator in self.elevators:
            # wait until elevator is Idle
            if elevator.state == Elevator.States.Idle:
                self.startNextAction(elevator.id)

    # def findClosestElevator(self, floor):
    #     # find the emptiest, closest, idle elevator, else the closest
    #     targets = filter(lambda elevator: elevator.state == Elevator.States.Idle, self.elevators)

    #     targets = list(targets)
    #     if len(targets) == 0: targets = self.elevators
    #     targets.sort(key= lambda x: (abs(x.current - floor), x.weight))

    #     # print('debug:', [(x.id, abs(x.current - floor), round(x.weight)) for x in targets])

    #     return targets[0].id
    def findClosestElevator(self, floor):
        
        return random.randint(0, len(self.elevators)-1)

        # closest = -1
        # closest_move = 0
        # distance = 1000
        # distance_move = 1000
        # for elevator in self.elevators:
        #         dx = elevator.current - floor
        #         if dx < distance and elevator.state == Elevator.States.Idle:
        #             distance = dx
        #             closest = elevator.id
                
        #         if dx < distance_move:
        #             distance_move = dx
        #             closest_move = elevator.id
        
        # if closest == -1:
        #     return closest_move
        # else: return closest



    # push button events to collection queue if not already
    def up(self, floor):
        if self.upButton[floor] == False:
            elevator_id = self.findClosestElevator(floor)
            self.actions_queue[elevator_id].append(('goto', floor))
            self.actions_queue[elevator_id].append(('load', Elevator.Directions.Up))
            self.upButton[floor] = True

    def down(self, floor):
        # if (floor, Elevator.Directions.Down) not in self.collection_queue:
        #     self.collection_queue.append((floor, Elevator.Directions.Down))
        if self.downButton[floor] == False:
            elevator_id = self.findClosestElevator(floor)
            self.actions_queue[elevator_id].append(('goto', floor))
            self.actions_queue[elevator_id].append(('load', Elevator.Directions.Down))
            self.downButton[floor] = True

    # the simple algorithm does not consider the weight
    def updateElevatorWeight(self, e, w):
        pass

    #
    def floorSelect(self, e, f):
        if not self.elevators[e.id].buttons[f]:
            self.elevators[e.id].buttons[f] = True
            self.actions_queue[e.id].append(('goto', f))
            self.actions_queue[e.id].append(('offload', None))