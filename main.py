import re
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QFormLayout, \
    QLineEdit, QMessageBox, QComboBox
import sqlite3
from adminint import AdminInterface
from resint import ResultsInterface
from studint import StudentInterface
from teachint import TeacherInterface
from errors import *
from hash_password import hash_password

# Задача айди (не менять)

ROLE_ID_ADMIN = 2
ROLE_ID_TEACHER = 3
ROLE_ID_STUDENT = 4


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ТСОЛ")
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.label = QLabel("Добро пожаловать в ТСОЛ (Тестирующая Система От Латвикса)")
        self.layout.addWidget(self.label)
        self.login_button = QPushButton("Войти")
        self.layout.addWidget(self.login_button)
        self.register_button = QPushButton("Зарегистрироваться")
        self.layout.addWidget(self.register_button)
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)
        self.login_window = None
        self.register_window = None
        self.results_button = QPushButton("Результаты")
        self.layout.addWidget(self.results_button)

        self.results_button.clicked.connect(self.show_results)
        self.results_window = None

    def show_results(self):
        self.results_window = ResultsInterface()
        self.results_window.show()

    def login(self):
        self.login_window = LoginWindow(self)
        self.login_window.show()

    def register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()


class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowIcon(QIcon(""))
        self.setFixedSize(300, 100)
        self.main_window = main_window
        self.setWindowTitle("Вход")

        self.layout = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Пример: student")
        self.layout.addRow("Логин:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Пример: Qwert1234!")
        self.layout.addRow("Пароль:", self.password_input)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.authenticate)
        self.layout.addWidget(self.login_button)

        self.setLayout(self.layout)

    def authenticate(self):
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        username = self.username_input.text().strip().lower()
        password = self.password_input.text().strip()

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
        user = c.fetchone()

        if user:
            role_id = user[4]
            user_id = user[0]
            author_id = user_id
            self.window = None

            if role_id == ROLE_ID_TEACHER:
                self.window = TeacherInterface(user_id, author_id)
            elif role_id == ROLE_ID_STUDENT:
                self.window = StudentInterface(user_id)
            elif role_id == ROLE_ID_ADMIN:
                self.window = AdminInterface(user_id)
            else:
                QMessageBox.warning(self, "Вход", "Неизвестная роль!")
                return

            self.window.show()
            self.close()
            self.main_window.close()
            conn.close()

        else:
            QMessageBox.warning(self, "Вход", "Неправильное имя или пароль!")


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Регистрация")
        self.setFixedSize(500, 200)
        self.layout = QFormLayout()
        self.name = QLineEdit()
        self.name.setPlaceholderText("Пример: Иванов Иван Иванович")
        self.layout.addRow("ФИО:", self.name)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Пример: student")
        self.layout.addRow("Логин:", self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Пример: Qwert1234!")
        self.layout.addRow("Пароль:", self.password_input)

        self.password_input_2 = QLineEdit()
        self.password_input_2.setEchoMode(QLineEdit.Password)
        self.password_input_2.setPlaceholderText("Повтор пароля, пример: Qwert1234!")
        self.layout.addRow("Подтвердите пароль:", self.password_input_2)

        self.role_choice = QComboBox()
        self.role_choice.addItem("Ученик", ROLE_ID_STUDENT)
        self.role_choice.addItem("Учитель", ROLE_ID_TEACHER)

        self.role_choice.addItem("Администратор", ROLE_ID_ADMIN)
        self.layout.addRow("Роль:", self.role_choice)

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.clicked.connect(self.register)
        self.layout.addWidget(self.register_button)

        self.setLayout(self.layout)

    def register(self):
        try:
            conn = sqlite3.connect('test.db')
            c = conn.cursor()
            name = self.name.text().strip()
            username = self.username_input.text().strip().lower()
            password = self.password_input.text().strip()
            repeat_password = self.password_input_2.text().strip()
            if len(name.split()) < 2:
                raise LengthError("Введите ФИО полностью (можно без отчества)!")
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

            if password != repeat_password:
                raise PasswordsAreNotMatchingError("Пароли не совпадают!")

            if "12345" in password or "qwerty" in password.lower():
                raise DifferentPassword("Слишком простой пароль!")

            role_id = self.role_choice.currentData()
            c.execute("INSERT INTO users (name, username, password, role_id) VALUES (?, ?, ?, ?)",
                      (name, username, hash_password(password), role_id))
            conn.commit()
            QMessageBox.information(self, "Регистрация", "Регистрация произошла успешно!")
            conn.close()
            self.close()

        except (
                LengthError, RussianCharError, CapitalLetterError, NumberError, SpecialCharError,
                LoginAlreadyExists, PasswordsAreNotMatchingError, DifferentPassword) as e:
            QMessageBox.warning(self, "Регистрация", str(e))

        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Регистрация", "Такое имя уже существует!")

        except sqlite3.Error:
            QMessageBox.warning(self, "Регистрация", "Ошибка в базе данных!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    style = """
    QMainWindow {
        background-color:rgb(82, 82, 82);
    }
    QWidget {
        background-color:rgb(82, 82, 82);
    }
    QTextEdit {
        background-color:rgb(82, 82, 82);
        color: rgb(255, 255, 255);
    }
    QComboBox {
      color: rgb(255, 255, 255);
      background: rgb(100, 100, 100);
      border-width: 1px; border-radius: 4px;
      border-color: rgb(58, 58, 58);
      border-style: inset;
      padding: 2px 18px 2px 3px;
      selection-background-color: #D0D0D0;
      selection-color: #000000;
    }
    QComboBox:editable {
      background: rgb(100, 100, 100);
    }
    QComboBox:!editable,
    QComboBox::drop-down:editable,
    QComboBox:!editable:on,
    QComboBox::drop-down:editable:on {
      background: rgb(100, 100, 100);
    }
    QComboBox::drop-down {
      subcontrol-origin: padding;
      subcontrol-position: top right;
      border-left: none;
    }
    QComboBox::down-arrow {
      image: url(:/icons/18/ic_arrow_drop_down_black);
    }
    QComboBox QAbstractItemView {
      color: rgb(255, 255, 255);
      background: rgb(100, 100, 100);
      border: none;
    }
    QPushButton{
        border-style: solid;
        border-color: #050a0e;
        border-width: 1px;
        border-radius: 5px;
        color: #d3dae3;
        padding: 2px;
        background-color: #100E19;
    }
    QPushButton::default{
        border-style: solid;
        border-color: #050a0e;
        border-width: 1px;
        border-radius: 5px;
        color: rgb(82, 82, 82);
        padding: 2px;
        background-color: #151a1e;
    }
    QPushButton:hover{
        border-style: solid;
        border-top-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:1, stop:0 #D426BD, stop:0.4 #D426BD, stop:0.5 #100E19, stop:1 #100E19);
        border-bottom-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:1, stop:0 #100E19, stop:0.5 #100E19, stop:0.6 #D426BD, stop:1 #D426BD);
        border-left-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #D426BD, stop:0.3 #D426BD, stop:0.7 #100E19, stop:1 #100E19);
        border-right-color: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #D426BD, stop:0.3 #D426BD, stop:0.7 #100E19, stop:1 #100E19);
        border-width: 2px;
        border-radius: 1px;
        color: #d3dae3;
        padding: 2px;
    }
    QPushButton:pressed{
        border-style: solid;
        border-top-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:1, stop:0 #d33af1, stop:0.4 #d33af1, stop:0.5 #100E19, stop:1 #100E19);
        border-bottom-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:1, stop:0 #100E19, stop:0.5 #100E19, stop:0.6 #d33af1, stop:1 #d33af1);
        border-left-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #d33af1, stop:0.3 #d33af1, stop:0.7 #100E19, stop:1 #100E19);
        border-right-color: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #d33af1, stop:0.3 #d33af1, stop:0.7 #100E19, stop:1 #100E19);
        border-width: 2px;
        border-radius: 1px;
        color: #d3dae3;
        padding: 2px;
    }
    QLineEdit {
        border-width: 1px; border-radius: 4px;
        border-color: rgb(58, 58, 58);
        border-style: inset;
        padding: 0 8px;
        color: rgb(255, 255, 255);
        background:rgb(100, 100, 100);
        selection-background-color: rgb(187, 187, 187);
        selection-color: rgb(60, 63, 65);
    }
    QLabel {
        color:rgb(255,255,255);	
    }
    QProgressBar {
        text-align: center;
        color: rgb(240, 240, 240);
        border-width: 1px; 
        border-radius: 10px;
        border-color: rgb(58, 58, 58);
        border-style: inset;
        background-color:rgb(77,77,77);
    }
    QProgressBar::chunk {
        background-color: qlineargradient(spread:pad, x1:0.5, y1:0.7, x2:0.5, y2:0.3, stop:0 rgba(87, 97, 106, 255), stop:1 rgba(93, 103, 113, 255));
        border-radius: 5px;
    }
    QMenuBar {
        background:rgb(82, 82, 82);
    }
    QMenuBar::item {
        color:rgb(223,219,210);
        spacing: 3px;
        padding: 1px 4px;
        background: transparent;
    }
    
    QMenuBar::item:selected {
        background:rgb(115, 115, 115);
    }
    QMenu::item:selected {
        color:rgb(255,255,255);
        border-width:2px;
        border-style:solid;
        padding-left:18px;
        padding-right:8px;
        padding-top:2px;
        padding-bottom:3px;
        background:qlineargradient(spread:pad, x1:0.5, y1:0.7, x2:0.5, y2:0.3, stop:0 rgba(87, 97, 106, 255), stop:1 rgba(93, 103, 113, 255));
        border-top-color: qlineargradient(spread:pad, x1:0.5, y1:0.6, x2:0.5, y2:0.4, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
        border-right-color: qlineargradient(spread:pad, x1:0.4, y1:0.5, x2:0.6, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
        border-left-color: qlineargradient(spread:pad, x1:0.6, y1:0.5, x2:0.4, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(62, 62, 62, 255));
        border-bottom-color: rgb(58, 58, 58);
        border-bottom-width: 1px;
    }
    QMenu::item {
        color:rgb(223,219,210);
        background-color:rgb(78,78,78);
        padding-left:20px;
        padding-top:4px;
        padding-bottom:4px;
        padding-right:10px;
    }
    QMenu{
        background-color:rgb(78,78,78);
    }
    QTabWidget {
        color:rgb(0,0,0);
        background-color:rgb(247,246,246);
    }
    QTabWidget::pane {
            border-color: rgb(77,77,77);
            background-color:rgb(101,101,101);
            border-style: solid;
            border-width: 1px;
            border-radius: 6px;
    }
    QTabBar::tab {
        padding:2px;
        color:rgb(250,250,250);
        background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(77, 77, 77, 255), stop:1 rgba(97, 97, 97, 255));
        border-style: solid;
        border-width: 2px;
        border-top-right-radius:4px;
       border-top-left-radius:4px;
        border-top-color: qlineargradient(spread:pad, x1:0.5, y1:0.6, x2:0.5, y2:0.4, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(95, 92, 93, 255));
        border-right-color: qlineargradient(spread:pad, x1:0.4, y1:0.5, x2:0.6, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(95, 92, 93, 255));
        border-left-color: qlineargradient(spread:pad, x1:0.6, y1:0.5, x2:0.4, y2:0.5, stop:0 rgba(115, 115, 115, 255), stop:1 rgba(95, 92, 93, 255));
        border-bottom-color: rgb(101,101,101);
    }
    QTabBar::tab:selected, QTabBar::tab:last:selected, QTabBar::tab:hover {
        background-color:rgb(101,101,101);
        margin-left: 0px;
        margin-right: 1px;
    }
    QTabBar::tab:!selected {
            margin-top: 1px;
            margin-right: 1px;
    }
    QCheckBox {
        color:rgb(223,219,210);
        padding: 2px;
    }
    QCheckBox:hover {
        border-radius:4px;
        border-style:solid;
        padding-left: 1px;
        padding-right: 1px;
        padding-bottom: 1px;
        padding-top: 1px;
        border-width:1px;
        border-color: rgb(87, 97, 106);
        background-color:qlineargradient(spread:pad, x1:0.5, y1:0.7, x2:0.5, y2:0.3, stop:0 rgba(87, 97, 106, 150), stop:1 rgba(93, 103, 113, 150));
    }
    QCheckBox::indicator:checked {
        border-radius:4px;
        border-style:solid;
        border-width:1px;
        border-color: rgb(180,180,180);
        background-color:qlineargradient(spread:pad, x1:0.5, y1:0.7, x2:0.5, y2:0.3, stop:0 rgba(87, 97, 106, 255), stop:1 rgba(93, 103, 113, 255));
    }
    QCheckBox::indicator:unchecked {
        border-radius:4px;
        border-style:solid;
        border-width:1px;
        border-color: rgb(87, 97, 106);
        background-color:rgb(255,255,255);
    }
    QStatusBar {
        color:rgb(240,240,240);
    }"""
    app.setStyleSheet(style)
    sys.exit(app.exec_())
