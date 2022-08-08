import json
import os
from datetime import datetime, timedelta
from pathlib import Path


class Instance:

    def __init__(self, name: str, start: datetime, duration: timedelta):
        """
        Initializes the problem instance
        :param name: the name of the instance
        """
        self.name = name
        self.start = start
        self.end = self.start + duration
        self.time_between_dates = self.end - self.start
        print(f'start {start} \n end: {self.end} \n time between: {self.time_between_dates}')
        self.dtos = []
        self.ars = []
        self.constants = {}
        self.paws = []
        self.dlos = []

    def get_dtos(self):
        return self.dtos

    def get_ars(self):
        return self.ars

    def get_constants(self):
        return self.constants

    def get_paws(self):
        return self.paws

    def get_dlos(self):
        return self.dlos

    def save(self):
        """ Saves the instance to a directory named as the instance """
        root_directory = Path(__file__).absolute().parent.parent.parent
        path = os.path.join(f'{root_directory}/instances', self.name)
        if not os.path.exists(path):
            os.makedirs(path)

        with open(f'{path}/constants.json', 'w') as f:
            json.dump(self.constants, f)

        with open(f'{path}/ARs.json', 'w') as f:
            json.dump(self.ars, f)

        with open(f'{path}/DTOs.json', 'w') as f:
            json.dump(self.dtos, f)

        with open(f'{path}/PAWs.json', 'w') as f:
            json.dump(self.paws, f)

        with open(f'{path}/DLOs.json', 'w') as f:
            json.dump(self.dlos, f)

        print("Instance generated")