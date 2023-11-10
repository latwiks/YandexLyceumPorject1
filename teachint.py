import csv
import sqlite3

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, \
    QMessageBox, QInputDialog, QFileDialog, QLabel

from changename import ChangeNameInterface
from adminwidgets import EditTestWidget
from hash_password import hash_password
from changepass import ChangePasswordInterface


class TeacherInterface(QWidget):
    def __init__(self, user_id, author_id):
        super().__init__()
        self.user_id = user_id
        self.author_id = author_id
        self.setWindowTitle('Учитель')
        self.layout = QFormLayout()
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute('select name from users where id=?', (self.user_id,))
        self.name = c.fetchone()[0]
        conn.close()
        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap('images/teacher.png'))
        self.image_label.setFixedSize(QSize(100, 100))
        self.layout.addWidget(self.image_label)
        self.role = '[Учитель] '
        self.label2 = QLabel(self.role + self.name)
        self.layout.addWidget(self.label2)
        self.test_name_input = QLineEdit()
        self.layout.addRow("Имя теста:", self.test_name_input)

        self.add_question_button = QPushButton("Добавить вопрос")
        self.add_question_button.clicked.connect(self.add_question)
        self.layout.addWidget(self.add_question_button)

        self.question_input = QLineEdit()
        self.layout.addRow("Вопрос:", self.question_input)

        self.answer_input = QLineEdit()
        self.layout.addRow("Ответ:", self.answer_input)

        self.finish_test_button = QPushButton("Завершить работу с тестом")
        self.finish_test_button.clicked.connect(self.finish_test)
        self.layout.addWidget(self.finish_test_button)
        self.setLayout(self.layout)
        self.fetch_tests_button = QPushButton("Отобразить мои тесты")
        self.fetch_tests_button.clicked.connect(self.fetch_tests)
        self.layout.addWidget(self.fetch_tests_button)

        self.test_list = QComboBox()
        self.layout.addWidget(self.test_list)

        self.edit_test_button = QPushButton("Изменить тест")
        self.edit_test_button.clicked.connect(self.edit_test)
        self.layout.addWidget(self.edit_test_button)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Ученик", "Тест", "Процент успеха", "Ошибки"])
        self.layout.addWidget(self.results_table)

        self.fetch_results_button = QPushButton("Отобразить результаты теста")
        self.fetch_results_button.clicked.connect(self.fetch_results)
        self.layout.addWidget(self.fetch_results_button)
        self.test_stats_button = QPushButton("Отобразить среднюю статистику")
        self.test_stats_button.clicked.connect(self.test_statistics)
        self.layout.addWidget(self.test_stats_button)
        self.save_as_csv_button = QPushButton("Сохранить как CSV")
        self.save_as_csv_button.clicked.connect(self.save_as_csv)
        self.layout.addWidget(self.save_as_csv_button
                              )
        self.change_name_button = QPushButton("Сменить имя")
        self.change_name_button.clicked.connect(self.change_name)
        self.layout.addWidget(self.change_name_button)

        self.change_password_button = QPushButton("Сменить пароль")
        self.change_password_button.clicked.connect(self.change_password)
        self.layout.addWidget(self.change_password_button)

        self.delete_profile_button = QPushButton("Удалить свой профиль")
        self.delete_profile_button.clicked.connect(self.delete_me)
        self.layout.addWidget(self.delete_profile_button)
        self.fetch_tests()

    def change_name(self):  # изменить свое фио
        self.change_name_dialog = ChangeNameInterface(self.user_id, self.role, self.label2)
        if self.change_name_dialog.exec():
            QMessageBox.information(self, "Успех", "Имя успешно изменено!")

    def save_as_csv(self):  # сохранить результаты теста в csv
        if self.results_table.rowCount() > 0:
            path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'CSV(*.csv)')
            if path:
                with open(path, mode='w', newline='') as f:
                    writer = csv.writer(f, dialect='excel')
                    header = []
                    for i in range(self.results_table.columnCount()):
                        header.append(self.results_table.horizontalHeaderItem(i).text())
                    writer.writerow(header)
                    for i in range(self.results_table.rowCount()):
                        row_data = []
                        for j in range(self.results_table.columnCount()):
                            data = self.results_table.item(i, j).text()
                            row_data.append(data)
                        writer.writerow(row_data)
                QMessageBox.information(self, "Сохранить как CSV", "Файл успешно сохранён!")
        else:
            QMessageBox.warning(self, "Ошибка", "Таблица пуста.")

    def change_password(self):  # сменить пароль
        self.change_password_dialog = ChangePasswordInterface(self.user_id)
        if self.change_password_dialog.exec():
            QMessageBox.information(self, "Успех", "Пароль изменён успешно!")

    def fetch_results(self):  # перезагрузить результаты теста
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        try:
            test_name = self.test_list.currentText()

            c.execute("SELECT id FROM tests WHERE test_name=?", (test_name,))
            test_id = c.fetchone()

            c.execute("""
                      SELECT users.username, tests.test_name, results.score, results.errors 
                      FROM results 
                      INNER JOIN users ON results.user_id = users.id
                      INNER JOIN tests ON results.test_id = tests.id
                      WHERE test_id=?
                      """, (test_id[0],))
            results = c.fetchall()

            print(f"Найдены результаты: {results}")  # debug print

            while self.results_table.rowCount() > 0:
                self.results_table.removeRow(0)

            for i, (username, test_name, score, errors) in enumerate(results):
                row_data = [username, test_name, str(score), str(errors)]
                self.results_table.insertRow(i)
                for j, data in enumerate(row_data):
                    self.results_table.setItem(i, j, QTableWidgetItem(data))

            print(f"Заполнена таблица с {self.results_table.rowCount()} строками")  # debug print
            conn.close()
            if self.results_table.rowCount() == 0:
                QMessageBox.warning(self, "Статистика", "В настоящее время нет прохождений этого теста")

        except Exception as e:
            print(f"Ошибка: {e}")  # debug print

    def delete_me(self):  # удалить профиль
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        reply = QMessageBox.question(self, 'Подтвердить удаление',
                                     'Вы уверены, что хотите удалить свой профиль?', QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            password, ok = QInputDialog.getText(self, 'Проверка пароля',
                                                'Введите ваш пароль:', QLineEdit.Password)
            if ok:
                c.execute("SELECT password FROM users WHERE id=?", (self.user_id,))
                correct_password = c.fetchone()
                if correct_password and correct_password[0] == hash_password(password):

                    c.execute("SELECT id FROM tests WHERE author_id=?", (self.user_id,))
                    tests = c.fetchall()

                    for test_id in tests:
                        c.execute("DELETE FROM results WHERE test_id=?", (test_id[0],))
                        c.execute("DELETE FROM questions WHERE test_id=?", (test_id[0],))
                        c.execute('SELECT id FROM questions WHERE test_id=?', (test_id[0],))

                        questions_ids = c.fetchall()

                        for question_id in questions_ids:
                            c.execute("DELETE FROM answers WHERE question_id=?", (question_id[0],))

                        c.execute("DELETE FROM answers WHERE author_id=?", (self.user_id,))
                    c.execute("DELETE FROM tests WHERE author_id=?", (self.user_id,))
                    c.execute("DELETE FROM users WHERE id=?", (self.user_id,))

                    conn.commit()
                    QMessageBox.information(self, 'Удалено',
                                            'Вы успешно удалили свой профиль')
                    conn.close()
                    self.close()

                else:
                    QMessageBox.critical(self, 'Ошибка', 'Пароль неверный')

    def edit_test(self):  # изменить выбранный тест
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        test_name = self.test_list.currentText()
        if not test_name:
            QMessageBox.warning(self, "Изменить тест", "Тест не выбран.")
            return

        c.execute("SELECT id FROM tests WHERE test_name=?", (test_name,))
        test_id = c.fetchone()

        self.edit_test_widget = EditTestWidget(test_name, test_id[0])
        self.edit_test_widget.show()
        conn.close()

    def fetch_tests(self):  # обновить список тестов
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute(f"SELECT test_name FROM tests WHERE author_id={self.user_id}")
        tests = c.fetchall()

        self.test_list.clear()

        for test_name in tests:
            self.test_list.addItem(test_name[0])
        conn.close()

    def test_statistics(self):  # средняя статистика тестов
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        test_name = self.test_list.currentText()
        if not test_name:
            QMessageBox.warning(self, "Статистика", "Тест не выбран.")
            return
        c.execute("SELECT tests.id, COUNT(results.score), AVG(results.score) FROM tests "
                  "LEFT JOIN results ON tests.id=results.test_id "
                  "WHERE tests.test_name=? GROUP BY tests.id ", (test_name,))

        statistics = c.fetchone()

        if statistics:
            test_id, test_attempts, avg_score = statistics
            if test_attempts == 0:
                QMessageBox.warning(self, "Статистика", "В настоящее время нет прохождений этого теста")
            else:
                QMessageBox.information(self, "Статистика",
                                        f"ID теста: {test_id}\n"
                                        f"Всего попыток: {test_attempts}\n"
                                        f"Средний балл: {round(avg_score, 2)}")
                conn.close()
        else:
            QMessageBox.warning(self, "Статистика", "Ошибка.")

    def add_question(self):  # добавить вопрос к тесту
        self.test_name_input.setEnabled(False)
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        test_name = self.test_name_input.text().strip()
        question = self.question_input.text().strip()
        answer = self.answer_input.text().strip()

        if len(test_name) == 0 or len(question) == 0 or len(answer) == 0:
            QMessageBox.warning(self, "Добавить вопрос", "Все поля должны быть заполнены!")
        else:
            try:
                c.execute("SELECT id FROM tests WHERE test_name=?", (test_name,))
                test_id = c.fetchone()
                if not test_id:
                    c.execute("INSERT INTO tests (test_name, author_id) VALUES (?, ?)", (test_name,
                                                                                         self.author_id))
                    test_id = c.lastrowid
                else:
                    test_id = test_id[0]

                c.execute("INSERT INTO questions (content, test_id) VALUES (?, ?)", (question, test_id))
                question_id = c.lastrowid

                c.execute("INSERT INTO answers (content, is_correct, question_id, author_id) VALUES (?, ?, ?, ?)",
                          (answer, True, question_id, self.user_id))
                conn.commit()

                QMessageBox.information(self, "Добавить вопрос", "Вопрос добавлен!")
                conn.close()

                self.question_input.clear()
                self.answer_input.clear()

            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Добавить вопрос", "Ошибка!")

    def finish_test(self):  # завершить работу с этим тестом
        self.test_name_input.clear()
        self.test_name_input.setEnabled(True)
        self.question_input.clear()
        self.answer_input.clear()
        QMessageBox.information(self, "Завершить тест", "Создание теста завершено!")
