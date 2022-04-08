import numpy as np
import json
import gurobipy as gp
from gurobipy import GRB
import time
from utils import overlap

# read JSON files

dtos_file = open('../data/day1_0/DTOs.json')
ars_file = open('../data/day1_0/ARs.json')
constansts_file = open('../data/day1_0/constants.json')
paws_file = open('../data/day1_0/PAWs.json')
dlos_file = open('../data/day1_0/DLOs.json')

# loads JSON, the result is a dictionary
dtos = json.loads(dtos_file.read())
ars = json.loads(ars_file.read())
constants = json.loads(constansts_file.read())
paws = json.loads(paws_file.read())
dlos = json.loads(dlos_file.read())


# get rid of dtos overlapping with paws and dlos
filtered_dtos = []
for dto in dtos:
    skip = False
    for event in paws + dlos:
        if overlap(dto, event):
            skip = True
            break
    if not skip:
        filtered_dtos.append(dto)

print(f"Total DTOs: {len(dtos)}")
print(f"Filtered DTOs: {len(filtered_dtos)}")
dtos = filtered_dtos

# Number of DTOs overlapping with the first one
# count = 0
# for dto in dtos:
#     if overlap(dto, dtos[0]):
#         count = count + 1
# print(count)

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

# add the decision variable to the model
variables = model.addMVar((DTOS_NUMBER,), vtype=GRB.BINARY)

# for each couple of dtos which overlap add a constraint
for i1, dto1 in enumerate(dtos):
    dto1_overlap = []
    for i2, dto2 in enumerate(dtos):
        if overlap(dto1, dto2) and dto1 != dto2:
            dto1_overlap.append(i2)
            # add overlapping contraints
            model.addConstr(variables[i1] + variables[i2] <= 1, "Overlapping constraint" + str(dtos.index(dto1)))

    # print("Overlapping with dto " + str(i1) + ": " + str(len(dto1_overlap)))

# add the memory constraint
model.addConstr(gp.quicksum([memories[i] * variables[i] for i in range(DTOS_NUMBER)]) <= CAPACITY, "Memory constraint")
# set objective function to maximize dto's priority
model.setObjective(gp.quicksum([priorities[i] * variables[i] for i in range(DTOS_NUMBER)]), GRB.MAXIMIZE)

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
