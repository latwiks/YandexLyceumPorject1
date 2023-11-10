import re
import sqlite3

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox, QLabel, QPushButton, QComboBox, QVBoxLayout, QWidget, QLineEdit, QInputDialog
from adminwidgets import EditTestWidget, ChangePasswordToUser, ChangeNameToUser, ChangeLoginToUser
from changename import ChangeNameInterface
from changepass import ChangePasswordInterface
from hash_password import hash_password
from errors import *

# айди не менять
ROLE_ID_ADMIN = 2
ROLE_ID_TEACHER = 3
ROLE_ID_STUDENT = 4


class AdminInterface(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.setFixedSize(300, 850)
        self.user_id = user_id
        self.setWindowTitle('Админ-панель')
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute('select name from users where id=?', (self.user_id,))
        name = c.fetchone()[0]
        conn.close()
        self.layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap('images/admin.png'))
        self.image_label.setFixedSize(QSize(100, 100))
        self.layout.addWidget(self.image_label, 0, Qt.AlignmentFlag.AlignHCenter)
        self.role = '[Администратор] '
        self.label2 = QLabel(self.role + name)
        self.layout.addWidget(self.label2, 0, Qt.AlignmentFlag.AlignHCenter)

        self.user_list = QComboBox()
        self.fetch_users_button = QPushButton("Найти пользователей")
        self.fetch_users_button.clicked.connect(self.fetch_users)
        self.role_list = QComboBox()
        self.fetch_roles_button = QPushButton("Найти роли")
        self.fetch_roles_button.clicked.connect(self.fetch_roles)
        self.assign_role_button = QPushButton("Назначить роль")
        self.assign_role_button.clicked.connect(self.assign_role)
        self.change_pass_to_user_button = QPushButton("Сменить пароль пользователю")
        self.change_pass_to_user_button.clicked.connect(self.change_pass_to_user)
        self.change_login_to_user_button = QPushButton("Сменить логин пользователю")
        self.change_login_to_user_button.clicked.connect(self.change_login_to_user)
        self.change_name_to_user_button = QPushButton("Сменить ФИО пользователю")
        self.change_name_to_user_button.clicked.connect(self.change_name_to_user)
        self.remove_user_button = QPushButton("Удалить пользователя")
        self.remove_user_button.clicked.connect(self.remove_user)
        self.layout.addWidget(QLabel("Пользователи:"))
        self.layout.addWidget(self.user_list)
        self.layout.addWidget(self.fetch_users_button)
        self.layout.addWidget(self.change_name_to_user_button)
        self.layout.addWidget(self.change_login_to_user_button)
        self.layout.addWidget(self.change_pass_to_user_button)
        self.layout.addWidget(self.role_list)
        self.layout.addWidget(self.fetch_roles_button)
        self.layout.addWidget(self.assign_role_button)
        self.layout.addWidget(self.remove_user_button)
        self.test_list = QComboBox()
        self.fetch_test_button = QPushButton("Найти тесты")
        self.fetch_test_button.clicked.connect(self.fetch_test)
        self.edit_test_button = QPushButton("Изменить тест")
        self.edit_test_button.clicked.connect(self.edit_test)
        self.delete_test_button = QPushButton("Удалить тест")
        self.delete_test_button.clicked.connect(self.delete_test)
        self.layout.addWidget(QLabel("Тесты:"))
        self.layout.addWidget(self.test_list)
        self.layout.addWidget(self.fetch_test_button)
        self.layout.addWidget(self.edit_test_button)
        self.layout.addWidget(self.delete_test_button)

        self.layout.addWidget(QLabel('Добавить пользователя:'))
        self.new_user_name_input = QLineEdit()
        self.new_user_name_input.setPlaceholderText("ФИО")
        self.layout.addWidget(self.new_user_name_input)
        self.new_user_input = QLineEdit()
        self.new_user_input.setPlaceholderText("Логин")
        self.layout.addWidget(self.new_user_input)
        self.password = QLineEdit()
        self.password.setPlaceholderText("Пароль")
        self.layout.addWidget(self.password)
        self.role_choice = QComboBox()
        self.role_choice.addItem("Ученик", ROLE_ID_STUDENT)
        self.role_choice.addItem("Учитель", ROLE_ID_TEACHER)

        self.role_choice.addItem("Администратор", ROLE_ID_ADMIN)
        self.layout.addWidget(self.role_choice)
        self.add_user_button = QPushButton('Добавить пользователя')
        self.add_user_button.clicked.connect(self.add_user)
        self.layout.addWidget(self.add_user_button)

        self.change_name_button = QPushButton("Сменить имя")
        self.change_name_button.clicked.connect(self.change_name)
        self.layout.addWidget(self.change_name_button)

        self.change_password_button = QPushButton("Сменить пароль")
        self.change_password_button.clicked.connect(self.change_password)
        self.layout.addWidget(self.change_password_button)

        self.delete_profile_button = QPushButton("Удалить свой профиль")
        self.delete_profile_button.clicked.connect(self.delete_me)
        self.layout.addWidget(self.delete_profile_button)
        self.fetch_users()
        self.fetch_roles()
        self.fetch_test()

        self.setLayout(self.layout)

    # Фановые штучки

    def change_name_to_user(self):  # изменить фио пользователю от имени админа
        if not self.user_list.currentText():
            QMessageBox.warning(self, "Изменить имя пользователю", "Ничего не выбрано.")
            return
        current_user = self.user_list.currentText()
        my_login = sqlite3.connect('test.db').cursor().execute('select username from users where id=?',
                                                               (self.user_id,)).fetchone()[0]
        if current_user == my_login:
            QMessageBox.warning(self, "Изменить пароль пользователю", "Вы не можете изменить своё ФИО так.")
            return
        self.change_name_dialog_2 = ChangeNameToUser(current_user)
        if self.change_name_dialog_2.exec():
            QMessageBox.information(self, "Успех", "Имя изменено успешно!")

    def change_pass_to_user(self):  # изменить пароль пользователю от имени админа
        if not self.user_list.currentText():
            QMessageBox.warning(self, "Изменить пароль пользователю", "Ничего не выбрано.")
            return
        current_user = self.user_list.currentText()
        my_login = sqlite3.connect('test.db').cursor().execute('select username from users where id=?',
                                                               (self.user_id,)).fetchone()[0]
        if current_user == my_login:
            QMessageBox.warning(self, "Изменить пароль пользователю", "Вы не можете изменить свой пароль так.")
            return
        self.change_password_dialog_2 = ChangePasswordToUser(current_user)
        if self.change_password_dialog_2.exec():
            QMessageBox.information(self, "Успех", "Пароль изменён успешно!")

    def change_login_to_user(self):  # изменить логин пользователя от имени админа
        if not self.user_list.currentText():
            QMessageBox.warning(self, "Изменить логин пользователю", "Ничего не выбрано.")
            return
        my_login = sqlite3.connect('test.db').cursor().execute('select username from users where id=?',
                                                               (self.user_id,)).fetchone()[0]
        if self.user_list.currentText() == my_login:
            QMessageBox.warning(self, "Изменить логин пользователю", "Вы не можете изменить свой логин.")
            return
        current_user = self.user_list.currentText()
        self.change_login_to_user_dialog_2 = ChangeLoginToUser(current_user)
        if self.change_login_to_user_dialog_2.exec():
            QMessageBox.information(self, "Успех", "логин изменён успешно!")
        self.fetch_users()

    # Полезности

    def change_name(self):  # изменение своего фио
        self.change_name_dialog = ChangeNameInterface(self.user_id, self.role, self.label2)
        if self.change_name_dialog.exec():
            QMessageBox.information(self, "Успех", "Имя успешно изменено!")

    def change_password(self):  # изменение своего пароля
        self.change_password_dialog = ChangePasswordInterface(self.user_id)
        if self.change_password_dialog.exec():
            QMessageBox.information(self, "Успех", "Пароль изменён успешно!")

    def fetch_test(self):  # кнопка для обновления списка тестов
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute("SELECT test_name FROM tests")
        tests = c.fetchall()
        self.test_list.clear()
        for test in tests:
            self.test_list.addItem(test[0])
        conn.close()

    def edit_test(self):  # кнопка для изменения выбранного теста
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        test_name = self.test_list.currentText()
        if not test_name:
            QMessageBox.warning(self, "Измененить тест", "Ничего не выбрано.")
            return

        c.execute("SELECT id FROM tests WHERE test_name=?", (test_name,))
        test_id = c.fetchone()

        self.edit_test_widget = EditTestWidget(test_name, test_id[0])
        self.edit_test_widget.show()
        conn.close()

    def fetch_users(self):  # кнопка для обновления списка пользователей
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute("SELECT username FROM users")
        users = c.fetchall()
        self.user_list.clear()
        for user in users:
            self.user_list.addItem(user[0])
        conn.close()

    def fetch_roles(self):  # кнопка для обновления списка ролей (хз, зачем ее добавил.. но пусть будет, вдруг сделаю добавление ролей админом в будущем :))
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute("SELECT role_name FROM roles")
        roles = c.fetchall()
        self.role_list.clear()
        for role in roles:
            self.role_list.addItem(role[0])
        conn.close()

    def assign_role(self):  # Назначить роль
        if not self.user_list.currentText():
            QMessageBox.warning(self, "Ошибка", "Поле пользователя не должно быть пустым")
            return
        if not self.role_list.currentText():
            QMessageBox.warning(self, "Ошибка", "Поле ролей не должно быть пустым")
            return
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute('select username from users where id=?', (self.user_id,))
        my_login = c.fetchone()[0]
        user = self.user_list.currentText()
        role = self.role_list.currentText()
        if user == my_login:
            QMessageBox.warning(self, "Ошибка", "Вы не можете назначить себе роль")
            return
        c.execute("UPDATE users SET role_id=(SELECT id FROM roles WHERE role_name = ?) WHERE username = ?",
                  (role, user))
        conn.commit()
        QMessageBox.information(self, "Успех", f"Вы успешно назначили роль {role} пользователю {user}")
        conn.close()

    def remove_user(self):  # удаление пользователя от админа (не удаляются тесты и результаты, вдруг разбанят)
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        user = self.user_list.currentText()
        c.execute("SELECT * FROM users WHERE username=?", (user,))
        p = c.fetchall()
        if p and p[0][0] == self.user_id:
            QMessageBox.warning(self, "Удалить пользователя", "Вы не можете удалить себя так!")
        elif p and len(user) > 0:
            try:
                c.execute("DELETE FROM users WHERE username=?", (user,))
                conn.commit()
                QMessageBox.information(self, "Удалить пользователя", "Пользователь удалён!")
                conn.close()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Удалить пользователя", "Не удалось удалить пользователя!")
        else:
            QMessageBox.warning(self, "Удалить пользователя", "Поле пользователя не должно быть пустым!")

    def delete_test(self):  # удаление выбранного теста
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        delete_test = self.test_list.currentText().strip()
        if len(delete_test) == 0:
            QMessageBox.warning(self, "Удалить тест", "Название теста не должно быть пустым!")
            return
        try:
            c.execute("DELETE FROM tests WHERE test_name = (?)", (delete_test,))
            conn.commit()
            QMessageBox.information(self, "Удалить тест", "Тест удалён!")
            conn.close()
            self.test_list.clear()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Удалить тест", "Не удалось удалить тест!")

    def delete_me(self):  # удаление себя
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
                    try:
                        c.execute("DELETE FROM users WHERE id=?", (self.user_id,))
                        conn.commit()
                        QMessageBox.information(self, 'Удалено',
                                                'Вы успешно удалили свой профиль')
                        conn.close()
                        self.close()

                    except sqlite3.Error as e:
                        print(f"An error occurred: {e}")
                else:
                    QMessageBox.critical(self, 'Ошибка', 'Пароль неверный')

    def add_user(self):  # добавление пользователя от имени админа
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        username = self.new_user_input.text().strip()
        password = self.password.text().strip()
        fio = self.new_user_name_input.text().strip()

        if len(username) == 0 or len(password) == 0 or len(fio) == 0:
            QMessageBox.warning(self, "Добавить пользователя", "Пустое, пароль или ФИО")
        else:
            try:
                if len(fio.split()) < 2:
                    raise LengthError("Введите ФИО (можно без отчества)")

                if len(username) < 3:
                    raise LengthError("Логин должен содержать не менее 3 символов!")
                # проверка длины пароля
                if len(password) < 8:
                    raise LengthError("Пароль должен содержать не менее 8 символов!")

                # проверка на русские буквы в логине и пароле
                if re.search('[а-яА-Я]', username) or re.search('[а-яА-Я]', password):
                    raise RussianCharError("Логин и пароль не должны содержать русские буквы!")

                # проверка на наличие как минимум одной заглавной и строчной буквы
                if not re.search('[A-Z]', password) or not re.search('[a-z]', password):
                    raise CapitalLetterError("Пароль должен содержать хотя бы одну заглавную и одну строчную букву!")

                # проверка на наличие числа
                if not re.search('[0-9]', password):
                    raise NumberError("Пароль должен содержать хотя бы одну цифру!")

                # проверка на наличие специального символа
                if not re.search('[!@#$%^&*(),.?":{}|<>]', password):
                    raise SpecialCharError("Пароль должен содержать хотя бы один специальный символ!")
                # проверка на существование пользователя в бд
                c.execute("SELECT * FROM users WHERE username=?", (username.lower(),))
                if c.fetchone():
                    raise LoginAlreadyExists("Пользователь уже существует!")

                if "12345" in password or "qwerty" in password.lower():
                    raise DifferentPassword("Слишком простой пароль!")

                role_id = self.role_choice.currentData()
                c.execute("INSERT INTO users (name, username, password, role_id) VALUES (?, ?, ?)",
                          (fio, username, hash_password(password), role_id))
                conn.commit()
                QMessageBox.information(self, "Регистрация", "Регистрация произошла успешно!")
                conn.close()

            except (
                    LengthError, RussianCharError, CapitalLetterError, NumberError, SpecialCharError,
                    LoginAlreadyExists, DifferentPassword) as e:
                QMessageBox.warning(self, "Регистрация", str(e))

            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Регистрация", "Такое имя уже существует!")

            except sqlite3.Error:
                QMessageBox.warning(self, "Регистрация", "Ошибка, в базе данных!")
