import sys
import numpy as np
import json
import gurobipy as gp
from gurobipy import GRB
import time
from utils.overlap import overlap

# read JSON files
dtos_file = open('../data/day1_0/DTOs.json')
ars_file = open('../data/day1_0/ARs.json')
constansts_file = open('../data/day1_0/constants.json')
paws_file = open('../data/day1_0/PAWs.json')

# loads JSON, the result is a dictionary
dtos = json.loads(dtos_file.read())
ars = json.loads(ars_file.read())
constants = json.loads(constansts_file.read())
paws = json.loads(paws_file.read())

# get rid of dtos overlapping with paws and dlos
filtered_dtos = []
for dto in dtos:
    skip = False
    for event in paws:
        if overlap(dto, event):
            skip = True
            break
    if not skip:
        filtered_dtos.append(dto)

print(f"Total DTOs: {len(dtos)}")
print(f"Filtered DTOs: {len(filtered_dtos)}")
dtos = filtered_dtos

CAPACITY = constants['MEMORY_CAP']
DTOS_NUMBER = len(dtos)

priorities = []

# populate array of priorities
for index_dto, dto in enumerate(dtos):
    priorities.append(next((ar['rank'] for ar in ars if ar['id'] == dto['ar_id']), None))

memories = np.array(list(map(lambda dto_: dto_["memory"], dtos)))
dtos_id = np.array(list(map(lambda dto_: dto_["id"], dtos)))

# Read and solve model
model = gp.Model()

print("Prepare variables and constraints...")
start = time.time()

# add the decision variables to the model
dtos_variables = list(model.addMVar((DTOS_NUMBER,), vtype=GRB.BINARY, name="DTOs"))

grouped_dtos = dict()

# for each couple of dtos which overlap add a constraint
for i1, dto1 in enumerate(dtos):
    for i2, dto2 in enumerate(dtos):
        if overlap(dto1, dto2) and dto1 != dto2:
            # add overlapping constraints
            model.addLConstr(dtos_variables[i1] + dtos_variables[i2] <= 1,
                             f"Overlapping constraint for DTOs {dto1['id']} and {dto2['id']}")

    if dto1['ar_id'] not in grouped_dtos.keys():
        grouped_dtos[dto1['ar_id']] = [dto1]
    else:
        grouped_dtos[dto1['ar_id']].append(dto1)

# add the single satisfaction constraints
for ar_id in grouped_dtos.keys():
    model.addLConstr(gp.quicksum([dtos_variables[dtos.index(dto_)] for dto_ in grouped_dtos[ar_id]]) <= 1,
                     f"Single satisfaction constraint for {ar_id}")

# add the memory constraint
model.addLConstr(gp.quicksum([memories[i] * dtos_variables[i] for i in range(DTOS_NUMBER)]) <= CAPACITY,
                 "Memory constraint")
# set objective function to maximize dto's priority
model.setObjective(gp.quicksum([priorities[i] * dtos_variables[i] for i in range(DTOS_NUMBER)]), GRB.MAXIMIZE)

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
    print(f'Number of constraints: {len(model.getConstrs())}')
    # print("RESOCONTO", model.display())
elif model.Status != GRB.INFEASIBLE:
    print('Optimization was stopped with status %d' % model.Status)

end = time.time()
print("Solved in ", end - start)
