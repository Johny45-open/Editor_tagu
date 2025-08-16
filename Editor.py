import sys
import os
import pygame
import tempfile
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QDialog, QLineEdit, QFormLayout, QHBoxLayout
)
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from gtts import gTTS

# --- Funkce pro hlasový výstup přes gTTS s automatickým smazáním ---
def speak_gtts(text):
    tts = gTTS(text=text, lang='cs')
    with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as tmp_file:
        tts.save(tmp_file.name)
        pygame.mixer.music.load(tmp_file.name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

# --- Dialog pro editaci tagů + cover art ---
class TagDialog(QDialog):
    def __init__(self, tags=None):
        super().__init__()
        self.setWindowTitle("Editace tagů")
        self.resize(350, 220)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        form_layout = QFormLayout()
        self.layout.addLayout(form_layout)

        self.title_edit = QLineEdit(tags.get("title", ""))
        form_layout.addRow("Název:", self.title_edit)

        self.artist_edit = QLineEdit(tags.get("artist", ""))
        form_layout.addRow("Autor:", self.artist_edit)

        self.album_edit = QLineEdit(tags.get("album", ""))
        form_layout.addRow("Album:", self.album_edit)

        self.comment_edit = QLineEdit(tags.get("comment", ""))
        form_layout.addRow("Komentář:", self.comment_edit)

        self.cover_file = None
        self.cover_btn = QPushButton("Vybrat obrázek (cover art)")
        self.cover_btn.clicked.connect(self.select_cover)
        self.layout.addWidget(self.cover_btn)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Zrušit")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        self.layout.addLayout(btn_layout)

    def select_cover(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Vyber obrázek", "", "Obrázky (*.jpg *.jpeg *.png)")
        if file_path:
            self.cover_file = file_path

    def get_tags(self):
        return {
            "title": self.title_edit.text(),
            "artist": self.artist_edit.text(),
            "album": self.album_edit.text(),
            "comment": self.comment_edit.text(),
            "cover": self.cover_file
        }

# --- Hlavní okno editoru ---
class EditorTagu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor tagů – přehrávač + cover art + hlas")
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

        self.edit_tag_btn = QPushButton("Editovat tagy a cover")
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
                    "comment": audio.get("comment", [""])[0],
                    "cover": None
                }
            except:
                self.current_tags = {"title": "", "artist": "", "album": "", "comment": "", "cover": None}

            # hlasový výstup všech tagů
            tag_text = (
                f"Vybrán soubor {os.path.basename(file_path)}. "
                f"Název: {self.current_tags['title'] or 'nenastaveno'}. "
                f"Autor: {self.current_tags['artist'] or 'nenastaveno'}. "
                f"Album: {self.current_tags['album'] or 'nenastaveno'}. "
                f"Komentář: {self.current_tags['comment'] or 'nenastaveno'}."
            )
            speak_gtts(tag_text)

    def play_sound(self):
        if self.sound_file:
            pygame.mixer.music.load(self.sound_file)
            pygame.mixer.music.play()
            self.label_play.setText(f"Přehrává: {os.path.basename(self.sound_file)}")
            speak_gtts(f"Přehrává se {os.path.basename(self.sound_file)}")
        else:
            self.label_play.setText("Nejdřív vyber soubor!")
            speak_gtts("Nejdřív vyber soubor")

    def edit_tag(self):
        dialog = TagDialog(self.current_tags)
        if dialog.exec():
            self.current_tags = dialog.get_tags()
            try:
                # uložit základní tagy
                audio = MP3(self.sound_file, ID3=EasyID3)
                for key, value in self.current_tags.items():
                    if key != "cover":
                        audio[key] = value
                audio.save()

                # uložit cover art, pokud byl vybrán
                if self.current_tags.get("cover"):
                    audio_id3 = ID3(self.sound_file)
                    with open(self.current_tags["cover"], "rb") as img:
                        mime_type = "image/jpeg" if self.current_tags["cover"].lower().endswith((".jpg", ".jpeg")) else "image/png"
                        audio_id3["APIC"] = APIC(
                            encoding=3,
                            mime=mime_type,
                            type=3,
                            desc="Cover",
                            data=img.read()
                        )
                    audio_id3.save()

                self.label_play.setText(f"Tagy a cover uloženy: {self.current_tags.get('title','')}")
                speak_gtts(f"Tagy uloženy: {self.current_tags.get('title','')}")
            except Exception as e:
                self.label_play.setText(f"Chyba při ukládání tagů: {e}")
                speak_gtts("Chyba při ukládání tagů")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditorTagu()
    window.show()
    sys.exit(app.exec())
