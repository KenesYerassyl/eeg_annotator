from pathlib import Path
from typing import Union, Tuple, Optional

import mne
from montage_utils import montage_controller

class EEGData:
    def __init__(self):
        self._reset_attrs()
    
    def _reset_attrs(self):
        self.raw_base: mne.io.Raw = None
        self.raw_view: mne.io.Raw = None
        self.filter: Tuple[Optional[float], Optional[float]] = None
        self.current_montage: str = None

    def load_edf(self, filename: Union[str, Path], filter: Tuple[Optional[float], Optional[float]], current_montage: str) -> None:
        self._reset_attrs()
        self.raw_base = mne.io.read_raw_edf(filename, preload=True, verbose=False)
        self.load_view(filter, current_montage)
    
    def load_view(self, filter: Tuple[Optional[float], Optional[float]], current_montage: str) -> None:
        if self.filter == filter and self.current_montage == current_montage:
            return self.raw_view
        
        self.raw_view = None

        if current_montage.startswith('BIPOLAR'):
            montage = montage_controller.get_montage(current_montage)
            ch_name, anode, cathode = [], [], []
            
            for k, v in montage.items():
                ch_name.append(k)
                anode.append(v[0])
                cathode.append(v[1])
            self.raw_view = mne.set_bipolar_reference(
                self.raw_base,
                anode=anode,
                cathode=cathode,
                ch_name=ch_name,
                drop_refs=True,
                copy=True,
                verbose=False,
            )
            self.raw_view.pick(ch_name)
        else:
            self.raw_view = self.raw_base.copy()
        try:
            self.raw_view.filter(l_freq=filter[0], h_freq=filter[1], verbose=False)
        except:
            pass
        self.filter = filter
        self.current_montage = current_montage
    
    def get_s_freq(self) -> float:
        return self.raw_view.info['sfreq']
    
    def get_duration(self) -> float:
        s_freq = self.get_s_freq()
        signal_length = self.raw_view.get_data().shape[-1]

        return signal_length / s_freq