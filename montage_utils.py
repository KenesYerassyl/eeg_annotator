import os
import yaml
from path_utils import resource_path

class MontageController:

    def __init__(self):
        self.montages_path = resource_path('montages')
        self.montage_types = [entry.name.replace('.yaml', '').replace('_', ' ').upper() for entry in os.scandir(self.montages_path)]
        self.montages = {}

        for montage_type in self.montage_types:
            self.montages[montage_type] = self._load_montage(montage_type)

    def _load_montage(self, montage_type):
        montage_type = montage_type.replace(' ', '_').lower() + '.yaml'
        montage_path = os.path.join(self.montages_path, montage_type)
        with open(montage_path, 'r') as file:
            data = yaml.safe_load(file)
        return data
    
    def get_montage(self, montage_type):
        if montage_type in self.montages:
            return self.montages[montage_type]
        else:
            raise KeyError("Non-existent montage type")
    
montage_controller = MontageController()