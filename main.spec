# -*- mode: python ; coding: utf-8 -*-

"""Optimized PyInstaller spec for Ziyatron EEG Annotator.

Key optimizations:
- Selective MNE imports (not collect_all) - saves 300-400MB
- Excludes matplotlib and dependencies - saves 50-80MB
- Excludes unused PyQt6 modules - saves 100-180MB
- Enables strip and UPX compression
- Expected bundle size: 150-200MB (vs 500-600MB before)
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import sys

# ===== SELECTIVE MNE DATA COLLECTION =====
# Only include necessary MNE data, exclude tests/examples/datasets
mne_data = collect_data_files(
    'mne',
    excludes=[
        '**/tests/**',
        '**/examples/**',
        '**/datasets/**',
        '**/sample_data/**',
        '**/__pycache__/**',
        '**/*.pyc',
    ]
)

# Collect ALL MNE submodules as hidden imports.
# MNE uses lazy_loader extensively — PyInstaller can't detect these imports.
# Only adds ~9MB of .py files (the large data/tests are excluded above).
mne_imports = collect_submodules('mne')

# PyQtGraph hidden imports
pyqtgraph_imports = [
    'pyqtgraph.graphicsItems',
    'pyqtgraph.widgets',
]

# ===== DATA FILES =====
datas = [
    ('resources/icons', 'resources/icons'),
    ('resources/montages', 'resources/montages'),
] + mne_data

# ===== EXCLUSIONS =====
# Exclude packages we don't use to reduce bundle size
excludes = [
    # Matplotlib and dependencies (replaced with PyQtGraph)
    'matplotlib',
    'matplotlib.backends',
    'matplotlib.pyplot',
    'mpl_toolkits',
    'matplotlib.testing',
    'matplotlib.tests',

    # Matplotlib dependencies
    'kiwisolver',
    'cycler',
    'fonttools',
    'contourpy',

    # Unused image libraries
    'PIL',
    'Pillow',

    # Development and testing tools
    'IPython',
    'jupyter',
    'notebook',
    'nbconvert',
    'pytest',
    'sphinx',
    'docutils',

    # Unused stdlib modules
    'tkinter',
    'turtle',
    'unittest',
    'distutils',
    'setuptools',
    'pip',

    # Large unused PyQt6 modules
    'PyQt6.QtWebEngine',
    'PyQt6.QtWebEngineCore',
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.Qt3D',
    'PyQt6.Qt3DCore',
    'PyQt6.Qt3DRender',
    'PyQt6.QtMultimedia',
    'PyQt6.QtMultimediaWidgets',
    'PyQt6.QtQuick',
    'PyQt6.QtQml',
    'PyQt6.QtBluetooth',
    'PyQt6.QtNfc',
    'PyQt6.QtPositioning',
    'PyQt6.QtLocation',
]

# ===== ANALYSIS =====
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=mne_imports + pyqtgraph_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Additional binary filtering to remove excluded Qt modules
# (in case they slip through despite excludes)
excluded_binaries = ['Qt3D', 'QtWebEngine', 'QtMultimedia', 'QtQml', 'QtQuick']
a.binaries = [
    (name, path, type_)
    for name, path, type_ in a.binaries
    if not any(excl in name for excl in excluded_binaries)
]

# ===== PYZ (Python ZIP) =====
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None
)

# ===== EXE =====
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='eeg_annotator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Strip debug symbols (ENABLED for size reduction)
    upx=True,    # UPX compression
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# ===== COLLECT =====
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,  # Strip binaries (ENABLED for size reduction)
    upx=True,    # UPX compression
    upx_exclude=[],
    name='eeg_annotator',
)
