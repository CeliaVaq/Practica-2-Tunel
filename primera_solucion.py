"""
Solution to the one-way tunnel
solucion 1 que puedan pasar coches en una direccion siempre que no
haya coches en el tunel en la otra direccion
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "north"
NORTH = "south"

NCARS = 50

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.inside_north = Value('i', 0)
        self.inside_south = Value('i', 0)
        self.sem_north = Condition(self.mutex)
        self.sem_south = Condition(self.mutex)
    
    def no_cars_north_inside(self):
        return self.inside_north.value == 0
    
    def no_cars_south_inside(self):
        return self.inside_south.value == 0
    
    def wants_enter(self, direction):
        self.mutex.acquire()
        
        if direction == SOUTH:
            self.sem_north.wait_for(self.no_cars_north_inside)
            self.inside_south.value = self.inside_south.value + 1
        else:
            self.sem_south.wait_for(self.no_cars_south_inside)
            self.inside_north.value = self.inside_north.value + 1
            
        self.mutex.release()

    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        
        if direction == NORTH:
            self.inside_north.value = self.inside_north.value - 1
            if(self.inside_north.value==0):
                self.sem_north.notify_all()
        else:
            self.inside_south.value = self.inside_south.value - 1
            if(self.inside_south.value==0):
                self.sem_south.notify_all()
    
        self.mutex.release()
        

        
def delay(n=3):
    time.sleep(random.random()*n)

def car(cid, direction, monitor):
    flecha = '^'
    if direction == NORTH:
        flecha = 'v'
    print(f"car {cid} direction {direction} created")
    delay(6)
    print(f"car {cid} heading {direction} wants to enter")
    monitor.wants_enter(direction)
    print(f"car {cid} heading {direction} enters the tunnel")
    delay(3)
    print(f"car {cid} heading {direction} leaving the tunnel")
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel ({flecha})")



def main():
    monitor = Monitor()
    cid = 0
    for _ in range(NCARS):
        direction = NORTH if random.randint(0,1)==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s

if __name__ == '__main__':
    main()
    
    
    
    
#
