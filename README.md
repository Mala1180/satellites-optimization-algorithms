# satellites-optimization-algorithm

This repository contains different algorithms (mathematical and heuristic) to optimize a problem of satellites acquisition planning.\

The problem is defined as follows:\
At the start of planning is given a series of acquisition requests (AR) which have to be performed by the satellite.
Each AR has a priority and a memory cost. 
Furthermore, can be satisfied by different Data Take Opportunities (DTOs) defined by a time window. It is necessary that an AR is served only by one DTO.
The satellite can perform only one active AR at a time, so the plan cannot contain two overlapping DTOs.\
The sum of DTOs memories in the plan cannot exceed the satellite memory capacity.\
The goal is to maximize the priority of the ARs satisfied by the satellite.

The complete problem also includes the possibility to downlink the acquisitions to the ground.\
The satellite ha a downlink rate. Acquisitions can be downloaded in different Downlink Opportunities (DLOs), which has a time window.

In the ILP directory you can find the exact solution of the partial problem (without DLOs) and the complete problem as well.\
In the heuristic directory you can find the heuristic solution implemented with a genetic algorithm.

## Usage

```console
cd directory/of/project
export PYTHONPATH=.
```

### Mathematical solution:

For the partial problem:
```console
python ILP/partial_problem.py
```

For the complete problem:
```console
python ILP/complete_problem.py
```
N.B. The mathematical solution uses Gurobi solver which is a paid software, make sure you have a license for it.


### Heuristic solution:

For the partial problem:
```console
python heuristic/partial_problem.py
```

For the complete problem:
```console
python heuristic/complete_problem.py
```