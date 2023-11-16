import sqlite3
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QTableWidgetItem
from picture_ui import Ui_PictureWindow
from rules import RulesWindow, InfoWindow, UserList


class PictureGame(QWidget, Ui_PictureWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.uid = 0
        self.con = sqlite3.connect("records.db")
        self.level = self.level_spin.value()
        self.step_counter = 0
        self.goal = False
        self.game_timer = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_timer)
        self.timer.start(1000)
        self.but = [[QPushButton for i in range(10)] for j in range(10)]
        self.tiles = [[0] * 10] * 10
        self.resetButton.clicked.connect(self.reset_level)
        self.rulesButton.clicked.connect(self.rules_show)
        self.statButton.clicked.connect(self.stat_show)
        self.bgPicLabel = QLabel(self)
        self.x_offset = 130
        self.y_offset = 20
        self.cur_pos = [-1, -1]
        for i in range(10):
            for j in range(10):
                self.but[i][j] = QPushButton(self.bgPicLabel)
                self.but[i][j].setObjectName("b" + str(i) + str(j))
                self.but[i][j].clicked.connect(self.next_step)
        self.draw_board()

    def rules_show(self):
        rul = RulesWindow(self, content='picture')
        rul.show()

    def stat_show(self):
        cur = self.con.cursor()
        res = cur.execute(f"SELECT users.name, level, step_count, timer FROM {self.parent().objectName()[4:]}"
                          f" INNER JOIN users ON users.id = user_id WHERE level = {self.level}"
                          f" ORDER BY step_count, timer").fetchall()
        ulist = UserList(self)
        ulist.stat_header.setText(f"Рекорды уровня {self.level}")
        ulist.stat_table.setRowCount(len(res))
        ulist.stat_table.setColumnCount(4)
        ulist.stat_table.setColumnWidth(0, 200)
        for i in range(1, 6):
            ulist.stat_table.setColumnWidth(i, 80)
        ulist.stat_table.setHorizontalHeaderLabels(['Имя', 'Уровень', 'Кол-во ходов', 'Время'])
        ulist.stat_table.setSortingEnabled(True)
        for i, elem in enumerate(res):
            for j, val in enumerate(elem):
                ulist.stat_table.setItem(i, j, QTableWidgetItem(str(val)))
        ulist.show()

    def show_timer(self):
        if self.step_counter and not self.goal:
            self.game_timer += 1
            self.timer_label.setText(f'{(self.game_timer // 60):02d}.{(self.game_timer % 60):02d}')

    def draw_board(self):
        self.tiles = [[0 for i in range(10)] for j in range(10)]
        picture = QPixmap(f":pics/pics/{self.parent().objectName()[4:]}/pic{self.level}.jpg")
        self.bgPicLabel.setPixmap(picture)
        self.bgPicLabel.setGeometry(self.x_offset, self.y_offset, picture.width(), picture.height())
        tile_size = picture.width() // self.level
        for i in range(10):
            for j in range(10):
                if i < self.level and j < self.level:
                    self.but[i][j].resize(tile_size - 2, tile_size - 2)
                    self.but[i][j].move(i * tile_size + 1, j * tile_size + 1)
                    self.but[i][j].show()
                else:
                    self.but[i][j].hide()
        self.set_buttons()

    def set_buttons(self):
        for i in range(self.level):
            for j in range(self.level):
                if self.tiles[i][j]:
                    self.but[i][j].setStyleSheet("background-color: rgba(255, 255, 255, 192); border: None;")
                else:
                    self.but[i][j].setStyleSheet("background-color: rgba(0, 160, 255, 255); border: None;")

    def next_step(self):
        cur = self.con.cursor()
        delta = [[0, 0], [-1, 0], [1, 0], [0, -1], [0, 1]]
        self.step_counter += 1
        self.step_label.setText(str(self.step_counter))
        x = int(self.sender().objectName()[1])
        y = int(self.sender().objectName()[2])
        for i in range(5):
            if 0 <= x + delta[i][0] < self.level and 0 <= y + delta[i][1] < self.level:
                self.tiles[x + delta[i][0]][y + delta[i][1]] = (self.tiles[x + delta[i][0]][y + delta[i][1]] + 1) % 2
        self.set_buttons()
        self.goal = self.check_goal()
        if self.goal:
            res = cur.execute(f"SELECT step_count, timer FROM picture WHERE user_id={self.uid} and level={self.level}").fetchone()
            if res:
                if res[0] > self.step_counter or res[0] == self.step_counter and res[1] > self.game_timer:
                    cur.execute(f"UPDATE picture SET step_count={self.step_counter}, timer={self.game_timer}"
                                f" WHERE user_id={self.uid} and level={self.level}")
            else:
                new_rec = (None, self.uid, self.level, self.step_counter, self.game_timer)
                cur.execute('INSERT INTO picture VALUES (?,?,?,?,?)', new_rec)
            res = cur.execute(f"SELECT picture_count FROM users WHERE id = {self.uid}").fetchone()
            if res:
                cur.execute(f"UPDATE users SET picture_count={res[0] + 1} WHERE id={self.uid}")
            self.con.commit()
            info = InfoWindow(self, content=6)
            info.show()
            for i in range(10):
                for j in range(10):
                    self.but[i][j].hide()

    def reset_level(self):
        self.cur_pos = [-1, -1]
        self.goal = False
        self.game_timer = 0
        self.timer_label.setText(f'{(self.game_timer // 60):02d}.{(self.game_timer % 60):02d}')
        self.level = self.level_spin.value()
        self.step_counter = 0
        self.step_label.setText(str(self.step_counter))
        self.draw_board()
        self.set_buttons()

    def check_goal(self):
        for i in range(self.level):
            for j in range(self.level):
                if not self.tiles[i][j]:
                    return False
        return True


class KnightGame(PictureGame):

    def __init__(self, parent=None):
        super().__init__(parent)

    def rules_show(self):
        rul = RulesWindow(self, content='knight')
        rul.show()

    def set_buttons(self):
        delta = [[-2, -1], [-2, 1], [2, -1], [2, 1], [-1, -2], [1, -2], [-1, 2], [1, 2]]
        for i in range(self.level):
            for j in range(self.level):
                self.but[i][j].setEnabled(not self.step_counter)
                if self.tiles[i][j]:
                    self.but[i][j].setStyleSheet("background-color: rgba(255, 255, 255, 192); border: None;")
                else:
                    self.but[i][j].setStyleSheet("background-color: rgba(0, 160, 255, 255); border: None;")
        if self.step_counter:
            cnt = 0
            for i in range(8):
                x = self.cur_pos[0] + delta[i][0]
                y = self.cur_pos[1] + delta[i][1]
                if 0 <= x < self.level and 0 <= y < self.level and not self.tiles[x][y]:
                    cnt += 1
                    self.but[x][y].setEnabled(True)
                    self.but[x][y].setStyleSheet("background-color: rgba(20, 255, 180, 255); border: None;")
            if not cnt and not self.goal:
                info = InfoWindow(self, content=5)
                info.show()

    def next_step(self):
        cur = self.con.cursor()
        self.step_counter += 1
        self.step_label.setText(str(self.step_counter))
        x = int(self.sender().objectName()[1])
        y = int(self.sender().objectName()[2])
        self.cur_pos = [x, y]
        self.tiles[x][y] = 1
        self.goal = self.check_goal()
        self.set_buttons()
        if self.goal:
            res = cur.execute(f"SELECT step_count, timer FROM knight"
                              f" WHERE user_id={self.uid} and level={self.level}").fetchone()
            if res:
                if res[0] > self.step_counter or res[0] == self.step_counter and res[1] > self.game_timer:
                    cur.execute(f"UPDATE knight SET step_count={self.step_counter}, timer={self.game_timer}"
                                f" WHERE user_id={self.uid} and level={self.level}")
            else:
                new_rec = (None, self.uid, self.level, self.step_counter, self.game_timer)
                cur.execute('INSERT INTO knight VALUES (?,?,?,?,?)', new_rec)
            res = cur.execute(f"SELECT knight_count FROM users WHERE id = {self.uid}").fetchone()
            if res:
                cur.execute(f"UPDATE users SET knight_count={res[0] + 1} WHERE id={self.uid}")
            self.con.commit()
            info = InfoWindow(self, content=6)
            info.show()
            for i in range(10):
                for j in range(10):
                    self.but[i][j].hide()
