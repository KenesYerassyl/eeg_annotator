from pathlib import Path

import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QWidget,
    QApplication,
    QFileDialog,
)

from control_frame import ControlToolBar
from eeg_frame import EEGPlotWidget
from eeg_data import EEGData
from app_state import AppState

class EEGAnnotator(QMainWindow):
    """EEG Annotator main window"""

    def __init__(self):
        super(EEGAnnotator, self).__init__()
        self.setWindowTitle("EEG Annotator")
        self.resize(1024, 720)
        
        self.state = AppState()
        self.state.montage_changed.connect(self.load_eeg)
        self.state.filter_changed.connect(self.load_eeg)
        self.state.scale_changed.connect(self.load_eeg)

        self.eeg_data = EEGData()
        self.control_toolbar = ControlToolBar(self.state)
        self.control_toolbar.open_file_clicked.connect(self.open_file)
        self.control_toolbar.save_clicked.connect(self.save_annotation)
        self.eeg_plot_widget = EEGPlotWidget(self.state)

        layout = QHBoxLayout()
        # add toolbar
        self.addToolBar(self.control_toolbar)
        menu = self.menuBar()
        # create an open action
        openAction = QAction("Open", self)
        openAction.triggered.connect(self.open_file)

        # Add the open action to the menu
        fileMenu = menu.addMenu("&File")
        fileMenu.addAction(openAction)

        # add widgets to the layout
        layout.addWidget(self.eeg_plot_widget)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def open_file(self):
        self.eeg_plot_widget.fig.clear()
        file_filters = "*.edf *.EDF"

        self.filename = QFileDialog.getOpenFileName(self, filter=file_filters)[0]

        if not self.filename:
            return

        self.filename = Path(self.filename)
        self.eeg_data.load_edf(self.filename, self.state.filter, self.state.montage)
        self.load_eeg()

    def load_eeg(self):
        if hasattr(self, 'filename') and self.filename is not None:
            work_dir = self.filename.parent
            eeg_file_name = self.filename.stem
            annotation = []

            annotation_file_path = work_dir / f"{eeg_file_name}_{self.state.montage.replace(' ', '_')}.csv"

            if annotation_file_path.exists():
                df = pd.read_csv(annotation_file_path)
                annotation = df.to_dict(orient="records")
                annotation.sort(key=lambda a: (a['start_time'], a['stop_time'], a['onset']))

                merged_annotation = []
                current_channel_label = {
                    'channels': [annotation[0]['channels']],
                    'start_time': annotation[0]['start_time'],
                    'stop_time': annotation[0]['stop_time'],
                    'onset': annotation[0]['onset']
                }
                for channel_id in range(1, len(annotation)):
                    label = annotation[channel_id]
                    if current_channel_label['start_time'] == label['start_time'] and \
                        current_channel_label['stop_time'] == label['stop_time'] and \
                        current_channel_label['onset'] == label['onset']:
                        current_channel_label['channels'].append(label['channels'])
                    else:
                        merged_annotation.append(current_channel_label)
                        current_channel_label = {
                            'channels': [label['channels']],
                            'start_time': label['start_time'],
                            'stop_time': label['stop_time'],
                            'onset': label['onset']
                        }
                merged_annotation.append(current_channel_label)
                annotation = merged_annotation

            self.eeg_data.load_view(self.state.filter, self.state.montage)
            self.state.set_montage_list(self.eeg_data.raw_view.ch_names)

            signal_duration = self.eeg_data.get_duration()
            s_freq = self.eeg_data.get_s_freq()

        if self.eeg_data.raw_view:
            self.control_toolbar.label_btn.setEnabled(True)
            self.control_toolbar.save_btn.setEnabled(True)
            self.control_toolbar.show_controls(signal_duration, s_freq)

            # set the annotation
            self.eeg_plot_widget.annotation = annotation
            self.eeg_plot_widget.show_plot(self.eeg_data.raw_view, signal_duration, self.state.scale)
            self.eeg_plot_widget.render_saved_annotations()

    def save_annotation(self):
        if not len(self.eeg_plot_widget.annotation):
            return
        
        work_dir = self.filename.parent
        eeg_file_name = self.filename.stem
        annotation_file_path = work_dir / f"{eeg_file_name}_{self.state.montage.replace(' ', '_')}.csv"
        csv_rows = []

        for annotation in self.eeg_plot_widget.annotation:
            for channel in annotation['channels']:
                csv_rows.append({
                    'channels': channel,
                    'start_time': annotation['start_time'],
                    'stop_time': annotation['stop_time'],
                    'onset': annotation['onset'],
                })
        df = pd.DataFrame(csv_rows, columns=["channels", "start_time", "stop_time", "onset"])
        df.to_csv(annotation_file_path, index=False)

if __name__ == "__main__":
    app = QApplication([])
    window = EEGAnnotator()
    window.show()

    app.exec()
