"""Montage configuration manager for EEG channel setups."""
import os
import yaml
from src.utils.path_utils import resource_path


class MontageManager:
    """Manages loading and accessing EEG montage configurations from YAML files."""

    def __init__(self):
        self.montages_path = resource_path('resources/montages')
        self.montage_types = [
            entry.name.replace('.yaml', '').replace('_', ' ').upper()
            for entry in os.scandir(self.montages_path)
            if entry.name.endswith('.yaml')
        ]
        self.montages = {}

        for montage_type in self.montage_types:
            self.montages[montage_type] = self._load_montage(montage_type)

    def _load_montage(self, montage_type: str) -> dict:
        """Load montage configuration from YAML file.

        Args:
            montage_type: Name of montage (e.g., 'BIPOLAR DOUBLE BANANA')

        Returns:
            Dictionary mapping channel names to electrode pairs
        """
        montage_filename = montage_type.replace(' ', '_').lower() + '.yaml'
        montage_path = os.path.join(self.montages_path, montage_filename)

        with open(montage_path, 'r') as file:
            data = yaml.safe_load(file)
        return data

    def get_montage(self, montage_type: str) -> dict:
        """Get montage configuration by name.

        Args:
            montage_type: Name of montage

        Returns:
            Montage configuration dictionary

        Raises:
            KeyError: If montage type doesn't exist
        """
        if montage_type in self.montages:
            return self.montages[montage_type]
        else:
            raise KeyError(f"Non-existent montage type: {montage_type}")


# Global singleton instance
montage_manager = MontageManager()
