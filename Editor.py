import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QLabel, QLineEdit, QFileDialog
from gtts import gTTS
import playsound

# Funkce pro hlasový výstup
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
        self.setGeometry(100, 100, 500, 400)
        
        self.layout = QVBoxLayout()
        
        # Seznam souborů
        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)
        
        # Tagy
        self.title_label = QLabel("Název:")
        self.title_edit = QLineEdit()
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.title_edit)
        
        self.artist_label = QLabel("Interpret:")
        self.artist_edit = QLineEdit()
        self.layout.addWidget(self.artist_label)
        self.layout.addWidget(self.artist_edit)
        
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
        
        self.setLayout(self.layout)
        
    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Vyber složku se soubory")
        if folder:
            self.file_list.clear()
            for file in os.listdir(folder):
                if file.endswith((".mp3", ".flac", ".wav")):
                    self.file_list.addItem(os.path.join(folder, file))
            speak(f"Načteno {self.file_list.count()} souborů.")
    
    def read_tags(self):
        current_item = self.file_list.currentItem()
        if current_item:
            file_path = current_item.text()
            # Zjednodušeně jen název souboru jako název skladby
            title = os.path.splitext(os.path.basename(file_path))[0]
            self.title_edit.setText(title)
            self.artist_edit.setText("Neznámý")
            speak(f"Název skladby je {title}, interpret Neznámý.")
    
    def save_tags(self):
        # Tady by se přidala logika pro upravení skutečných tagů
        title = self.title_edit.text()
        artist = self.artist_edit.text()
        speak(f"Změny uloženy: {title} od {artist}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = VoiceTagEditor()
    editor.show()
    sys.exit(app.exec())
