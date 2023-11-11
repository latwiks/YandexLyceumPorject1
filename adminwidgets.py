import re
import sqlite3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QFormLayout, QHBoxLayout, \
    QDialog, QDialogButtonBox

from errors import *
from hash_password import hash_password


class EditTestWidget(QWidget):  # виджет для изменения выбранного теста (в adminint.py)
    def __init__(self, test_name, test_id):
        super().__init__()

        self.setWindowTitle(f"Изменить тест {test_name}")

        self.test_id = test_id
        self.test_name = test_name

        self.layout = QVBoxLayout()
        self.test_name_input = QLineEdit(test_name)
        self.layout.addWidget(self.test_name_input)
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute("SELECT id, content FROM questions WHERE test_id=?", (test_id,))
        self.question_widgets = [QuestionEditWidget(question_id, content, self) for question_id, content in
                                 c.fetchall()]
        for widget in self.question_widgets:
            self.layout.addWidget(widget)
        conn.close()

        self.save_button = QPushButton('Сохранить')
        self.save_button.clicked.connect(self.save)
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)

        self.new_question_input = QLineEdit()
        self.new_question_input.setPlaceholderText('Вопрос')
        self.layout.addWidget(self.new_question_input)

        self.new_answer_input = QLineEdit()
        self.new_answer_input.setPlaceholderText('Ответ')
        self.layout.addWidget(self.new_answer_input)

        self.new_question_button = QPushButton('Добавить вопрос')
        self.new_question_button.clicked.connect(self.add_question)
        self.layout.addWidget(self.new_question_button)

    def add_question(self):  # добавить вопрос
        new_question_text = self.new_question_input.text().strip()
        new_answer_text = self.new_answer_input.text().strip()

        if len(new_question_text) == 0 or len(new_answer_text) == 0:
            QMessageBox.warning(self, "Добавить вопрос", "Поля не должны быть пустыми!")
        else:
            conn = sqlite3.connect('test.db')
            c = conn.cursor()
            c.execute("INSERT INTO questions (content, test_id) VALUES (?, ?)", (new_question_text, self.test_id))
            question_id = c.lastrowid

            c.execute("INSERT INTO answers (content, question_id) VALUES (?, ?)",
                      (new_answer_text, question_id))
            conn.commit()

            QMessageBox.information(self, "Добавить вопрос", f"Вопрос к тесту '{self.test_name}' добавлен успешно!")
            conn.close()

    def save(self):  # сохранить тест
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        new_test_name = self.test_name_input.text().strip()
        c.execute("UPDATE tests SET test_name=? WHERE id=?", (new_test_name, self.test_id))

        for question_widget in self.question_widgets:
            if question_widget.parent() is not None:
                question_widget.save()

        conn.commit()
        QMessageBox.information(self, "Изменить тест", f"Изменения к тесту '{self.test_name}' были применены успешно!")
        self.close()
        conn.close()


class QuestionEditWidget(QWidget):  # виджет для вопросов
    def __init__(self, question_id, content, parent=None):
        super().__init__(parent)

        self.question_id = question_id
        self.layout = QFormLayout()

        self.question_input = QLineEdit(content)
        self.question_input.setPlaceholderText('Вопрос')
        self.layout.addRow(f"Вопрос:", self.question_input)
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute("SELECT id, content FROM answers WHERE question_id=?", (question_id,))
        self.answer_widgets = [AnswerEditWidget(answer_id, content) for answer_id, content in
                               c.fetchall()]
        for answer_widget in self.answer_widgets:
            self.layout.addRow("Ответ:", answer_widget)
        conn.close()
        self.delete_button = QPushButton('Удалить вопрос')
        self.delete_button.clicked.connect(self.delete)
        self.layout.addRow(self.delete_button)

        self.setLayout(self.layout)

    def delete(self):  # удаление вопроса
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute("DELETE FROM questions WHERE id=?", (self.question_id,))
        c.execute("DELETE FROM answers WHERE question_id=?", (self.question_id,))
        conn.commit()
        conn.close()
        self.setParent(None)

    def save(self):  # сохранение вопроса
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        new_content = self.question_input.text().strip()
        c.execute("UPDATE questions SET content=? WHERE id=?", (new_content, self.question_id))
        for answer_widget in self.answer_widgets:
            answer_widget.save()
        conn.close()


class AnswerEditWidget(QWidget):
    def __init__(self, answer_id, content):
        super().__init__()

        self.answer_id = answer_id

        self.layout = QHBoxLayout()
        self.answer_input = QLineEdit(content)
        self.layout.addWidget(self.answer_input)
        self.setLayout(self.layout)

    def save(self):  # сохранение ответа
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        new_content = self.answer_input.text().strip()
        c.execute("UPDATE answers SET content=? WHERE id=?", (new_content, self.answer_id))
        conn.close()


class ChangePasswordToUser(QDialog):  # изменение пароля пользователю от имени админа
    def __init__(self, login):
        super().__init__()
        self.setFixedSize(200, 100)
        self.login = login
        self.setWindowTitle(f"Сменить пароль пользователю {login}")
        self.layout = QVBoxLayout()
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Пароль")
        self.layout.addWidget(self.new_password_input)
        self.confirm_new_password_input = QLineEdit()
        self.confirm_new_password_input.setPlaceholderText("Подтверждение пароля")
        self.layout.addWidget(self.confirm_new_password_input)
        self.confirm_button = QPushButton("Подтвердить")
        self.confirm_button.clicked.connect(self.change_password)
        self.layout.addWidget(self.confirm_button)
        self.setLayout(self.layout)

    def change_password(self):  # собственно функция для изменения
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        new_password_input = self.new_password_input.text()
        confirm_new_password_input = self.confirm_new_password_input.text()

        if new_password_input != confirm_new_password_input:
            QMessageBox.warning(self, "Ошибка", "Новые пароли не совпадают!")
            return

        try:
            if len(new_password_input) < 8:
                raise LengthError("Пароль должен содержать не менее 8 символов!")
            if re.search('[а-яА-Я]', new_password_input):
                raise RussianCharError("Пароль не должен содержать русские буквы!")
            if not re.search('[A-Z]', new_password_input) or not re.search('[a-z]', new_password_input):
                raise CapitalLetterError("Пароль должен содержать хотя бы одну заглавную и одну строчную букву!")
            if not re.search('[0-9]', new_password_input):
                raise NumberError("Пароль должен содержать хотя бы одну цифру!")
            if not re.search('[!@#$%^&*(),.?":{}|<>]', new_password_input):
                raise SpecialCharError("Пароль должен содержать хотя бы один специальный символ!")
            if "12345" in new_password_input or "qwerty" in new_password_input.lower():
                raise DifferentPassword("Слишком простой пароль!")

            hashed_new_password = hash_password(new_password_input)

            c.execute("UPDATE users SET password=? WHERE username=?", (hashed_new_password, self.login))
            conn.commit()
            self.accept()
        except (LengthError, RussianCharError, CapitalLetterError, NumberError, SpecialCharError) as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Произошла ошибка при смене пароля!")


class ChangeNameToUser(QDialog):  # изменить фио пользователю от имени админа
    def __init__(self, login):
        super().__init__()
        self.setWindowTitle(f"Сменить имя пользователю {login}")
        self.setFixedSize(350, 100)
        self.login = login
        self.layout = QFormLayout()

        self.new_name = QLineEdit()
        self.new_name.setEchoMode(QLineEdit.Password)
        self.new_name.setPlaceholderText("Пример: Иванов Иван Иванович")
        self.layout.addRow("Новое ФИО", self.new_name)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.change_name)
        self.buttons.rejected.connect(self.reject)

        self.layout.addRow(self.buttons)

        self.setLayout(self.layout)

    def change_name(self):  # ф-ия для этого
        new_name = self.new_name.text().strip()
        conn = sqlite3.connect("test.db")
        c = conn.cursor()

        if len(new_name.split()) < 2:
            QMessageBox.warning(self, "Ошибка", "Введите полностью ФИО (можно без отчества)!")
            return

        c.execute("UPDATE users SET name=? WHERE username=?", (new_name, self.login))
        conn.commit()
        self.accept()
        conn.close()


class ChangeLoginToUser(QDialog):  # изменить логин юзеру от имени админа
    def __init__(self, login):
        super().__init__()
        self.setWindowTitle(f"Сменить логин пользователю {login}")
        self.setFixedSize(350, 100)
        self.login = login
        self.layout = QFormLayout()

        self.new_name = QLineEdit()
        self.new_name.setPlaceholderText("Пример: student")
        self.layout.addRow("Новый логин", self.new_name)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.change_name)
        self.buttons.rejected.connect(self.reject)

        self.layout.addRow(self.buttons)

        self.setLayout(self.layout)

    def change_name(self):  # ф-ия
        new_name = self.new_name.text().strip()
        conn = sqlite3.connect("test.db")
        c = conn.cursor()

        if len(new_name) < 3:
            QMessageBox.warning(self, "Ошибка", "Логин меньше 3х символов!")
            return
        if re.search('[а-яА-Я]', new_name):
            QMessageBox.warning(self, "Ошибка", "Логин не должен содержать русские буквы!")
        c.execute("UPDATE users SET username=? WHERE username=?", (new_name, self.login))
        conn.commit()
        self.accept()
        conn.close()
