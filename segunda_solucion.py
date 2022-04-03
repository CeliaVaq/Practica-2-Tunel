#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 10:43:22 2022

@author: mat
"""

import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "north"
NORTH = "south"

NCARS = 20
MAX = 3


class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.inside_north = Value('i', 0)
        self.inside_south = Value('i', 0)
        self.sem_north = Condition(self.mutex)
        self.sem_south = Condition(self.mutex)
        
        self.contador_north = Value('i',0) #cuenta los que han pasado y estan pasando en una direccion
        self.contador_south = Value('i',0) #cuenta los que han pasado y estan pasando en una direccion
        self.waiting_south = Value('i',0) #numero de coches esperando para entrar con direccion sur
        self.waiting_north = Value('i',0) #numero de coches esperando para entrar con direccion sur
    
    def no_cars_north_inside(self):
        return self.inside_north.value == 0 and (self.contador_south.value < MAX or self.waiting_north.value == 0)
        #(self.waiting_north == 0 and self.waiting_south>0))
        
    def no_cars_south_inside(self):
        return self.inside_south.value == 0 and (self.contador_north.value < MAX or self.waiting_south.value == 0)
    
    def wants_enter(self, direction):
        self.mutex.acquire()
        
        if direction == SOUTH:
            self.waiting_south.value = self.waiting_south.value + 1
            print(f"waiting_south: {self.waiting_south.value}")
            self.sem_north.wait_for(self.no_cars_north_inside)
            self.inside_south.value = self.inside_south.value + 1
            self.contador_south.value = self.contador_south.value + 1
            print(f"contador_south: {self.contador_south.value}")
            self.waiting_south.value = self.waiting_south.value - 1
            
        else:
            self.waiting_north.value = self.waiting_north.value + 1
            print(f"waiting_north: {self.waiting_north.value}")
            self.sem_south.wait_for(self.no_cars_south_inside)
            self.inside_north.value = self.inside_north.value + 1
            self.contador_north.value = self.contador_north.value + 1
            print(f"contador_north: {self.contador_north.value}")
            self.waiting_north.value = self.waiting_north.value - 1
            
        self.mutex.release()

    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        
        if direction == NORTH:
            self.inside_north.value = self.inside_north.value - 1
            if (self.inside_north.value==0):
                self.contador_south.value = 0
                
                self.sem_north.notify_all()
                self.sem_south.notify_all()
            
        else:
            self.inside_south.value = self.inside_south.value - 1
            if(self.inside_south.value==0):
                self.contador_north.value = 0
                
                self.sem_south.notify_all()
                self.sem_north.notify_all()
                
        print(f"waiting_north: {self.waiting_north.value}")
        print(f"waiting_south: {self.waiting_south.value}")
        self.mutex.release()
        

        
def delay(n=3):
    time.sleep(random.random()*n)

def car(cid, direction, monitor):
    flecha  = 'v'
    if direction == SOUTH:
        flecha = '^'
    print(f"car {cid} direction {direction} created")
    delay(6)
    print(f"car {cid} heading {direction} wants to enter")
    monitor.wants_enter(direction)
    
    
    print(f"car {cid} heading {direction} enters the tunnel")
    delay(3)
    print(f"car {cid} heading {direction} leaving the tunnel")
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel({flecha},{cid})")


def main():
    monitor = Monitor()
    cid = 0
    for _ in range(NCARS):
        direction = NORTH if random.randint(0,1)==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1/0.3)) # a new car enters each 0.5s

if __name__ == '__main__':
    main()
    
    
    
    
