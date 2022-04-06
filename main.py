import functools
import sys

import numpy as np
import json
import gurobipy as gp
from gurobipy import GRB
import time

# read JSON files

dtos_file = open('data/day1_0/DTOs.json')
ars_file = open('data/day1_0/ARs.json')
constansts_file = open('data/day1_0/constants.json')

# loads JSON, the result is a dictionary
dtos = json.loads(dtos_file.read())
ars = json.loads(ars_file.read())
constants = json.loads(constansts_file.read())

CAPACITY = constants['MEMORY_CAP']
DTOS_NUMBER = len(dtos)
incidences = np.array(list(map(lambda dto: dto["incidence"], dtos)))
memories = np.array(list(map(lambda dto: dto["memory"], dtos)))
dtos_id = np.array(list(map(lambda dto: dto["id"], dtos)))

# Read and solve model
model = gp.Model()

print("Prepare variables and constraints...")
start = time.time()

# add the decision variable to the model
variables = model.addMVar(DTOS_NUMBER, vtype=GRB.BINARY)

variables_constraint = []

# print(np.ufunc.reduce(np.array(dtos), dtype=None, out=None, keepdims=False, initial={'start_time': 0, 'stop_time': 0},
#                      where=lambda acc, dto: dto))


from functools import reduce


# def get_start_time(a):
#     return a['start_time']
#
#
# vfunc = np.vectorize(get_start_time)
#
# for dto in dtos:
#     indexes = np.where(np.logical_and(dto['start_time'] <= vfunc(dtos), vfunc(dtos) <= dto['stop_time']))
#     print(indexes[0])
#     break


for dto1 in dtos:
    for dto2 in dtos:
        if dto1['start_time'] <= dto2['stop_time'] and dto1['stop_time'] >= dto2['start_time']:
        #if dto2['start_time'] <= dto1['start_time'] <= dto2['stop_time']:
            variables_constraint.append(variables[dtos.index(dto1)])
            variables_constraint.append(variables[dtos.index(dto2)])
            print([dtos.index(dto1), dtos.index(dto2)])
            # add overlapping contraints
            model.addConstr(gp.quicksum(variables_constraint) <= 1, "Overlapping constraint" + str(dtos.index(dto1)))
            #variables_constraint = []
    print(variables_constraint)
    break


# add the memory constraint
model.addConstr(gp.quicksum([memories[i] * variables[i] for i in range(DTOS_NUMBER)]) <= CAPACITY, "Memory constraint")
# set objective function to maximize dto's incidences
model.setObjective(gp.quicksum([incidences[i] * variables[i] for i in range(DTOS_NUMBER)]), GRB.MAXIMIZE)

end = time.time()
print("Preparation terminated in ", end - start)

# solve model
print("Solve model...")
start = time.time()

model.optimize()

if model.Status == GRB.INF_OR_UNBD:
    # Turn presolve off to determine whether model is infeasible
    # or unbounded
    model.setParam(GRB.Param.Presolve, 0)
    model.optimize()
if model.Status == GRB.OPTIMAL:
    print('Optimal objective: %g' % model.ObjVal)
    print(model.getJSONSolution())
    # print("RESOCONTO", model.display())
elif model.Status != GRB.INFEASIBLE:
    print('Optimization was stopped with status %d' % model.Status)

end = time.time()
print("Solved in ", end - start)
