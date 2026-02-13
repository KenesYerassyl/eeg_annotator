# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Ziyatron EEG Annotator v2.0** - A high-performance desktop GUI application for neurophysiologists to view, analyze, and annotate EEG (electroencephalogram) data from EDF files. Built with PyQt6 and PyQtGraph, optimized for memory efficiency (10x improvement over v1.0).

## Common Commands

### Running the Application
```bash
# Run from source (always use from project root)
python main.py

# NOT: python src/main.py (will fail with import errors)
```

### Testing
```bash
# Install dev dependencies first
pip install -r requirements-dev.txt

# Run all tests
pytest tests/

# Run with coverage report
pytest --cov=src tests/

# Memory profiling
python -m memory_profiler src/main.py
# Expected: <50MB RAM usage with 100MB EDF file
```

### Building Executables
```bash
# Build locally with PyInstaller
pyinstaller main.spec

# Executable location: dist/eeg_annotator/

# Check bundle size (should be <200MB)
du -sh dist/eeg_annotator/  # macOS/Linux
```

### Code Quality
```bash
# Format code
black src/

# Lint code
flake8 src/
```

### Deployment
```bash
# Trigger automated builds via GitHub Actions
git tag v2.0.1
git push origin v2.0.1

# Builds Windows and macOS executables automatically
# Uploads to GitHub Releases with release notes
```

## Architecture Overview

### Design Philosophy
- **Lazy Loading**: Only loads 6-10 second windows of EEG data, not entire files
- **Memory Efficiency**: 30-50MB RAM for 100MB EDF files (vs 400-500MB in v1.0)
- **Performance**: PyQtGraph provides 10x faster rendering than Matplotlib
- **MVC-inspired**: Clear separation between Models (state), Views (UI), and Core (business logic)

### Module Organization

```
src/
├── main.py                      # Application bootstrap
├── models/
│   └── app_state.py            # Centralized state management with Qt signals
├── views/
│   ├── main_window.py          # Main window orchestration
│   ├── plot_widget.py          # PyQtGraph-based EEG visualization
│   └── control_toolbar.py      # User controls (file, montage, filter, scale)
├── core/
│   ├── data_streamer.py        # Lazy-loading EEG data with LRU cache
│   ├── montage_manager.py      # YAML-based montage configuration
│   └── config.py               # App configuration (diagnosis labels)
└── utils/
    └── path_utils.py           # Resource path resolution (dev vs PyInstaller)
```

### Key Data Flow Patterns

**File Loading:**
```
User clicks "Open" → open_file()
  → EEGPlotWidget.load_edf_file()
    → EEGDataStreamer.open_edf()     [opens handle with preload=False]
    → get_window(start=0, duration=10) [loads only first 10s]
    → update_plot()
```

**Lazy Loading (Pan/Zoom):**
```
User pans plot → sigRangeChanged signal
  → on_view_range_changed()
    → data_streamer.get_window(new_range) [loads new window from LRU cache or disk]
    → update_plot()
```

**State Changes:**
```
User changes montage/filter → ControlToolbar emits signal
  → AppState updates and emits montage_changed/filter_changed
    → MainWindow.on_settings_changed()
      → data_streamer.clear_cache()  [cache invalidation]
      → reload current window with new settings
```

### Signal/Slot Architecture (Qt)

**AppState signals:**
- `montage_changed` → triggers data reload
- `filter_changed` → triggers data reload
- `scale_changed` → updates plot Y-axis scaling
- `label_clicked` → enables annotation selection mode
- `undo_clicked` → removes last annotation
- `goto_input_return_pressed` → jumps to specific time
- `spinner_value_changed` → changes display window duration

### Critical Implementation Details

**Lazy Loading (data_streamer.py):**
- Uses `mne.io.read_raw_edf(preload=False)` to avoid loading entire file
- LRU cache with max 5 windows (configurable via `MAX_CACHE_SIZE`)
- Cache key: `(start_time, duration, montage_name, filter_tuple)`
- Loads windows with 2-second buffer for smooth panning
- Cache cleared when settings change (montage/filter)

**PyQtGraph Optimization (plot_widget.py):**
- `downsample=10` reduces point density when zoomed out
- `clipToView=True` only renders visible region
- No full redraws on pan/zoom (unlike Matplotlib)
- `_scale_constant = 0.00001` controls vertical channel spacing

**Montage System:**
- YAML files in `resources/montages/` define electrode pairs
- Format: `{channel_name}: [electrode1, electrode2]`
- Example: `FP1-F7: ['FP1', 'F7']` for bipolar montage
- "AVERAGE" montage uses average reference instead of pairs
- MontageManager dynamically loads all YAMLs at startup

**Annotation Persistence:**
- Saves as CSV: `{edf_filename}_{montage}.csv`
- Format: `channels,start_time,stop_time,onset`
- Multi-channel annotations expanded to one row per channel
- Backward compatible with v1.0 annotations

### PyInstaller Bundle Optimization

**Key exclusions in main.spec:**
- Matplotlib and dependencies (replaced with PyQtGraph) - saves ~80MB
- Unused PyQt6 modules (WebEngine, Multimedia, 3D) - saves ~180MB
- MNE tests/examples/datasets - saves ~400MB
- Strip and UPX compression enabled
- Result: 150MB bundle vs 500MB in v1.0

**Resource path handling:**
- `path_utils.py` uses `sys._MEIPASS` for PyInstaller bundles
- Always use `resource_path()` for accessing `resources/` folder

## Development Guidelines

### Adding New Features

**New Diagnosis Label:**
Edit `src/core/config.py` and add to the `diagnosis` list.

**New Montage:**
Create YAML file in `resources/montages/my_montage.yaml`:
```yaml
CH1-CH2: ['CH1', 'CH2']
CH2-CH3: ['CH2', 'CH3']
```
Will automatically appear in montage dropdown.

**New Control Widget:**
1. Add widget to `ControlToolbar` class
2. Create signal in `AppState`
3. Emit signal from toolbar
4. Connect signal in `MainWindow` to handler

**Modify Memory Behavior:**
In `src/core/data_streamer.py`:
- Adjust `MAX_CACHE_SIZE` (default: 5 windows)
- Modify `buffer_seconds` in `get_window()` (default: 2.0)

### Important Constraints

**Entry Point:**
- Always run `python main.py` from project root
- Never run `python src/main.py` (import paths will break)
- `main.py` wrapper adds `src/` to Python path

**Memory Management:**
- Never use `preload=True` when opening EDF files
- Always invalidate cache (`clear_cache()`) when settings change
- Keep window duration small (6-10 seconds recommended)

**UI Threading:**
- EEG data loading happens on main thread (consider threading for very large files)
- Qt signals/slots handle all cross-component communication

**Logging:**
- Application logs to `eeg_annotator.log` and console
- Use `logging.getLogger(__name__)` in new modules

### Testing Notes

**Manual Testing Checklist:**
- Load 100MB+ EDF file and verify <50MB RAM usage
- Pan/zoom should be smooth (<50ms response)
- Test all montages load correctly
- Verify filter changes update display
- Annotation save/load with correct CSV format

**Memory Leak Detection:**
Run with memory profiler and check:
- Opening files doesn't accumulate memory
- Changing settings clears cache properly
- Annotations don't leak when creating/removing

### GitHub Actions CI/CD

**Workflow (`.github/workflows/build.yml`):**
- Triggers on version tags (`v*`) or manual dispatch
- Builds on Windows and macOS with Python 3.10
- Runs PyInstaller with `main.spec`
- Creates ZIP archives
- Uploads to GitHub Releases with auto-generated notes
- Build time: ~10-15 minutes per platform

**To deploy a new version:**
```bash
git tag v2.0.1
git push origin v2.0.1
# Wait for GitHub Actions to complete
# Download from Releases page
```

## Key File References

- Entry point: `main.py:10` (imports from `src/main.py`)
- Application bootstrap: `src/main.py:20-32`
- Main window orchestration: `src/views/main_window.py`
- Lazy loading implementation: `src/core/data_streamer.py:40-100` (get_window)
- Plot rendering: `src/views/plot_widget.py` (EEGPlotWidget class)
- State management: `src/models/app_state.py` (Qt signals)
- Configuration: `src/core/config.py:8-54` (diagnosis labels)
- PyInstaller spec: `main.spec:16-50` (optimization settings)

## Common Pitfalls

1. **Import errors**: Always run from project root, not from `src/`
2. **Memory issues**: Don't use `preload=True`, keep cache size reasonable
3. **Bundle bloat**: Don't import matplotlib or unused PyQt6 modules
4. **Cache invalidation**: Clear cache when montage/filter changes
5. **Resource paths**: Use `path_utils.resource_path()` for resources, not hardcoded paths
