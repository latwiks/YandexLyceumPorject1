import csv
import datetime
import sqlite3

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, \
    QLabel, QLineEdit, QInputDialog, QFileDialog

from changename import ChangeNameInterface
from hash_password import hash_password
from changepass import ChangePasswordInterface


class StudentInterface(QWidget):  # ученик (вход через main.py)
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle('Ученик')
        self.user_id = user_id
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute('select name from users where id=?', (self.user_id,))
        name = c.fetchone()[0]
        conn.close()
        self.layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap('images/student.png'))
        self.image_label.setFixedSize(QSize(100, 100))
        self.layout.addWidget(self.image_label, 0, Qt.AlignmentFlag.AlignHCenter)
        self.role = '[Ученик] '
        self.label2 = QLabel(self.role + name)
        self.layout.addWidget(self.label2, 0, Qt.AlignmentFlag.AlignHCenter)

        self.test_list = QComboBox()
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute("SELECT test_name FROM tests")
        tests = c.fetchall()
        for test_name in tests:
            self.test_list.addItem(test_name[0])
        conn.close()

        self.layout.addWidget(self.test_list)

        self.take_test_button = QPushButton("Пройти тест")
        self.take_test_button.clicked.connect(self.take_test)
        self.layout.addWidget(self.take_test_button)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Тест", "Процент успеха", "Ошибки", "Дата"])
        self.layout.addWidget(self.results_table)

        self.fetch_results_button = QPushButton("Посмотреть мои результаты")
        self.fetch_results_button.clicked.connect(self.fetch_results)
        self.layout.addWidget(self.fetch_results_button)

        self.setLayout(self.layout)
        self.question_widgets = []
        self.finish_test_button = QPushButton("Закончить тест")
        self.finish_test_button.clicked.connect(self.finish_test)
        self.finish_test_button.hide()

        self.save_to_csv_button = QPushButton("Сохранить результаты в CSV")
        self.save_to_csv_button.clicked.connect(self.save_to_csv)
        self.layout.addWidget(self.save_to_csv_button)

        self.change_name_button = QPushButton("Сменить имя")
        self.change_name_button.clicked.connect(self.change_name)
        self.layout.addWidget(self.change_name_button)

        self.change_password_button = QPushButton("Сменить пароль")
        self.change_password_button.clicked.connect(self.change_password)
        self.layout.addWidget(self.change_password_button)

        self.delete_profile_button = QPushButton("Удалить свой профиль")
        self.delete_profile_button.clicked.connect(self.delete_me)
        self.layout.addWidget(self.delete_profile_button)
        self.fetch_results()

    def change_name(self):  # сменить имя
        self.change_name_dialog = ChangeNameInterface(self.user_id, self.role, self.label2)
        if self.change_name_dialog.exec():
            QMessageBox.information(self, "Успех", "Имя успешно изменено!")

    def save_to_csv(self):  # сохранить свои результаты в файлик csv
        if self.results_table.rowCount() > 0:
            filename = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "CSV (*.csv)")[0]
            if filename:
                with open(filename, mode='w') as csv_file:
                    writer = csv.writer(csv_file)
                    header = [self.results_table.horizontalHeaderItem(i).text() for i in
                              range(self.results_table.columnCount())]
                    writer.writerow(header)
                    for row in range(self.results_table.rowCount()):
                        rowdata = []
                        for column in range(self.results_table.columnCount()):
                            item = self.results_table.item(row, column)
                            if item is not None:
                                rowdata.append(item.text())
                            else:
                                rowdata.append('')
                        writer.writerow(rowdata)
                QMessageBox.information(self, "Сохранение успешно завершено",
                                        "Результаты успешно сохранены в файл " + filename)
        else:
            QMessageBox.warning(self, "Ошибка", "Таблица пуста.")

    def delete_me(self):  # удалить профиль
        reply = QMessageBox.question(self, 'Подтвердить удаление',
                                     'Вы уверены, что хотите удалить свой профиль?', QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            password, ok = QInputDialog.getText(self, 'Проверка пароля',
                                                'Введите ваш пароль:', QLineEdit.Password)
            if ok:
                conn = sqlite3.connect('test.db')
                c = conn.cursor()
                c.execute("SELECT password FROM users WHERE id=?", (self.user_id,))
                correct_password = c.fetchone()
                if correct_password and correct_password[0] == hash_password(password):
                    try:
                        c.execute("DELETE FROM users WHERE id=?", (self.user_id,))
                        c.execute("delete from results where user_id=?", (self.user_id,))
                        conn.commit()
                        QMessageBox.information(self, 'Удалено',
                                                'Вы успешно удалили свой профиль')
                        conn.close()
                        self.close()

                    except sqlite3.Error as e:
                        print(f"Ошибка: {e}")
                else:
                    QMessageBox.critical(self, 'Ошибка', 'Пароль неверный')

    def change_password(self):  # сменить пароль
        self.change_password_dialog = ChangePasswordInterface(self.user_id)
        if self.change_password_dialog.exec():
            QMessageBox.information(self, "Успех", "Пароль успешно изменён!")

    def fetch_results(self):  # перезагрузить результаты
        try:
            conn = sqlite3.connect('test.db')
            c = conn.cursor()
            c.execute("""
                      SELECT tests.test_name, results.score, results.errors, results.completed_at 
                      FROM results 
                      INNER JOIN tests ON results.test_id = tests.id
                      WHERE results.user_id=?
                      ORDER BY results.completed_at DESC
                      """, (self.user_id,))
            results = c.fetchall()

            while self.results_table.rowCount() > 0:
                self.results_table.removeRow(0)

            for i, (test_name, score, errors, date) in enumerate(results):
                row_data = [test_name, str(score), str(errors), date]
                self.results_table.insertRow(i)
                for j, data in enumerate(row_data):
                    self.results_table.setItem(i, j, QTableWidgetItem(data))
            conn.close()

        except Exception as e:
            print(f"Не удалось получить результаты: {e}")

    def take_test(self):  # взять тест
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        test_name = self.test_list.currentText().strip()

        if len(test_name) == 0:
            QMessageBox.warning(self, "Взять тест", "Пожалуйста, выберите тест!")
            return

        for widget in self.question_widgets:
            self.layout.removeWidget(widget)
            widget.setParent(None)
        self.question_widgets.clear()

        c.execute("SELECT id FROM tests WHERE test_name=?", (test_name,))
        test_id = c.fetchone()
        if test_id:
            c.execute("SELECT id, content FROM questions WHERE test_id=?", (test_id[0],))
            questions = c.fetchall()
            for question_id, question_content in questions:
                question_widget = QuestionWidget(question_content, question_id)
                self.layout.addWidget(question_widget)
                self.question_widgets.append(question_widget)

        self.layout.addWidget(self.finish_test_button)
        self.finish_test_button.show()
        conn.close()

    def finish_test(self):  # закончить тест
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        correct_answers = sum([q.correct_answer == q.answer_input.text() for q in self.question_widgets])
        total_questions = len(self.question_widgets)
        incorrect_answers = total_questions - correct_answers

        score = (correct_answers / total_questions) * 100

        completed_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            test_name = self.test_list.currentText().strip()
            c.execute("SELECT id FROM tests WHERE test_name=?", (test_name,))
            test_id = c.fetchone()[0]
            c.execute("SELECT author_id FROM tests WHERE test_name=?", (test_name,))
            author_id = c.fetchone()[0]
            c.execute(
                "INSERT INTO results (user_id, test_id, author_id, score, errors, completed_at) VALUES (?, ?, ?, ?, ?, ?)",
                (self.user_id, test_id, author_id, score, incorrect_answers, completed_at))
            conn.commit()
            QMessageBox.information(self, "Рекорд",
                                    f"Ты ответил правильно на {correct_answers} из {total_questions} вопросов!\n"
                                    f"Твой процент успеха: {round(score, 2)}%")
            for widget in self.question_widgets:
                self.layout.removeWidget(widget)
                widget.setParent(None)
            self.question_widgets.clear()
            conn.close()

        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить результаты в бд!")

        finally:
            self.finish_test_button.hide()


class QuestionWidget(QWidget):
    def __init__(self, question_content, question_id):
        super(QuestionWidget, self).__init__()

        self.layout = QVBoxLayout()

        self.question_label = QLabel(question_content)
        self.answer_input = QLineEdit()

        self.layout.addWidget(self.question_label)
        self.layout.addWidget(self.answer_input)

        self.setLayout(self.layout)
        self.question_id = question_id
        self.correct_answer = None
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        # пояснялка к низу: возможно в будущем появятся варианты ответов, поэтому пока что запихнул is_correct = 1 везде
        c.execute("SELECT content FROM answers WHERE question_id=? AND is_correct=1", (question_id,))
        answer = c.fetchone()
        if answer:
            self.correct_answer = answer[0]
        conn.close()
