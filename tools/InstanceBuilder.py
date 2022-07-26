import json
import os
from math import floor
from pathlib import Path
from random import randint

from tools.Instance import Instance


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

    # def generate_ars(self, length: int, max_rank: int):
    #     """
    #     Generates the ARs of the instance
    #     :param length: number of ARs to generate
    #     :param max_rank: the maximum rant an AR can have
    #     """
    #     for i in range(length):
    #         self.instance.ars.append({"id": i, "rank": randint(0, max_rank)})
    #     self.instance.constants['NUM_ARS'] = length
    #     return self

    def generate_dtos(self, length: int, max_memory: float, ar_percentage: float, max_rank: int):
        """
        Generates the DTOs of the instance
        :param length: number of DTOs to generate
        :param max_memory: the maximum memory a DTO can have
        :param max_rank: the maximum priority a DTO can have (AR rank)
        :param ar_percentage: percentage of ARs respect to DTOs
        """
        ars_length: int = floor(length * ar_percentage)
        for i in range(length):
            if i < ars_length:
                self.instance.ars.append({"id": i, "rank": randint(0, max_rank)})
                ar_id = i
            else:
                ar_id = randint(0, ars_length)
            self.instance.dtos.append({"id": i, "ar_id": ar_id, "start_time": 418257802.937371,
                                       "stop_time": 418257822.937371, "memory": max_memory})
        self.instance.constants['NUM_DTOS'] = length
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
        for i in range(length):
            self.instance.dlos.append({"id": i, "start_time": 418257802.937371, "stop_time": 418257822.937371})
        self.instance.constants['NUM_DLOS'] = length
        return self

    def get_instance(self) -> Instance:
        return self.instance

    def save_instance(self):
        """ Saves the instance to a directory named as the instance """
        root_directory = Path(__file__).absolute().parent.parent
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
