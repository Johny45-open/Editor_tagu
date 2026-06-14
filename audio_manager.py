from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl
from accessible_output2.outputs.auto import Auto

class AudioManager:
    def __init__(self):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.speaker = Auto()

    def speak(self, text):
        self.speaker.speak(text)

    def play(self, file_path):
        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.player.play()
