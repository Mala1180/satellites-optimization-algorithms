# satellites-optimization-algorithm

This repository contains different solution approaches (mathematical and heuristic) to optimize problems of satellites acquisition planning.
In the ILP directory you can find the exact solution of the relaxed problem (without DLOs) and the complete problem as well.
In the heuristic directory you can find the heuristic solution implemented with a genetic algorithm.

## Usage

```console
cd directory/of/project
export PYTHONPATH=. 
```

### Heuristic solution:

```console
python heuristic/relaxed_problem.py
```

### Mathematical solution:

For the relaxed problem:
```console
python ILP/relaxed_problem.py
```

For the complete problem:
```console
python ILP/complete_problem.py
```
N.B. The mathematical solution use Gurobi solver which is a paid software, make sure you have a license for it.
