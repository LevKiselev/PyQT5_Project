import sys
import sqlite3
from datetime import date
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem
from main_ui import Ui_MainWindow
from start_ui import Ui_StartWindow
from rules import RulesWindow, UserList
from picture_game import PictureGame, KnightGame
from numbers_game import NumbersGame


class StartPage(QWidget, Ui_StartWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.unameEdit.setFocus()


class MainWin(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWin, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.username = 'Nemo'
        self.con = sqlite3.connect("records.db")
        cur = self.con.cursor()
        res = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
        if not res:
            self.create_tables()
        self.action_start.triggered.connect(self.game_select)
        self.action_numbers.triggered.connect(self.game_select)
        self.action_picture.triggered.connect(self.game_select)
        self.action_knight.triggered.connect(self.game_select)
        self.action_about.triggered.connect(self.rules_show)
        self.action_rules_numbers.triggered.connect(self.rules_show)
        self.action_rules_picture.triggered.connect(self.rules_show)
        self.action_rules_knight.triggered.connect(self.rules_show)
        self.action_userlist.triggered.connect(self.user_list)
        self.start_page = StartPage(self.tab_start)
        self.game_numbers = NumbersGame(self.tab_numbers)
        self.game_picture = PictureGame(self.tab_picture)
        self.game_knight = KnightGame(self.tab_knight)
        self.start_page.goNumbersButton.clicked.connect(self.game_select)
        self.start_page.goPictureButton.clicked.connect(self.game_select)
        self.start_page.goKnightButton.clicked.connect(self.game_select)
        self.start_page.saveNameButton.clicked.connect(self.uname_save)

    def uname_save(self):
        cur = self.con.cursor()
        now = date.today()
        self.username = self.start_page.unameEdit.text()
        if self.username == '':
            self.username = 'Nemo'
        res = cur.execute(f"SELECT id FROM users WHERE name = '{self.username}'").fetchone()
        if res:
            cur.execute(f"UPDATE users SET last_time='{now}' WHERE id={res[0]}")
            self.start_page.greeting_label.setText(f"Здравствуйте, {self.username}!\n"
                                                   f"Ваше имя найдено в списке игроков.\nС возвращением!")
        else:
            new_rec = (None, self.username, now, now, 0, 0, 0)
            cur.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?)', new_rec)
            self.start_page.greeting_label.setText(f"Здравствуйте, {self.username}!\nПохоже, вы зашли в первый раз.\n"
                                                   f"Ваше имя добавлено к списку игроков.")
            res = cur.execute(f"SELECT id FROM users WHERE name = '{self.username}'").fetchone()
        self.game_picture.uid = res[0]
        self.game_knight.uid = res[0]
        self.game_numbers.uid = res[0]
        res_n = cur.execute(f"SELECT human_count, comp_count FROM numbers WHERE user_id = {res[0]}").fetchone()
        if res_n:
            self.game_numbers.human_counter = res_n[0]
            self.game_numbers.comp_counter = res_n[1]
            self.game_numbers.comp_counter_label.setText(str(self.game_numbers.comp_counter))
            self.game_numbers.human_counter_label.setText(str(self.game_numbers.human_counter))
        self.con.commit()

    def user_list(self):
        cur = self.con.cursor()
        res = cur.execute("SELECT name, reg_time, last_time, numbers_count, picture_count, knight_count FROM users ORDER BY name").fetchall()
        ulist = UserList(self)
        ulist.stat_table.setRowCount(len(res))
        ulist.stat_table.setColumnCount(6)
        ulist.stat_table.setColumnWidth(0, 200)
        for i in range(1, 6):
            ulist.stat_table.setColumnWidth(i, 80)
        ulist.stat_table.setHorizontalHeaderLabels(['Имя', 'Дата\nрегистрации', 'Последний\nвход',
                                                    'Сыграно в\nчисла', 'Сыграно в\nкартинки', 'Сыграно в\nконя'])
        ulist.stat_table.setSortingEnabled(True)
        for i, elem in enumerate(res):
            for j, val in enumerate(elem):
                ulist.stat_table.setItem(i, j, QTableWidgetItem(str(val)))
        ulist.show()

    def game_select(self):
        if self.sender().objectName() == 'action_start':
            self.tabWidget.setCurrentWidget(self.tab_start)
        elif self.sender().objectName() in ['action_numbers', 'goNumbersButton']:
            self.tabWidget.setCurrentWidget(self.tab_numbers)
        elif self.sender().objectName() in ['action_picture', 'goPictureButton']:
            self.tabWidget.setCurrentWidget(self.tab_picture)
        elif self.sender().objectName() in ['action_knight', 'goKnightButton']:
            self.tabWidget.setCurrentWidget(self.tab_knight)

    def rules_show(self):
        rul = RulesWindow(self, content='about')
        rul.text_label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        if self.sender().objectName() == 'action_rules_numbers':
            rul = RulesWindow(self, content='numbers')
        elif self.sender().objectName() == 'action_rules_picture':
            rul = RulesWindow(self, content='picture')
        elif self.sender().objectName() == 'action_rules_knight':
            rul = RulesWindow(self, content='knight')
        rul.show()

    def create_tables(self):
        cur = self.con.cursor()
        cur.execute('''
            CREATE TABLE users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT,
                reg_time      DATE,
                last_time     DATE,
                numbers_count INTEGER DEFAULT (0),
                picture_count INTEGER DEFAULT (0),
                knight_count  INTEGER DEFAULT (0) 
            );
        ''')
        cur.execute('''
            CREATE TABLE numbers (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER REFERENCES users (id),
                human_count INTEGER DEFAULT (0),
                comp_count  INTEGER DEFAULT (0),
                avg_steps   REAL    DEFAULT (0),
                avg_timer   INTEGER DEFAULT (0) 
            );
        ''')
        cur.execute('''
            CREATE TABLE picture (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER REFERENCES users (id),
                level      INTEGER,
                step_count INTEGER,
                timer      INTEGER
            );
        ''')
        cur.execute('''
            CREATE TABLE knight (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER REFERENCES users (id),
                level      INTEGER,
                step_count INTEGER,
                timer      INTEGER
            );
        ''')
        self.con.commit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWin()
    ex.show()
    sys.exit(app.exec_())
