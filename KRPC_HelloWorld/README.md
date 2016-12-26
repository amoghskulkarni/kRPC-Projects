# kRPC - Hello World
====================

## Objective
------------
To use kRPC to complete one of the tests on Mk16 parachute.

The test requirements are -

  1. Altitude 3000m to 10000m
  2. Speed 111.0m/s to 230.0m/s

## Approach
-----------
Used PID controller to control the throttle by observing the speed of the rocket.
So, the system to be controlled is rocket, which takes "throttle" as the input from
the controller and produces "speed" as the output and feeds it back to the controller,
forming a closed loop system. Reference diagram is as follows -

![alt text]("PID controller")

A simple 3 stage rocket is used for this task, which has 2 liquid fuel tanks attached to
liquid fuel engine controlled from command pod. (.craft file can be found [here]())

![alt text]("The rocket")

The PID library used can be found [here](https://github.com/ivmech/ivPID).

## Results
----------
Results generated with different PID values are hard-coded in the code and stored in
respective .csv files. Graphs are as follows -

P = 0.4, I = 0.02, D = 0.01

![alt text]("Graph 1")
