import sys
from PyQt6.QtWidgets import QApplication
from ui import EditorTagu
from audio_manager import AudioManager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    audio_manager = AudioManager()
    window = EditorTagu(audio_manager)
    window.show()
    sys.exit(app.exec())
