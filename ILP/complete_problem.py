import json
import time

import gurobipy as gp
import matplotlib.pyplot as plt
import numpy as np
from gurobipy import GRB

from utils.functions import overlap, load_instance

INSTANCE = 'day1_40'
dtos, ars, constants, paws, dlos = load_instance('day1_40')

initial_dlos = dlos

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

dtos = filtered_dtos
dlos = sorted(dlos, key=lambda dlo: dlo['start_time'])

# add the dummy variable for some next constraints
stop_time = max(dtos[len(dtos) - 1]['stop_time'], dlos[len(dlos) - 1]['stop_time'])
dummy_dlo = dlos[len(dlos) - 1].copy()
dummy_dlo['start_time'] = stop_time + 1
dummy_dlo['stop_time'] = dummy_dlo['start_time']
dlos.append(dummy_dlo)

CAPACITY = constants['MEMORY_CAP']
DOWNLINK_RATE = constants['DOWNLINK_RATE']
DTOS_NUMBER = len(dtos)
DLOS_NUMBER = len(dlos)

print(f"Total DTOs: {len(dtos)}")
print(f"Filtered DTOs: {len(filtered_dtos)}")
print(f"Total DLOs: {len(dlos)}")

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

z_ji = []
for index in range(DLOS_NUMBER):
    z_ji.append(list(model.addMVar((DTOS_NUMBER,), vtype=GRB.BINARY, name=f"DTOs_downloaded_in_DLO_{index}")))

grouped_dtos = dict()

# for each couple of dtos which overlap add a constraint
for i1, dto1 in enumerate(dtos):
    for i2, dto2 in enumerate(dtos):
        if overlap(dto1, dto2) and dto1 != dto2:
            # add overlapping constraints
            model.addConstr(dtos_variables[i1] + dtos_variables[i2] <= 1,
                            f"Overlapping_constraint_for_DTOs_{dto1['id']}_and_{dto2['id']}")

    if dto1['ar_id'] not in grouped_dtos.keys():
        grouped_dtos[dto1['ar_id']] = [dto1]
    else:
        grouped_dtos[dto1['ar_id']].append(dto1)

# add the single satisfaction constraints
for ar_id in grouped_dtos.keys():
    model.addConstr(gp.quicksum([dtos_variables[dtos.index(dto_)] for dto_ in grouped_dtos[ar_id]]) <= 1,
                    f"Single_satisfaction_constraint_for_AR_{ar_id}")

# add the taken memory constraints
satellite_memories = [gp.quicksum([memories[i] * dtos_variables[i] for i, dto in enumerate(dtos)
                                   if dto['stop_time'] < dlos[0]['start_time']])]
model.addConstr(satellite_memories[0] <= CAPACITY, f'Memory_constraint_DLO_0')

for j in range(1, DLOS_NUMBER):
    satellite_memories.append(satellite_memories[j - 1] -
                              gp.quicksum([memories[i] * z_ji[j - 1][i] for i in range(DTOS_NUMBER)]) +
                              gp.quicksum([memories[i] * dtos_variables[i] for i, dto in enumerate(dtos)
                                           if dto['start_time'] > dlos[j - 1]['stop_time']
                                           and dto['stop_time'] < dlos[j]['start_time']]))

    model.addConstr(satellite_memories[j] <= CAPACITY, f'Memory_constraint_DLO_{j}')

# # add DTO selected in plan constraint
# for j in range(DLOS_NUMBER):
#     for i in range(DTOS_NUMBER):
#         model.addConstr(z_ji[j][i] <= dtos_variables[i], f'DTO_selected_in_plan_constraint_DLO:{j}_DTO:{i}')
#
# # add single downlink constraint
# for i in range(DTOS_NUMBER):
#     model.addConstr(gp.quicksum([z_ji[j][i] for j in range(DLOS_NUMBER)]) <= 1)

# last two commented constraints can be reduced to the next one (maybe)
for i in range(DTOS_NUMBER):
    model.addConstr(gp.quicksum([z_ji[j][i] for j in range(DLOS_NUMBER)]) <= dtos_variables[i],
                    f'Single_downlink_constraint_and_post_acquisition_for_DTO_{i}')

# add downloaded memory constraint
for j in range(DLOS_NUMBER):
    model.addConstr(gp.quicksum([memories[i] * z_ji[j][i] for i in range(DTOS_NUMBER)]) <=
                    DOWNLINK_RATE * (dlos[j]['stop_time'] - dlos[j]['start_time']),
                    f'Downloaded_memory_constraint_DLO_{j}')

# add time constraint
for j in range(DLOS_NUMBER):
    for i in range(DTOS_NUMBER):
        if dlos[j]['start_time'] < dtos[i]['stop_time']:
            model.addConstr(z_ji[j][i] == 0, f'Time_constraint_for_DTO_{i}_DLO_{j}')

# set objective function to maximize dtos priority
model.setObjective(gp.quicksum([priorities[i] * dtos_variables[i] for i in range(DTOS_NUMBER)]), GRB.MAXIMIZE)

end = time.time()
print("Preparation terminated in ", end - start)

# solve model
print("Solve model...")
start = time.time()

model.optimize()

if model.Status == GRB.INF_OR_UNBD:
    # Turn pre-solve off to determine whether model is infeasible
    # or unbounded
    model.setParam(GRB.Param.Presolve, 0)
    model.optimize()
if model.Status == GRB.OPTIMAL:
    print('Optimal objective: %g' % model.ObjVal)
    print(f'Number of constraints: {len(model.getConstrs())}')
    json_solution = json.loads(model.getJSONSolution())
    print(json_solution)

    # take the DTOs in the plan
    dtos_taken = [dtos[index] for index in range(DTOS_NUMBER) if dtos_variables[index].getAttr("X") == 1]

    # calculate which dtos are downloaded
    dtos_in_memory = []
    dtos_downloaded = []
    for i in range(DTOS_NUMBER):
        downloaded = False
        j = 0
        while j < DLOS_NUMBER and not downloaded:
            if z_ji[j][i].getAttr("X") == 1:
                downloaded = True
                dtos_downloaded.append(dtos[i])
            j = j + 1

    # dtos remained in memory at the end of plan
    dtos_in_memory = [dto for dto in dtos_taken if dto not in dtos_downloaded]
    memories_in_memory = list(map(lambda dto_: dto_['memory'], dtos_in_memory))
    print("Memory occupied:", sum(memories_in_memory))
    print("DTOs left in memory", dtos_in_memory)

    # memories freed during the plan
    freed_memories = []
    for j in range(DLOS_NUMBER):
        freed_memory = 0
        for i in range(DTOS_NUMBER):
            if z_ji[j][i].getAttr("X") == 1:
                freed_memory += dtos[i]['memory']

        freed_memories.append(freed_memory)

    # calculate memories for each activity to plot the memory graph
    activities = dtos_taken + dlos
    activities = sorted(activities, key=lambda activity_: activity_['start_time'])
    tot_memory = 0
    chronology_memories = []
    for activity in activities:
        if "memory" in activity:
            tot_memory += activity['memory']
        else:
            tot_memory -= freed_memories[dlos.index(activity)]

        chronology_memories.append(tot_memory)

    xx = np.arange(len(chronology_memories))
    plt.plot(xx, chronology_memories)
    plt.title('Memory')
    plt.show()

    with open(f'../instances/{INSTANCE}/result.json', 'w') as f:
        json.dump(json_solution, f)

    # with open(f'../instances/{INSTANCE}/result.json') as f:
    #     old_json = json.loads(f.read())
    #     print(old_json['Vars'])
    #     print(json_solution['Vars'])
    #     print(old_json['Vars'] == json_solution['Vars'])

    model.write(f'../instances/{INSTANCE}/model.lp')

elif model.Status != GRB.INFEASIBLE:
    print('Optimization was stopped with status %d' % model.Status)

end = time.time()
print("Solved in ", end - start)
