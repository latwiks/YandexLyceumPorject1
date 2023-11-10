import sqlite3
from PyQt5.QtWidgets import QMessageBox, QDialogButtonBox, QLineEdit, QFormLayout, QDialog
from hash_password import hash_password

conn = sqlite3.connect('test.db')
c = conn.cursor()


class ChangeNameInterface(QDialog):  # сменить фио любому от имени того "любого"
    def __init__(self, user_id, role, label):
        super().__init__()
        self.role = role
        self.label = label
        self.setWindowTitle('Сменить имя')
        self.setFixedSize(350, 100)
        self.user_id = user_id
        self.layout = QFormLayout()

        self.new_name = QLineEdit()
        self.new_name.setPlaceholderText("Пример: Иванов Иван Иванович")
        self.layout.addRow("Новое ФИО", self.new_name)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Пример: Qwert1234!")
        self.layout.addRow("Пароль", self.password)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.change_name)
        self.buttons.rejected.connect(self.reject)

        self.layout.addRow(self.buttons)

        self.setLayout(self.layout)

    def change_name(self):  # ф-ия
        new_name = self.new_name.text().strip()
        password = self.password.text()

        c.execute("SELECT password FROM users WHERE id=?", (self.user_id,))
        actual_password = c.fetchone()[0]

        if hash_password(password) != actual_password:
            QMessageBox.warning(self, "Ошибка", "Пароль неверный!")
            return

        if len(new_name.split()) < 2:
            QMessageBox.warning(self, "Ошибка", "Введите полностью ФИО (можно без отчества)!")
            return

        c.execute("UPDATE users SET name=? WHERE id=?", (new_name, self.user_id))
        conn.commit()
        self.accept()
        self.label.setText(self.role + new_name)
        conn.close()
