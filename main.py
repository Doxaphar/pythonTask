import os
import threading
import time
from functools import partial

from PyQt5.QtGui import QFont

os.environ['QT_MULTIMEDIA_PREFERRED_PLUGINS'] = 'windowsmediafoundation'
import sys
from datetime import timedelta
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import (QApplication,
                             QLabel,
                             QMainWindow,
                             QLayout,
                             QPushButton,
                             QGridLayout,
                             QVBoxLayout, QWidget, QStackedWidget, QHBoxLayout, QHeaderView, QSpacerItem, QScrollArea)


class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Karaoke")
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self._configureColorSettings()
        self._createSongsMenu()
        self.player = Player(self)

    def closeEvent(self, event):
        self.player.player.pause()
        self.player.state = "stop_all"

    def _configureColorSettings(self):
        self.setStyleSheet("color: white;"
                           "background-color: #A8D8EA;")

    def _changeCurrentWidget(self, widget):
        self.central_widget.addWidget(widget)
        self.central_widget.setCurrentWidget(widget)

    def _createSongsMenu(self):
        menu = Menu("Choose a track:", self)
        for song in os.listdir(f"data"):
            btn = self._createMenuButton(song)
            btn.clicked.connect(partial(self.openPlayer, f"data/{song}/"))
            menu.addMenuButton(btn)
        self._changeCurrentWidget(menu)

    def _createMenuButton(self, text):
        btn = QPushButton(text)
        btn.setFixedHeight(150)
        btn.setFixedWidth(1470)
        btn.setStyleSheet("border: 0;"
                          "background-color: #FCBAD3;"
                          "height: 150px;"
                          "font-size: 50px;")
        return btn

    def openPlayer(self, path):
        self.player.open(path)
        self._changeCurrentWidget(self.player)


class Player(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.state = "not_started"
        self.curr_line = 0
        self.curr_word = 0

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.upper_layout = QHBoxLayout()
        self.title = QPushButton()
        self.title.setStyleSheet("border: 1 double #E0144C;"
                                 "font-size: 50px;"
                                 "background-color: #AA96DA;")
        self.upper_layout.addWidget(self.title)
        self.back_btn = QPushButton("back")
        self.back_btn.setStyleSheet("border: 1 double #E0144C;"
                                    "font-size: 50px;"
                                    "background-color: #AA96DA;")
        self.upper_layout.addWidget(self.back_btn)
        self.layout.addLayout(self.upper_layout)

        self.pic = QPushButton()
        self.pic.setMinimumHeight(700)
        self.pic.setMaximumHeight(700)
        self.pic.clicked.connect(lambda: self.play())
        self.layout.addWidget(self.pic)

        self.line1 = QLabel()
        self.line2 = QLabel()

        self.line1.setTextFormat(Qt.RichText)
        self.line2.setTextFormat(Qt.RichText)

        self.line1.setMaximumHeight(100)
        self.line2.setMaximumHeight(100)

        self.line1.setAlignment(Qt.AlignCenter)
        self.line2.setAlignment(Qt.AlignCenter)

        self.line1.setFont(QFont("Arial", 50))
        self.line2.setFont(QFont("Arial", 50))

        self.layout.addWidget(self.line1)
        self.layout.addWidget(self.line2)

        self.player = QMediaPlayer()

        self.setLayout(self.layout)
        self.lyrics = []

    def open(self, path):
        url = QUrl.fromLocalFile(path + "audio.mp3")
        content = QMediaContent(url)
        self.player.setMedia(content)

        self.pic.setStyleSheet(f"background-repeat: no-repeat;"
                               f"background-position: center;"
                               f"background-image: url({path}img.jpg);")

        self.loadLyrics(path)
        self.curr_line = -1
        self.curr_word = -1
        self.line1.setText(self._getLine(0))
        self.line2.setText(self._getLine(1))

        self.title.setText(path.split("/")[1])
        self.back_btn.clicked.connect(lambda: self.back(lambda: self.parent._createSongsMenu()))

    def back(self, back):
        self.player.pause()
        self.state = "stop_all"
        back()

    def loadLyrics(self, path):
        self.lyrics = []
        txt = open(path + "text.txt", encoding="utf-8").readlines()
        for line in txt:
            self.lyrics += [[[x.split(':')[0], timedelta(milliseconds=int(float(x.split(':')[1]) * 1000))] for x in
                             line.split(';')[:-1]]]

    def _getLine(self, i):
        if i != self.curr_line:
            return " ".join([w[0] for w in self.lyrics[i]])
        res = f'<p><span style="color: #E0144C;">'
        for w in self.lyrics[self.curr_line][:self.curr_word + 1]:
            res += w[0]
        res += '</span>'
        for w in self.lyrics[self.curr_line][self.curr_word + 1:]:
            res += w[0]
        return res + '</p>'

    def waitForEnd(self):
        while True:
            if self.state == "stop_all":
                return
            if self.player.state() == QMediaPlayer.EndOfMedia:
                self.parent._createSongsMenu()
            time.sleep(1)

    def checkLyrics(self):
        while True:
            if self.state != "playing":
                return
            self.curr_word += 1
            if self.curr_line == -1:
                self.curr_line += 1
            if self.curr_word == len(self.lyrics[self.curr_line]):
                self.curr_word = 0
                self.curr_line += 1
                if self.curr_line == len(self.lyrics):
                    [self.line1, self.line2][(self.curr_line - 1) % 2].setText("")
                    thread = threading.Thread(target=self.waitForEnd)
                    thread.start()
                    return
                if self.curr_line == len(self.lyrics) - 1:
                    [self.line1, self.line2][(self.curr_line + 1) % 2].setText("")
                else:
                    [self.line1, self.line2][(self.curr_line + 1) % 2].setText(self._getLine(self.curr_line + 1))
            line = [self.line1, self.line2][self.curr_line % 2]
            text = self._getLine(self.curr_line)
            line.setText(text)
            time.sleep(self.lyrics[self.curr_line][self.curr_word][1].total_seconds())

    def play(self):
        if self.player.state() != QMediaPlayer.PlayingState:
            self.player.play()
            self.state = "playing"
            thread = threading.Thread(target=self.checkLyrics)
            thread.start()
        else:
            self.state = "paused"
            self.player.pause()


class Menu(QWidget):
    def __init__(self, title=None, parent=None):
        super(Menu, self).__init__(parent)
        self.outer_layout = QVBoxLayout()

        self.upper_layout = QHBoxLayout()
        self.outer_layout.addLayout(self.upper_layout)
        if title is not None:
            self.upper_layout.addWidget(self._createTitleButton(title))

        self.buttons = QWidget()
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.setAlignment(Qt.AlignCenter)
        self.buttons_layout.setSpacing(50)
        self.buttons.setLayout(self.buttons_layout)

        hlayout = QHBoxLayout()
        scroll = QScrollArea()
        scroll.setWidget(self.buttons)
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        hlayout.addWidget(scroll)

        self.outer_layout.addLayout(hlayout)

        self.setLayout(self.outer_layout)

    def addMenuButton(self, widget: QPushButton):
        self.buttons_layout.addWidget(widget)

    def addUpperMenuItem(self, widget):
        self.upper_layout.addWidget(widget)

    def _createTitleButton(self, text):
        btn = QPushButton(text)
        btn.setStyleSheet("border: 0;"
                          "background-color: #AA96DA;"
                          "height: 150px;"
                          "margin: 10px 200px 10px 200px;"
                          "font-size: 50px;")
        return btn


app = QApplication([])
window = Window()
window.showMaximized()
sys.exit(app.exec())
