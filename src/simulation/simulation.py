
from ast import Pass
import math
import queue
import random
import tkinter
import enum
from tqdm.auto import tqdm
import pickle
from typing import List
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy import integrate
import json
import pickle

from elevator import *
from passenger import *

from simpleController import *

# // -------- Simulation Constants --------

simulation_params = {
    'floors': 10,
    'elevators': 2,
    'loading_time': 6,  # seconds
    'offloading_time': 6,  # seconds
    'time_per_floor': 10,  # seconds
    'floor_height': 4,  # metres
    'dt': 1 / 30,  # seconds simulation step interval
}

# // -------- Generators --------

def generateElevators(sp):
    elevators = sp['elevators']
    return [Elevator(x, sp) for x in range(elevators)]



# // -------- Traffic Controller --------


class SimulationScene:

    def __init__(self, sp, elevators, passengers, traffic_times,
                 traffic_passengers, controller: Controller):
        self.elevators = elevators
        self.queue = [[] for y in range(sp['floors'])]
        self.passengers = passengers
        self.toUpdate = []
        self.start_time = sp['start']
        self.end_time = sp['end']
        self.time = self.start_time
        self.traffic_index = 0
        self.traffic_times = traffic_times
        self.traffic_passengers = traffic_passengers
        self.dt = sp['dt']
        self.controller = controller
        self.prevState = None
        self.log = []
        self.delayedPassengers = []



    def dumpScene(self):
        return {
            'time': self.time,
            'elevators': [elevator.dump() for elevator in self.elevators],
            'buttons': {
                'up': list(self.controller.upButton), 
                'down': list(self.controller.downButton)
            },
            'queue': [len(x) for x in self.queue]
        }

    def triggerPassenger(self, passenger):
        p_from = passenger.route[passenger.route_index]
        p_to = passenger.route[passenger.route_index + 1]
        # trigger button event & add passenger to relevant queue
        if p_from < p_to:
            self.controller.up(p_from)
            self.queue[p_from].append((Elevator.Directions.Up, passenger))
        else:
            self.controller.down(p_from)
            self.queue[p_from].append(
                (Elevator.Directions.Down, passenger))

        passenger.state = Passenger.States.Waiting

        self.toUpdate.append(passenger)

            # print('dispatched passenger ', self.time, p_from, '-->', p_to)


    def tick(self):

        # check if delayed passengers have reached their destination
        for passenger in self.delayedPassengers:
            if passenger.state == Passenger.States.Idle:
                self.triggerPassenger(passenger)
                self.delayedPassengers.remove(passenger)

        if self.traffic_index < len(self.traffic_times):
            # check if time to dispatch passenger
            if (self.time >= self.traffic_times[self.traffic_index]):
                passenger = self.passengers[self.traffic_passengers[
                    self.traffic_index]]
                self.traffic_index += 1

                # first check if the passenger is idle
                if(passenger.state == Passenger.States.Idle):
                    # push the passenger to the queue
                    self.triggerPassenger(passenger)
                else:
                    # push the passenger to the delayed queue
                    self.delayedPassengers.append(passenger)
        

        # if round(self.time) % 1700 == 0:
        #     print("Time: ", self.time)
        #     # for e in self.elevators:
        #     #     print('--', e)
        #     print(self.dumpScene())

        # check if there are passengers to load or offload to and from the elevators
        for elevator in self.elevators:

            if (elevator.state == Elevator.States.Loading):  # check if loading
                # load next passenger in floor queue
                for direction, passenger in self.queue[elevator.current]:
                    if direction == elevator.direction:
                        
                        # attempt to board a passenger 
                        if elevator.board(passenger):
                            self.controller.updateElevatorWeight(
                                elevator.id, elevator.weight)

                            passenger.state = Passenger.States.Passenger

                            # remove passenger from queue
                            self.queue[elevator.current].remove((direction, passenger))
                            self.toUpdate.remove(passenger)
                            
                            # simulate passenger pushing the floor button
                            self.controller.floorSelect(elevator, passenger.route[passenger.route_index + 1])

            # off load passengers even when in loading state
            elif (elevator.state == Elevator.States.Offloading or elevator.state == Elevator.States.Loading
                  ):  # check if offloading
                # offload passengers
                for passenger in elevator.passengers:
                    # check if elevator is at passenger destination
                    p_dest = passenger.route[passenger.route_index + 1]
                    if (elevator.current == p_dest):
                        # offload the passenger
                        elevator.leave(passenger)
                        passenger.state = Passenger.States.Idle
                        self.controller.updateElevatorWeight(
                            elevator.id, elevator.weight)
                        # update passenger trip index
                        passenger.route_index = passenger.route_index + 1
        
            # update the elevator
            elevator.update(self.dt)

        # update the controller
        self.controller.update()
        
        for item in self.toUpdate:
            item.update(self.dt)

        # finally update the time
        self.time = self.time + self.dt

        currentState = self.dumpScene()
        if self.prevState:
            if self.prevState['elevators'] == currentState['elevators'] and self.prevState['buttons'] == currentState['buttons'] and self.prevState['queue'] == currentState['queue']:
                pass
            else: self.log.append(dict(currentState))
        
        self.prevState = currentState


# // -------- Test Elevator  --------

def elevatorTest():
    simulation_params = {
        'floors': 10,
        'elevators': 2,
        'loading_time': 6,  # seconds
        'offloading_time': 6,  # seconds
        'time_per_floor': 10,  # seconds
        'floor_height': 4,  # metres
        'dt': 1 / 30,  # seconds simulation step interval
    }

    elevator = Elevator(0, simulation_params)

    print("initial:", elevator)


    dt = simulation_params['dt']

    passenger = Passenger(65, [0, 6, 0])

    for i in range(int(2 / dt)): elevator.update(dt) # wait two seconds
    # first load a passenger
    elevator.loadPassengers(Elevator.Directions.Up)

    for i in range(int(2 / dt)): elevator.update(dt) # wait two seconds
    print('Loading passenger --> ', elevator )

    elevator.board(passenger)

    for i in range(int(2 / dt)): elevator.update(dt) # wait two seconds
    print('Loading passenger --> ', elevator )

    for i in range(int(3 / dt)): elevator.update(dt) # wait three seconds
    print('Loading passenger --> ', elevator )

    # Now travel
    elevator.setTarget(4)
    for i in range (int(50 / dt)):
        # print every 5 seconds
        if(i % int(5 / dt) == 0):
            print(i * dt, '-->', elevator)
        elevator.update(dt)

    # offload the passenger
    elevator.offloadPassengers()
    elevator.leave(passenger)

    for i in range(int(2 / dt)): elevator.update(dt) # wait two seconds
    print('Passenger left --> ', elevator )

    for i in range(int(5 / dt)): elevator.update(dt) # wait two seconds
    print('Passenger left --> ', elevator )




class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__

# Main function

if __name__ == '__main__':
    print("Running...")

    # elevatorTest()

    # load sim data
    file = open('p1500e10f50.bin', 'rb')

    db = pickle.load(file)

    file.close()

    passengers = db['passengers']
    traffic_times = db['traffic_times']
    traffic_passengers = db['traffic_passengers']
    sp = db['simulation_params']
    sp['elevators'] = 11
    

    print('Simulation Parameters: ', sp)


    elevators = generateElevators(sp)
    
    # for elevator in elevators:
    #     print('--', elevator.__dict__)

    simpleController = SimpleController(elevators, sp['floors'])
    sc = SimulationScene(sp, elevators, passengers, traffic_times, traffic_passengers, simpleController)


    start = sp['start']
    end = sp['end']

    for i in tqdm(range(int(( (end-start) ) / sp['dt']))):
        sc.tick()



t_trips = 0
t_wait  = 0
t_travel = 0

for passenger in sc.passengers: 
    trips = len(passenger.route)

    t_trips += trips

    t_wait += passenger.waitingTime
    t_travel += passenger.rideTime


filePrefix = 'out_p{}e{}f{}'.format(sp['passengers'], sp['elevators'], sp['floors'])

outputfile = filePrefix + '.json'


passengerDumpFile = filePrefix + '.bin'

print('Writing passenger dump file')
with open(passengerDumpFile, 'wb') as f:
    pickle.dump(sc.passengers, f)
print('Passenger dump written to: ', passengerDumpFile)

print()

print('Writing JSON output file')
with open(outputfile, 'w') as f:
    json.dump({
        'log': sc.log,
        'sp': sp,
        'distribution': db['distribution']
    }
        , f)

# print('changes', len(sc.log))

print('mean wait', t_wait / t_trips)
print('total:', 'wait ->', t_wait, 'travel ->', t_travel)


print('Output file:', outputfile)




