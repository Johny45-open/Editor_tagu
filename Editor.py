from PyQt6.QtWidgets import QListWidget, QPushButton, QVBoxLayout, QWidget

class EditorTagu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor tagů – playlist + hlas")
        self.resize(500, 400)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.playlist = QListWidget()
        self.layout.addWidget(self.playlist)

        self.add_btn = QPushButton("Přidat soubor(y)")
        self.add_btn.clicked.connect(self.add_files)
        self.layout.addWidget(self.add_btn)

        self.play_btn = QPushButton("Přehrát vybraný soubor")
        self.play_btn.clicked.connect(self.play_selected)
        self.layout.addWidget(self.play_btn)

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
            pygame.mixer.music.load(file_to_play)
            pygame.mixer.music.play()
