# Ziyatron EEG Annotator v2.0

High-performance EEG annotation tool for neuro-physicians, optimized for low-memory environments (4-8GB RAM laptops).

## 🚀 Quick Start

### Running from Source

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Building Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build with optimized spec
pyinstaller main.spec

# Executable will be in: dist/eeg_annotator/
```

### Using GitHub Actions

1. Push a version tag:
   ```bash
   git tag v2.0.0
   git push origin v2.0.0
   ```

2. GitHub Actions automatically builds Windows + macOS versions

3. Download builds from GitHub Releases

---

## 📁 Project Structure

```
eeg_annotator/
├── .github/
│   └── workflows/
│       └── build.yml              # CI/CD pipeline
├── src/
│   ├── main.py                    # Application entry point
│   ├── core/
│   │   ├── config.py              # Configuration (labels, settings)
│   │   ├── data_streamer.py       # Lazy loading EEG data manager
│   │   └── montage_manager.py     # Montage configuration loader
│   ├── models/
│   │   └── app_state.py           # Application state with Qt signals
│   ├── views/
│   │   ├── main_window.py         # Main application window
│   │   ├── plot_widget.py         # PyQtGraph plotting widget
│   │   └── control_toolbar.py     # Control toolbar UI
│   └── utils/
│       └── path_utils.py          # Resource path resolution
├── resources/
│   ├── icons/                     # Application icons
│   └── montages/                  # EEG montage configurations
│       ├── average.yaml
│       ├── bipolar_double_banana.yaml
│       └── bipolar_transverse.yaml
├── tests/
│   ├── test_data_streamer.py      # Unit tests
│   └── test_plot_widget.py
├── main.py                        # Entry point wrapper
├── main.spec                      # PyInstaller configuration
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
└── README.md
```

---

## 🔧 Architecture

### Lazy Loading Data Streamer

The `EEGDataStreamer` class implements memory-efficient lazy loading:

```python
# OLD (loads entire file into RAM):
raw = mne.io.read_raw_edf(filename, preload=True)  # 100MB → 500MB RAM

# NEW (loads only visible windows):
streamer.open_edf(filename)  # preload=False
window = streamer.get_window(start=0, duration=10)  # Only 10s → 2MB RAM
```

**Benefits:**
- Only loads 6-10 second windows (not entire file)
- LRU cache with max 5 windows (~20-40MB total)
- Applies montage/filter on small windows only
- Supports files up to 1GB+

### PyQtGraph Rendering

```python
# Automatic downsampling when zoomed out
curve = plot_widget.plot(
    downsample=10,           # Reduces point density
    clipToView=True,         # Only renders visible region
    autoDownsampleFactor=5.0 # Adjusts by zoom level
)
```

**Benefits:**
- Native Qt integration (no QtAgg bridge)
- GPU acceleration via OpenGL (optional)
- Real-time pan/zoom without full redraws
- Efficient for time-series data

### Optimized PyInstaller Bundle

[main.spec](main.spec) uses selective imports and exclusions:

```python
# Exclude bloat
excludes = [
    'PyQt6.QtWebEngine',   # 100MB, unused
    'mne/tests/**',        # Test data
    # ... (see full list in main.spec)
]
```

**Result:** 500MB → 150MB bundle size

---

## 🎯 Features

### EEG Viewing
- ✅ Load EDF files (100MB+)
- ✅ Multiple montage support (Average, Bipolar Double Banana, Bipolar Transverse)
- ✅ Adjustable scale (1-1000 µV/mm)
- ✅ Frequency filtering (low-pass, high-pass)
- ✅ Pan with arrow keys or mouse
- ✅ Zoom with spinner control
- ✅ Goto specific time

### Annotation
- ✅ Rectangle selection for time/channel ranges
- ✅ 54 pre-defined diagnosis labels (AR, BR, SEIZ, etc.)
- ✅ Multi-channel annotation support
- ✅ Undo functionality

### File Format

Annotations are saved as CSV: `{filename}_{montage}.csv`


| channels | start_time | stop_time | onset |
|----------|------------|-----------|-------|
| FP1-F7 | 10 | 15 | SEIZ |
| F7-T3 | 10 | 15 | SEIZ |
| T3-T5 | 10 | 15 | SEIZ |

---

## 🧪 Testing

### Run Unit Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

### Performance Testing

```bash
# Memory profiling
python -m memory_profiler src/main.py

# Expected: <50MB RAM usage with 100MB EDF file
```

### Bundle Size Testing

```bash
# Build and check size
pyinstaller main.spec
du -sh dist/eeg_annotator/

# Expected: <200MB
```

---

## 🚢 Deployment

### GitHub Actions Workflow

The `.github/workflows/build.yml` automatically builds executables when you push a version tag:

```bash
# Create and push a version tag
git tag v2.0.0
git push origin v2.0.0

# GitHub Actions will:
# 1. Build Windows and macOS executables
# 2. Run tests
# 3. Create ZIP archives
# 4. Upload to GitHub Releases
# 5. Add release notes
```

**Build time:** ~3-5 minutes per platform

### Manual Deployment

```bash
# Build locally
pyinstaller main.spec

# Test the executable
dist/eeg_annotator/eeg_annotator

# Create ZIP for distribution
cd dist
zip -r eeg_annotator.zip eeg_annotator/
```

---

## 📝 Development

### Adding New Diagnosis Labels

Edit [src/core/config.py](src/core/config.py):

```python
diagnosis = [
    'AR', 'BR', 'SEIZ',
    'YOUR_NEW_LABEL',  # Add here
    # ...
]
```

### Adding New Montages

Create YAML file in [resources/montages/](resources/montages/):

```yaml
# resources/montages/my_montage.yaml
CH1-CH2: ['CH1', 'CH2']
CH2-CH3: ['CH2', 'CH3']
# ...
```

The montage will automatically appear in the dropdown.

### Modifying Lazy Loading Behavior

Edit [src/core/data_streamer.py](src/core/data_streamer.py):

```python
# Adjust cache size
MAX_CACHE_SIZE = 10  # Default: 5

# Adjust buffer for smooth panning
buffer_seconds = 5.0  # Default: 2.0
```

---

## 🐛 Troubleshooting

### Import Errors

If you see `ModuleNotFoundError: No module named 'src'`:

```bash
# Make sure you're running from the project root
cd /path/to/eeg_annotator
python main.py  # NOT python src/main.py
```

### Memory Issues

If still experiencing memory issues:

1. Reduce cache size in `data_streamer.py` (line 30)
2. Reduce window duration (use 5s instead of 10s)
3. Check for memory leaks with `memory_profiler`

### Build Failures

If PyInstaller build fails:

1. Check Python version (requires 3.10)
2. Update PyInstaller: `pip install --upgrade pyinstaller`
3. Try without optimizations first (comment out `excludes` in main.spec)
4. Check logs in `build/eeg_annotator/warn-eeg_annotator.txt`

### GitHub Actions Failures

If builds fail on GitHub Actions:

1. Check Python version in `.github/workflows/build.yml`
2. Ensure `requirements.txt` is up to date
3. Check action logs for specific error messages
4. Test build locally first: `pyinstaller main.spec`

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/eeg_annotator.git
cd eeg_annotator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run application
python main.py
```

### Code Style

- Use `black` for formatting: `black src/`
- Use `flake8` for linting: `flake8 src/`
- Follow PEP 8 guidelines
- Add docstrings to public functions

---

## 👏 Acknowledgments

Built with:
- [MNE-Python](https://mne.tools/) - EEG data processing
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [PyQtGraph](https://www.pyqtgraph.org/) - High-performance plotting
- [PyInstaller](https://pyinstaller.org/) - Executable bundling

---

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/eeg_annotator/issues)
- Email: kenesyerassyl@gmail.com

---

**Version:** 2.0.0
**Author:** Kenes Yerassyl
**Last Updated:** 2026-02-09
