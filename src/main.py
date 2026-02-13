"""Entry point for EEG Annotator application."""
import sys
import logging
from PyQt6.QtWidgets import QApplication

from src.views.main_window import EEGAnnotator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eeg_annotator.log'),
        logging.StreamHandler()
    ]
)


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("Ziyatron EEG Annotator")
    app.setOrganizationName("Ziyatron")
    app.setApplicationVersion("2.0.0")

    window = EEGAnnotator()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
