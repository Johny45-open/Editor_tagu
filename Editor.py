import sys
import os
import pygame
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QDialog, QLineEdit, QFormLayout, QHBoxLayout
)
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

class TagDialog(QDialog):
    def __init__(self, tags=None):
        super().__init__()
        self.setWindowTitle("Editace tagů")
        self.resize(350, 180)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        form_layout = QFormLayout()
        self.layout.addLayout(form_layout)

        # pole pro různé tagy
        self.title_edit = QLineEdit(tags.get("title", ""))
        form_layout.addRow("Název:", self.title_edit)

        self.artist_edit = QLineEdit(tags.get("artist", ""))
        form_layout.addRow("Autor:", self.artist_edit)

        self.album_edit = QLineEdit(tags.get("album", ""))
        form_layout.addRow("Album:", self.album_edit)

        self.comment_edit = QLineEdit(tags.get("comment", ""))
        form_layout.addRow("Komentář:", self.comment_edit)

        # tlačítka OK a Zrušit
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Zrušit")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.layout.addLayout(btn_layout)

    def get_tags(self):
        return {
            "title": self.title_edit.text(),
            "artist": self.artist_edit.text(),
            "album": self.album_edit.text(),
            "comment": self.comment_edit.text()
        }


class EditorTagu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor tagů – přehrávač + víc tagů")
        self.resize(400, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        pygame.mixer.init()

        self.label_file = QLabel("Žádný soubor vybrán")
        self.layout.addWidget(self.label_file)

        self.load_btn = QPushButton("Vybrat MP3 soubor")
        self.load_btn.clicked.connect(self.load_file)
        self.layout.addWidget(self.load_btn)

        self.label_play = QLabel("Zvuk nebyl přehrán")
        self.layout.addWidget(self.label_play)

        self.play_btn = QPushButton("Přehrát")
        self.play_btn.clicked.connect(self.play_sound)
        self.layout.addWidget(self.play_btn)

        self.edit_tag_btn = QPushButton("Editovat tagy")
        self.edit_tag_btn.clicked.connect(self.edit_tag)
        self.layout.addWidget(self.edit_tag_btn)

        self.sound_file = ""
        self.current_tags = {}

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Vyber MP3 soubor", "", "MP3 soubory (*.mp3)")
        if file_path:
            self.sound_file = file_path
            self.label_file.setText(f"Vybraný soubor: {file_path}")
            self.label_play.setText("Zvuk nebyl přehrán")
            # načti existující tagy
            try:
                audio = EasyID3(self.sound_file)
                self.current_tags = {
                    "title": audio.get("title", [""])[0],
                    "artist": audio.get("artist", [""])[0],
                    "album": audio.get("album", [""])[0],
                    "comment": audio.get("comment", [""])[0]
                }
            except:
                self.current_tags = {"title": "", "artist": "", "album": "", "comment": ""}

    def play_sound(self):
        if self.sound_file:
            pygame.mixer.music.load(self.sound_file)
            pygame.mixer.music.play()
            self.label_play.setText(f"Přehrává: {os.path.basename(self.sound_file)}")
        else:
            self.label_play.setText("Nejdřív vyber soubor!")

    def edit_tag(self):
        dialog = TagDialog(self.current_tags)
        if dialog.exec():
            self.current_tags = dialog.get_tags()
            # uložit tagy do MP3
            try:
                audio = MP3(self.sound_file, ID3=EasyID3)
                for key, value in self.current_tags.items():
                    audio[key] = value
                audio.save()
                self.label_play.setText(f"Tagy uloženy: {self.current_tags.get('title','')}")
            except Exception as e:
                self.label_play.setText(f"Chyba při ukládání tagů: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditorTagu()
    window.show()
    sys.exit(app.exec())
