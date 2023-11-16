import sqlite3
from random import randrange
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from numbers_ui import Ui_NumbersWindow
from rules import RulesWindow, InfoWindow, UserList


class NumbersGame(QWidget, Ui_NumbersWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.con = sqlite3.connect("records.db")
        self.uid = 0
        self.step_counter = 0
        self.comp_counter = 0
        self.human_counter = 0
        self.goal = 0
        self.human_list = list()
        self.comp_list = list()
        self.assumption = [0, 0, 0, 0]
        self.comp_number = [0, 0, 0, 0]
        self.game_timer = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_timer)
        self.timer.start(1000)
        self.resetButton.clicked.connect(self.reset_level)
        self.rulesButton.clicked.connect(self.rules_show)
        self.statButton.clicked.connect(self.stat_show)
        self.stepButton.clicked.connect(self.next_step)
        self.comp_inp = [self.compStep0, self.compStep1, self.compStep2, self.compStep3]
        self.human_inp = [self.humanBox0, self.humanBox1, self.humanBox2, self.humanBox3]
        for elem in self.human_inp:
            elem.currentIndexChanged.connect(self.check_input)
        self.answerB.currentIndexChanged.connect(self.check_input)
        self.answerK.currentIndexChanged.connect(self.check_input)
        self.reset_level()
        self.update_listing()

    def rules_show(self):
        rul = RulesWindow(self, content='numbers')
        rul.show()

    def stat_show(self):
        cur = self.con.cursor()
        res = cur.execute(f"SELECT users.name, human_count, comp_count, avg_steps, avg_timer FROM numbers"
                          f" INNER JOIN users ON users.id = user_id ORDER BY human_count").fetchall()
        ulist = UserList(self)
        ulist.stat_header.setText(f"Суммарная статистика")
        ulist.stat_table.setRowCount(len(res))
        ulist.stat_table.setColumnCount(5)
        ulist.stat_table.setColumnWidth(0, 200)
        for i in range(1, 6):
            ulist.stat_table.setColumnWidth(i, 80)
        ulist.stat_table.setHorizontalHeaderLabels(['Имя игрока', 'Выигрыши\nигрока', 'Выигрыши\nкомпьютера',
                                                    'Среднее\nкол-во ходов', 'Среднее\nвремя игры'])
        ulist.stat_table.setSortingEnabled(True)
        for i, elem in enumerate(res):
            for j, val in enumerate(elem):
                ulist.stat_table.setItem(i, j, QTableWidgetItem(str(val)))
        ulist.show()

    def show_timer(self):
        if self.step_counter and not self.goal:
            self.game_timer += 1
            self.timer_label.setText(f'{(self.game_timer // 60):02d}.{(self.game_timer % 60):02d}')

    def random_numbers(self):
        m = set(range(10))
        res = []
        for i in range(4):
            while (n := randrange(10)) not in m:
                pass
            m.discard(n)
            res.append(n)
        return res

    def clear_input(self):
        self.stepButton.setEnabled(False)
        for elem in self.human_inp:
            elem.setCurrentIndex(-1)
        self.answerB.setCurrentIndex(-1)
        self.answerK.setCurrentIndex(-1)
        res = [0, 0, 0, 0]
        if self.step_counter:
            res = self.check_assumption()
        else:
            res = self.random_numbers()
        if res:
            for i in range(4):
                self.comp_inp[i].setText(str(res[i]))
        elif not self.goal:
            self.goal = 4  # Обман в ответах
            self.comp_counter += 1

    def next_assumption(self):
        while 1:
            self.assumption[0] += 1
            if self.assumption[0] > 9:
                self.assumption[0] = 0
                self.assumption[1] += 1
                if self.assumption[1] > 9:
                    self.assumption[1] = 0
                    self.assumption[2] += 1
                    if self.assumption[2] > 9:
                        self.assumption[2] = 0
                        self.assumption[3] += 1
                        if self.assumption[3] > 9:
                            return False
            if len(set(self.assumption)) == 4:
                break
        return True

    def check_assumption(self):
        while self.next_assumption():
            for i in range(self.step_counter):
                b_cnt = 0
                k_cnt = 0
                for j in range(4):
                    if self.assumption[j] in self.comp_list[i][0:4]:
                        b_cnt += 1
                    if self.assumption[j] == self.comp_list[i][j]:
                        k_cnt += 1
                if b_cnt != self.comp_list[i][4] or k_cnt != self.comp_list[i][5]:
                    break
            else:
                return self.assumption
        return None

    def reset_level(self):
        self.step_counter = 0
        self.step_label.setText(str(self.step_counter))
        self.game_timer = 0
        self.timer_label.setText(f'{(self.game_timer // 60):02d}.{(self.game_timer % 60):02d}')
        self.goal = False
        self.assumption = [0, 0, 0, 0]
        self.human_list = list()
        self.comp_list = list()
        for i in range(4):
            self.human_inp[i].setEnabled(True)
        self.answerB.setEnabled(True)
        self.answerK.setEnabled(True)
        self.comp_number = self.random_numbers()
        # print(self.comp_number)
        self.clear_input()
        self.update_listing()

    def check_input(self):
        m = {self.human_inp[0].currentIndex(), self.human_inp[1].currentIndex(),
             self.human_inp[2].currentIndex(), self.human_inp[3].currentIndex()}
        b = self.answerB.currentIndex()
        k = self.answerK.currentIndex()
        if len(m) == 4 and -1 not in m and b >= 0 and 0 <= k <= b:
            self.stepButton.setEnabled(True)
        else:
            self.stepButton.setEnabled(False)

    def next_step(self):
        self.step_counter += 1
        self.step_label.setText(str(self.step_counter))
        b = 0
        k = 0
        comp_cur = list()
        for elem in self.comp_inp:
            comp_cur.append(int(elem.text()))
        for i in range(4):
            if self.human_inp[i].currentIndex() in self.comp_number:
                b += 1
                if self.human_inp[i].currentIndex() == self.comp_number[i]:
                    k += 1
        comp_cur.append(self.answerB.currentIndex())
        comp_cur.append(self.answerK.currentIndex())
        if b == k == comp_cur[4] == comp_cur[5] == 4:
            self.goal = 1  # Ничья
            self.comp_counter += 1
            self.human_counter += 1
        elif comp_cur[4] == comp_cur[5] == 4:
            self.goal = 2  # Компьютер выиграл
            self.comp_counter += 1
        elif b == k == 4:
            self.goal = 3  # Человек выиграл
            self.human_counter += 1
        self.human_list.insert(0, [self.human_inp[0].currentIndex(), self.human_inp[1].currentIndex(),
                                   self.human_inp[2].currentIndex(), self.human_inp[3].currentIndex(), b, k])
        self.comp_list.insert(0, comp_cur)
        self.clear_input()
        self.update_listing()
        if self.goal:
            self.game_over()

    def game_over(self):
        cur = self.con.cursor()
        res = cur.execute(f"SELECT * FROM numbers WHERE user_id={self.uid}").fetchone()
        if res:
            if self.goal == 1:
                avg_s = round((res[4] * (res[2] + res[3]) + self.step_counter * 2) /
                              (self.human_counter + self.comp_counter), 3)
                avg_t = round((res[5] * (res[2] + res[3]) + self.game_timer * 2) /
                              (self.human_counter + self.comp_counter))
            else:
                avg_s = round((res[4] * (res[2] + res[3]) + self.step_counter) /
                              (self.human_counter + self.comp_counter), 3)
                avg_t = round((res[5] * (res[2] + res[3]) + self.game_timer) /
                              (self.human_counter + self.comp_counter))
            cur.execute(f"UPDATE numbers SET human_count={self.human_counter}, comp_count={self.comp_counter},"
                        f" avg_steps={avg_s}, avg_timer={avg_t} WHERE user_id={self.uid}")
        else:
            new_rec = (None, self.uid, self.human_counter, self.comp_counter, self.step_counter, self.game_timer)
            cur.execute('INSERT INTO numbers VALUES (?,?,?,?,?,?)', new_rec)
        res = cur.execute(f"SELECT numbers_count FROM users WHERE id = {self.uid}").fetchone()
        if res:
            cur.execute(f"UPDATE users SET numbers_count={res[0] + 1} WHERE id={self.uid}")
        self.con.commit()
        for i in range(4):
            self.human_inp[i].setEnabled(False)
        self.answerB.setEnabled(False)
        self.answerK.setEnabled(False)
        self.comp_counter_label.setText(str(self.comp_counter))
        self.human_counter_label.setText(str(self.human_counter))
        info = InfoWindow(self, content=self.goal)
        if self.goal == 2:
            info.text_label.setText(info.text_label.text() + f"\n\nКомпьютер задумал: {self.comp_number}")
        info.show()

    def update_listing(self):
        self.listingTable.setRowCount(self.step_counter)
        self.listingTable.setColumnCount(13)
        for i in range(13):
            self.listingTable.setColumnWidth(i, 40)
        self.listingTable.setColumnWidth(6, 58)
        for i in range(self.step_counter):
            for j in range(6):
                cell = QTableWidgetItem(str(self.human_list[i][j]))
                cell.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                if j < 4:
                    cell.setBackground(QtGui.QColor("#FFE080"))
                else:
                    cell.setBackground(QtGui.QColor("#FFA0A0"))

                self.listingTable.setItem(i, j, cell)
            for j in range(6):
                cell = QTableWidgetItem(str(self.comp_list[i][j]))
                cell.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                if j < 4:
                    cell.setBackground(QtGui.QColor("#80E0FF"))
                else:
                    cell.setBackground(QtGui.QColor("#A0FFA0"))
                self.listingTable.setItem(i, j + 7, cell)
