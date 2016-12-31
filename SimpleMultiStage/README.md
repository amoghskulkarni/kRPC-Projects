# kRPC - Simple Multi-stage
===========================

## Objective
------------
To use kRPC to complete one of the tests on Hammer Solid Rocket Booster (SRB).

The test requirements are -

  1. Altitude 51000m to 530000m
  2. Speed 140.0m/s to 230.0m/s

## Approach
-----------
Used PID controller to control the throttle by observing the speed of the rocket.

An 8 stage rocket was built which has 2 stages of solid fuel, 1 stage of liquid fuel,
and 1 stage of solid fuel to be tested. All other stages attribute to separators and
the parachute. The craft file for the rocket can be found [here]().

![alt text](https://github.com/amoghskulkarni/kRPC-Projects/blob/master/KRPC_HelloWorld/images/2016-12-25.png "The rocket")

## Results
----------
Results would have been more or less the same as that of the earlier [Hello world]() example
where I have plotted the results of various variables related to the rocket during
flight, till the rocket gets stabilized at the desired speed.
