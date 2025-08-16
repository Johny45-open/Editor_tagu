import sys
import os
import pygame
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QLineEdit
)

class EditorTagu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor tagů – s přehrávačem")
        self.resize(400, 250)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Inicializace pygame mixeru
        pygame.mixer.init()

        # Label pro název souboru
        self.label_file = QLabel("Žádný soubor vybrán")
        self.layout.addWidget(self.label_file)

        # Tlačítko pro výběr souboru
        self.load_btn = QPushButton("Vybrat zvukový soubor")
        self.load_btn.clicked.connect(self.load_file)
        self.layout.addWidget(self.load_btn)

        # Label pro stav přehrávání
        self.label_play = QLabel("Zvuk nebyl přehrán")
        self.layout.addWidget(self.label_play)

        # Tlačítko pro přehrání
        self.play_btn = QPushButton("Přehrát")
        self.play_btn.clicked.connect(self.play_sound)
        self.layout.addWidget(self.play_btn)

        # Pole pro editaci tagu
        self.tag_edit = QLineEdit()
        self.tag_edit.setPlaceholderText("Zadej nový tag")
        self.layout.addWidget(self.tag_edit)

        # Tlačítko pro uložení tagu (můžeš doplnit funkci)
        self.save_btn = QPushButton("Uložit tag")
        self.layout.addWidget(self.save_btn)

        # Proměnná pro cestu k souboru
        self.sound_file = ""

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Vyber zvukový soubor", "", "Zvukové soubory (*.wav *.mp3)")
        if file_path:
            self.sound_file = file_path
            self.label_file.setText(f"Vybraný soubor: {file_path}")
            self.label_play.setText("Zvuk nebyl přehrán")

    def play_sound(self):
        if self.sound_file:
            pygame.mixer.music.load(self.sound_file)
            pygame.mixer.music.play()
            self.label_play.setText(f"Přehrává: {os.path.basename(self.sound_file)}")
        else:
            self.label_play.setText("Nejdřív vyber soubor!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditorTagu()
    window.show()
    sys.exit(app.exec())
