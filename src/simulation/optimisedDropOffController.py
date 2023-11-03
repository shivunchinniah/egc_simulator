from re import A
from elevator import *
from passenger import *
from controller import *


# Simple Revised Route Controller
# This controller fixes an issue where passengers are not dropped off in an optimal manner.
# To areas to optimise this controller are:
# 1) sorting the drop off queue
# 2) prioritising emptier elevators to pickup new passengers
class OptimisedDropOffController(Controller):
    

    def __init__(self, elevators, floors):
        super().__init__(elevators, floors)

        # goto floor boolean map for each elevator
        self.goto_queue = [[] for _ in range(len(elevators))]

        # floor drop off and collection queue for each elevator
        self.dropOff_queue = [[False] * floors for _ in range(len(elevators))]
        self.collection_queue_up = [[False] * floors for _ in range(len(elevators))]
        self.collection_queue_down = [[False] * floors for _ in range(len(elevators))]


    def update(self):
        for elevator in self.elevators:
            primary_collection_queue = self.collection_queue_up
            secondary_collection_queue = self.collection_queue_down
            alternate_direction = Elevator.Directions.Down
            if elevator.direction == Elevator.Directions.Down: 
                primary_collection_queue = self.collection_queue_down
                secondary_collection_queue = self.collection_queue_up
                alternate_direction = Elevator.Directions.Up

            dirChange = False

            if elevator.state == Elevator.States.Idle:
                # check if there are passengers to drop off and collect at the current floor
                if self.dropOff_queue[elevator.id][elevator.current]:
                    elevator.offloadPassengers()
                    self.dropOff_queue[elevator.id][elevator.current] = False
                
                elif primary_collection_queue[elevator.id][elevator.current]:

                    elevator.loadPassengers(elevator.direction)
                    
                    if elevator.direction == Elevator.Directions.Up:
                        self.upButton[elevator.current] = False
                    else: self.downButton[elevator.current] = False
                    
                    primary_collection_queue[elevator.id][elevator.current] = False
                
                elif not dirChange and secondary_collection_queue[elevator.id][elevator.current]:
                    elevator.direction = alternate_direction
                    elevator.loadPassengers(elevator.direction)
                    
                    if elevator.direction == Elevator.Directions.Up:
                        self.upButton[elevator.current] = False
                    else: self.downButton[elevator.current] = False
                    
                    secondary_collection_queue[elevator.id][elevator.current] = False

                # check if there are floors to go to
                elif len(self.goto_queue[elevator.id]) > 0:
                    currentDir = []
                    oppositeDir = []
                    for stop in self.goto_queue[elevator.id]:
                        diff = stop - elevator.current # diff > 0 if target floor above
                        if (elevator.direction == Elevator.Directions.Down and diff < 0) or (elevator.direction == Elevator.Directions.Up and diff > 0):
                            currentDir.append(stop)
                        else: oppositeDir.append(stop)

                    # check if floors in current direction
                    if len(currentDir) > 0:
                        target = 0
                        # go to next floor
                        if elevator.direction == Elevator.Directions.Up:
                            target = currentDir[0]
                        else: target = currentDir[-1]
                        self.goto_queue[elevator.id].remove(target) # remove from goto
                        elevator.setTarget(target)
                    else:
                        # time to change direction
                        elevator.direction = alternate_direction
                        # self.update() # retry
                        dirChange = True
                
                
                elif not dirChange: elevator.direction = Elevator.Directions.Neutral # unbias elevator

        
    def findBestElevator(self, targetFloor):
        best = 0
        best_distance = 1e10
        freeIdle = False
        # find the closest idle elevator with no work
        for elevator in self.elevators:
            distance = abs(targetFloor - elevator.current)
            if elevator.state == Elevator.States.Idle and len(self.goto_queue[elevator.id]) == 0 and distance < best_distance:
                freeIdle = True
                best = elevator.id
                best_distance = distance
                
        sameDir = False
        # check if there is an elevator going in the same direction
        if freeIdle == False:
            for elevator in self.elevators:
                diff = targetFloor - elevator.current # diff > 0 if target floor above
                if (elevator.direction == Elevator.Directions.Down and diff < 0) or (elevator.direction == Elevator.Directions.Up and diff > 0):
                    sameDir = True
                    best = elevator.id
                    break
        
        if sameDir == False and freeIdle == False:
        # assign the elevator with the smallest goto queue
            smallest = 1e10
            for elevator in self.elevators:
                queueSize = len(self.goto_queue[elevator.id])
                if queueSize < smallest:
                    smallest = queueSize
                    best = elevator.id
                

        return best
        # return random.randint(0, len(self.elevators)-1)

    # push button events to collection queue if not already
    def up(self, floor):
        if self.upButton[floor] == False:
            elevator_id = self.findBestElevator(floor)
            
            # goto the floor
            if floor not in self.goto_queue[elevator_id]:
                self.goto_queue[elevator_id].append(floor)
                self.goto_queue[elevator_id].sort()

            # pickup passengers
            self.collection_queue_up[elevator_id][floor] = True
            self.upButton[floor] = True

            # check if elevator direction is unbiased
            if self.elevators[elevator_id].direction == Elevator.Directions.Neutral:
                self.elevators[elevator_id].direction = Elevator.Directions.Up



    def down(self, floor):
        if self.downButton[floor] == False:
            elevator_id = self.findBestElevator(floor)
            
            # goto the floor
            if floor not in self.goto_queue[elevator_id]:
                self.goto_queue[elevator_id].append(floor)
                self.goto_queue[elevator_id].sort()

            # pickup passengers
            self.collection_queue_down[elevator_id][floor] = True
            self.downButton[floor] = True

            # check if elevator direction is unbiased
            if self.elevators[elevator_id].direction == Elevator.Directions.Neutral:
                self.elevators[elevator_id].direction = Elevator.Directions.Down
       

    # the simple algorithm does not consider the weight
    def updateElevatorWeight(self, e, w):
        pass

    #
    def floorSelect(self, e, f):
        if not self.elevators[e.id].buttons[f]:
            self.elevators[e.id].buttons[f] = True
            # goto the floor
            if f not in self.goto_queue[e.id]:
                self.goto_queue[e.id].append(f)
                self.goto_queue[e.id].sort()

            # drop off passengers
            self.dropOff_queue[e.id][f] = True
