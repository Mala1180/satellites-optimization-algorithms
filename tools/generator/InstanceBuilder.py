import datetime
import json
import math
import os
from pathlib import Path
from random import randint, randrange

import numpy as np

from .Instance import Instance


class InstanceBuilder:

    def __init__(self, name: str):
        """
        Initializes the instance builder
        :param name: the name of the instance
        """
        if name is None or not isinstance(name, str):
            raise ValueError("Wrong name parameter, must be a string")
        self.name = name
        self.instance = Instance()

    def generate_constants(self, memory_cap: float, downlink_rate: float):
        """ Generates the constants of the instance (memory_cap and downlink_rate) """
        self.instance.constants = {'MEMORY_CAP': memory_cap, 'DOWNLINK_RATE': downlink_rate}
        return self

    def generate_ars_and_dtos(self, ars_length: int, dto_per_ar: int, variance: float, max_memory: float,
                              max_rank: int):
        """
        Generates the DTOs of the instance
        :param ars_length: number of ARs to generate
        :param dto_per_ar: number of DTOs per AR on average
        :param variance: index of the variance of the DTOs per AR
        :param max_memory: the maximum memory a DTO can have
        :param max_rank: the maximum priority a DTO can have (AR rank)
        """
        mu, sigma = dto_per_ar, math.sqrt(variance)  # mean and standard deviation
        num_dto_per_ar = np.random.normal(mu, sigma, ars_length)

        print(num_dto_per_ar, len(num_dto_per_ar))

        start_plan = datetime.datetime.today()
        end_plan = start_plan + datetime.timedelta(hours=2)
        time_between_dates = end_plan - start_plan

        counter_id: int = 0
        for i, num_dtos in enumerate(num_dto_per_ar):
            self.instance.ars.append({"id": i, "rank": randint(0, max_rank)})

            for j in range(int(num_dtos)):
                random_start_date = start_plan + datetime.timedelta(seconds=randrange(time_between_dates.seconds))
                random_end_date = random_start_date + datetime.timedelta(seconds=randrange(120))
                self.instance.dtos.append({"id": counter_id, "ar_id": i,
                                           "start_time": random_start_date.timestamp(),
                                           "stop_time": random_end_date.timestamp(),
                                           "memory": max_memory})
                counter_id += 1

        self.instance.constants['NUM_DTOS'] = len(self.instance.dtos)
        self.instance.constants['NUM_ARS'] = ars_length
        return self

    def generate_paws(self, length: int):
        """
        Generates the PAWs of the instance
        :param length: number of PAWs to generate
        """
        for i in range(length):
            self.instance.paws.append({"id": i, "start_time": 418257802.937371, "stop_time": 418257822.937371})
        self.instance.constants['NUM_PAWS'] = length
        return self

    def generate_dlos(self, length: int):
        """
        Generates the DLOs of the instance
        :param length: number of DLOs to generate
        """
        start_plan = datetime.datetime.today()
        end_plan = start_plan + datetime.timedelta(hours=2)
        time_between_dates = end_plan - start_plan
        for i in range(length):
            random_start_date = start_plan + datetime.timedelta(seconds=randrange(time_between_dates.seconds))
            random_end_date = random_start_date + datetime.timedelta(seconds=randrange(100))
            self.instance.dlos.append({"id": i,
                                       "start_time": random_start_date,
                                       "stop_time": random_end_date})
        self.instance.constants['NUM_DLOS'] = length
        return self

    def get_instance(self) -> Instance:
        return self.instance

    def save_instance(self):
        """ Saves the instance to a directory named as the instance """
        root_directory = Path(__file__).absolute().parent.parent.parent
        path = os.path.join(f'{root_directory}/instances', self.name)
        if not os.path.exists(path):
            os.makedirs(path)

        with open(f'{path}/constants.json', 'w') as f:
            json.dump(self.instance.constants, f)

        with open(f'{path}/ARs.json', 'w') as f:
            json.dump(self.instance.ars, f)

        with open(f'{path}/DTOs.json', 'w') as f:
            json.dump(self.instance.dtos, f)

        with open(f'{path}/PAWs.json', 'w') as f:
            json.dump(self.instance.paws, f)

        with open(f'{path}/DLOs.json', 'w') as f:
            json.dump(self.instance.dlos, f)
