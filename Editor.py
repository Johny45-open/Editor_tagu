import sys
import os
import pygame
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QDialog, QLineEdit, QHBoxLayout
)

class TagDialog(QDialog):
    def __init__(self, current_tag=""):
        super().__init__()
        self.setWindowTitle("Editace tagu")
        self.resize(300, 120)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Zadej nový tag:")
        self.layout.addWidget(self.label)

        self.tag_edit = QLineEdit()
        self.tag_edit.setText(current_tag)
        self.layout.addWidget(self.tag_edit)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Zrušit")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.layout.addLayout(btn_layout)

    def get_tag(self):
        return self.tag_edit.text()


class EditorTagu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor tagů – s přehrávačem a dialogem")
        self.resize(400, 250)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        pygame.mixer.init()

        self.label_file = QLabel("Žádný soubor vybrán")
        self.layout.addWidget(self.label_file)

        self.load_btn = QPushButton("Vybrat zvukový soubor")
        self.load_btn.clicked.connect(self.load_file)
        self.layout.addWidget(self.load_btn)

        self.label_play = QLabel("Zvuk nebyl přehrán")
        self.layout.addWidget(self.label_play)

        self.play_btn = QPushButton("Přehrát")
        self.play_btn.clicked.connect(self.play_sound)
        self.layout.addWidget(self.play_btn)

        # tlačítko pro otevření dialogu tagu
        self.edit_tag_btn = QPushButton("Editovat tag")
        self.edit_tag_btn.clicked.connect(self.edit_tag)
        self.layout.addWidget(self.edit_tag_btn)

        self.sound_file = ""
        self.current_tag = ""

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

    def edit_tag(self):
        dialog = TagDialog(self.current_tag)
        if dialog.exec():  # OK stisknuto
            self.current_tag = dialog.get_tag()
            self.label_play.setText(f"Aktuální tag: {self.current_tag}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditorTagu()
    window.show()
    sys.exit(app.exec())
