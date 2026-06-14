from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget,
    QFileDialog, QLabel, QDialog, QFormLayout, QLineEdit, QMessageBox, QDialogButtonBox
)
from PyQt6.QtGui import QPixmap
import os
import tag_manager

class TagEditorDialog(QDialog):
    def __init__(self, file_path, audio_manager):
        super().__init__()
        self.audio_manager = audio_manager
        self.setWindowTitle("Upravit tagy")
        self.file_path = file_path

        layout = QFormLayout(self)

        audio = tag_manager.get_tags(file_path)

        self.title_edit = QLineEdit(audio.get("title", [""])[0] if "title" in audio else "")
        self.artist_edit = QLineEdit(audio.get("artist", [""])[0] if "artist" in audio else "")

        layout.addRow("Název:", self.title_edit)
        layout.addRow("Interpret:", self.artist_edit)

        self.cover_label = QLabel("Žádný obrázek")
        layout.addRow("Cover:", self.cover_label)

        self.cover_btn = QPushButton("Přidat obrázek")
        self.cover_btn.clicked.connect(self.add_cover)
        layout.addRow(self.cover_btn)

        self.cover_path = None

        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.save_tags)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

    def add_cover(self):
        file, _ = QFileDialog.getOpenFileName(self, "Vyber obrázek", "", "Obrázky (*.png *.jpg *.jpeg)")
        if file:
            self.cover_path = file
            pixmap = QPixmap(file).scaledToWidth(100)
            self.cover_label.setPixmap(pixmap)

    def save_tags(self):
        tag_manager.save_tags(self.file_path, self.title_edit.text(), self.artist_edit.text(), self.cover_path)
        self.accept()


class EditorTagu(QWidget):
    def __init__(self, audio_manager):
        super().__init__()
        self.audio_manager = audio_manager
        self.setWindowTitle("Editor tagů – playlist + hlas + tagy")
        self.resize(600, 450)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.playlist = QListWidget()
        self.layout.addWidget(self.playlist)

        self.label_status = QLabel("Zatím nic nehraje")
        self.layout.addWidget(self.label_status)

        self.add_btn = QPushButton("Přidat soubor(y)")
        self.add_btn.clicked.connect(self.add_files)
        self.layout.addWidget(self.add_btn)

        self.play_btn = QPushButton("Přehrát vybraný soubor")
        self.play_btn.clicked.connect(self.play_selected)
        self.layout.addWidget(self.play_btn)

        self.edit_btn = QPushButton("Upravit tagy vybraného souboru")
        self.edit_btn.clicked.connect(self.edit_tags)
        self.layout.addWidget(self.edit_btn)

        self.sound_files = []

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Vyber MP3 soubory", "", "MP3 soubory (*.mp3)")
        for f in files:
            if f not in self.sound_files:
                self.sound_files.append(f)
                self.playlist.addItem(os.path.basename(f))

    def play_selected(self):
        selected = self.playlist.currentRow()
        if selected >= 0:
            file_to_play = self.sound_files[selected]

            self.audio_manager.speak(f"Přehrává se {os.path.basename(file_to_play)}")
            self.audio_manager.play(file_to_play)

            self.label_status.setText(f"Přehrává: {os.path.basename(file_to_play)}")
        else:
            self.label_status.setText("Nejdřív vyber soubor!")
            self.audio_manager.speak("Nejdřív vyber soubor")

    def edit_tags(self):
        selected = self.playlist.currentRow()
        if selected >= 0:
            file_to_edit = self.sound_files[selected]
            dialog = TagEditorDialog(file_to_edit, self.audio_manager)
            if dialog.exec():
                self.audio_manager.speak("Tagy byly uloženy")
        else:
            QMessageBox.warning(self, "Chyba", "Nejdřív vyber soubor!")
