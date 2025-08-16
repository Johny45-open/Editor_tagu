import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel, QLineEdit, QFileDialog, QInputDialog
from gtts import gTTS
import playsound
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
import requests

def speak(text):
    tts = gTTS(text=text, lang='cs')
    filename = "temp.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

class VoiceTagEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceTagEditor")
        self.setGeometry(100, 100, 500, 500)
        
        self.layout = QVBoxLayout()
        
        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)
        
        self.title_label = QLabel("Název:")
        self.title_edit = QLineEdit()
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.title_edit)
        
        self.artist_label = QLabel("Interpret:")
        self.artist_edit = QLineEdit()
        self.layout.addWidget(self.artist_label)
        self.layout.addWidget(self.artist_edit)
        
        self.album_label = QLabel("Album:")
        self.album_edit = QLineEdit()
        self.layout.addWidget(self.album_label)
        self.layout.addWidget(self.album_edit)
        
        # Tlačítka
        self.load_btn = QPushButton("Načíst složku")
        self.load_btn.clicked.connect(self.load_folder)
        self.layout.addWidget(self.load_btn)
        
        self.read_btn = QPushButton("Přečíst tagy")
        self.read_btn.clicked.connect(self.read_tags)
        self.layout.addWidget(self.read_btn)
        
        self.save_btn = QPushButton("Uložit změny")
        self.save_btn.clicked.connect(self.save_tags)
        self.layout.addWidget(self.save_btn)
        
        self.auto_btn = QPushButton("Automaticky doplnit tagy")
        self.auto_btn.clicked.connect(self.auto_tags)
        self.layout.addWidget(self.auto_btn)
        
        self.filter_btn = QPushButton("Filtrovat soubory")
        self.filter_btn.clicked.connect(self.filter_files)
        self.layout.addWidget(self.filter_btn)
        
        self.setLayout(self.layout)
    
    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Vyber složku se soubory")
        if folder:
            self.file_list.clear()
            for file in os.listdir(folder):
                if file.endswith((".mp3", ".flac")):
                    self.file_list.addItem(os.path.join(folder, file))
            speak(f"Načteno {self.file_list.count()} souborů.")
    
    def read_tags(self):
        item = self.file_list.currentItem()
        if not item:
            speak("Nebyl vybrán žádný soubor.")
            return
        file_path = item.text()
        try:
            if file_path.endswith(".mp3"):
                audio = EasyID3(file_path)
                title = audio.get('title', ['Neznámý'])[0]
                artist = audio.get('artist', ['Neznámý'])[0]
                album = audio.get('album', ['Neznámé'])[0]
            elif file_path.endswith(".flac"):
                audio = FLAC(file_path)
                title = audio.get('title', ['Neznámý'])[0]
                artist = audio.get('artist', ['Neznámý'])[0]
                album = audio.get('album', ['Neznámé'])[0]
            self.title_edit.setText(title)
            self.artist_edit.setText(artist)
            self.album_edit.setText(album)
            speak(f"Název: {title}, Interpret: {artist}, Album: {album}")
        except Exception as e:
            speak(f"Chyba při čtení tagů: {str(e)}")
    
    def save_tags(self):
        item = self.file_list.currentItem()
        if not item:
            speak("Nebyl vybrán žádný soubor.")
            return
        file_path = item.text()
        title = self.title_edit.text()
        artist = self.artist_edit.text()
        album = self.album_edit.text()
        try:
            if file_path.endswith(".mp3"):
                audio = EasyID3(file_path)
                audio['title'] = title
                audio['artist'] = artist
                audio['album'] = album
                audio.save()
            elif file_path.endswith(".flac"):
                audio = FLAC(file_path)
                audio['title'] = title
                audio['artist'] = artist
                audio['album'] = album
                audio.save()
            speak(f"Změny uloženy: {title} od {artist}, album {album}")
        except Exception as e:
            speak(f"Chyba při ukládání tagů: {str(e)}")
    
    def auto_tags(self):
        item = self.file_list.currentItem()
        if not item:
            speak("Nebyl vybrán žádný soubor.")
            return
        file_path = item.text()
        title = os.path.splitext(os.path.basename(file_path))[0]
        # jednoduché hledání přes MusicBrainz API (příklad)
        try:
            response = requests.get(f"https://musicbrainz.org/ws/2/recording/?query={title}&fmt=json")
            data = response.json()
            if 'recordings' in data and len(data['recordings']) > 0:
                rec = data['recordings'][0]
                artist = rec['artist-credit'][0]['name'] if 'artist-credit' in rec else 'Neznámý'
                album = rec['releases'][0]['title'] if 'releases' in rec and len(rec['releases']) > 0 else 'Neznámé'
                self.title_edit.setText(title)
                self.artist_edit.setText(artist)
                self.album_edit.setText(album)
                speak(f"Navrženo: {title}, Interpret: {artist}, Album: {album}")
            else:
                speak("Žádné informace nenalezeny.")
        except Exception as e:
            speak(f"Chyba při získávání dat: {str(e)}")
    
    def filter_files(self):
        text, ok = QInputDialog.getText(self, "Filtrovat soubory", "Zadej text pro filtr:")
        if ok and text:
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                item.setHidden(text.lower() not in item.text().lower())
            speak(f"Soubory filtrovány podle '{text}'.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = VoiceTagEditor()
    editor.show()
    sys.exit(app.exec())
