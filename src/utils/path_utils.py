import sys
from typing import Union
from pathlib import Path

def resource_path(relative_path: Path, to_string: bool = False) -> Union[Path, str]:
    """Get path to resource file, handling both development and PyInstaller bundle.

    Args:
        relative_path: Path relative to project root (e.g., 'resources/icons/file.png')
        to_string: If True, return string instead of Path object

    Returns:
        Absolute path to resource
    """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller bundle - resources are in _MEIPASS
        base_path = Path(sys._MEIPASS)
    else:
        # Development - go up two levels from src/utils/ to project root
        base_path = Path(__file__).resolve().parent.parent.parent

    final_path = base_path / relative_path

    if to_string:
        return str(final_path)

    return final_path