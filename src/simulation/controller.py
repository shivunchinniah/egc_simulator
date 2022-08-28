from abc import abstractmethod

# Controller Interface
class Controller:

    def __init__(self, elevators, floors):
        self.elevators = elevators
        self.floors = floors
        self.upButton = [False] * floors
        self.downButton = [False] * floors

    @abstractmethod
    def update(self):
        raise NotImplementedError

    @abstractmethod
    def up(self, floor):
        raise NotImplementedError

    @abstractmethod
    def down(self, floor):
        raise NotImplementedError

    @abstractmethod
    def updateElevatorWeight(self, e, w):
        raise NotImplementedError

    @abstractmethod
    def floorSelect(self, e, f):
        raise NotImplementedError