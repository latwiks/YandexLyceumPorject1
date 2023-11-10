import re
import sqlite3
from PyQt5.QtWidgets import QMessageBox, QDialogButtonBox, QLineEdit, QFormLayout, QDialog
from hash_password import hash_password
from errors import *

conn = sqlite3.connect('test.db')
c = conn.cursor()


class ChangePasswordInterface(QDialog):
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle('Сменить пароль')

        self.user_id = user_id
        self.layout = QFormLayout()

        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        self.layout.addRow("Старый пароль", self.old_password)

        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.layout.addRow("Новый пароль", self.new_password)

        self.confirm_new_password = QLineEdit()
        self.confirm_new_password.setEchoMode(QLineEdit.Password)
        self.layout.addRow("Подтвердите новый пароль", self.confirm_new_password)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.change_password)
        self.buttons.rejected.connect(self.reject)

        self.layout.addRow(self.buttons)

        self.setLayout(self.layout)

    def change_password(self):
        old_password_input = self.old_password.text()
        new_password_input = self.new_password.text()
        confirm_new_password_input = self.confirm_new_password.text()

        c.execute("SELECT password FROM users WHERE id=?", (self.user_id,))
        actual_old_password = c.fetchone()[0]

        if hash_password(old_password_input) != actual_old_password:
            QMessageBox.warning(self, "Ошибка", "Старый пароль неверный!")
            return

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

            c.execute("UPDATE users SET password=? WHERE id=?", (hashed_new_password, self.user_id))
            conn.commit()
            self.accept()
        except (LengthError, RussianCharError, CapitalLetterError, NumberError, SpecialCharError) as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Произошла ошибка при смене пароля!")
