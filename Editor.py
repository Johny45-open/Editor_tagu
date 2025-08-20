import sys, os, tempfile, time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget,
    QFileDialog, QLabel, QDialog, QFormLayout, QLineEdit, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialogButtonBox
import pygame
from gtts import gTTS
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC


# inicializace pygame
pygame.mixer.init()

# funkce na mluvení přes gTTS
def speak_gtts(text):
    tts = gTTS(text=text, lang="cs")
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_file.close()
    tts.save(tmp_file.name)

    # přehrajeme hlas
    pygame.mixer.music.load(tmp_file.name)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()

    # smažeme dočasný soubor
    for _ in range(5):
        try:
            os.remove(tmp_file.name)
            break
        except PermissionError:
            time.sleep(0.1)


# dialog pro úpravu tagů
class TagEditorDialog(QDialog):
    def __init__(self, file_path):
        super().__init__()
        self.setWindowTitle("Upravit tagy")
        self.file_path = file_path

        layout = QFormLayout(self)

        try:
            audio = EasyID3(file_path)
        except Exception:
            audio = {}

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
        try:
            audio = EasyID3(self.file_path)
        except Exception:
            audio = MP3(self.file_path, ID3=ID3)
            audio.add_tags()

        audio["title"] = self.title_edit.text()
        audio["artist"] = self.artist_edit.text()
        audio.save()

        if self.cover_path:
            audio = MP3(self.file_path, ID3=ID3)
            with open(self.cover_path, "rb") as img:
                audio.tags.add(APIC(mime="image/jpeg", type=3, desc=u"Cover", data=img.read()))
            audio.save()

        self.accept()


class EditorTagu(QWidget):
    def __init__(self):
        super().__init__()
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

            # nejdřív hlas
            speak_gtts(f"Přehrává se {os.path.basename(file_to_play)}")

            # pak hudba
            pygame.mixer.music.load(file_to_play)
            pygame.mixer.music.play()

            self.label_status.setText(f"Přehrává: {os.path.basename(file_to_play)}")
        else:
            self.label_status.setText("Nejdřív vyber soubor!")
            speak_gtts("Nejdřív vyber soubor")

    def edit_tags(self):
        selected = self.playlist.currentRow()
        if selected >= 0:
            file_to_edit = self.sound_files[selected]
            dialog = TagEditorDialog(file_to_edit)
            if dialog.exec():
                speak_gtts("Tagy byly uloženy")
        else:
            QMessageBox.warning(self, "Chyba", "Nejdřív vyber soubor!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditorTagu()
    window.show()
    sys.exit(app.exec())
