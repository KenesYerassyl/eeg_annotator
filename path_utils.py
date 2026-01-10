import sys
from typing import Union
from pathlib import Path

def resource_path(relative_path: Path, to_string: bool = False) -> Union[Path, str]:
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent

    final_path = base_path / relative_path

    if to_string:
        return str(final_path)

    return final_path