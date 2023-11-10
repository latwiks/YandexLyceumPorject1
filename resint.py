import csv
import sqlite3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QPushButton, QTableWidgetItem, QFileDialog, QMessageBox

conn = sqlite3.connect('test.db')
c = conn.cursor()


class ResultsInterface(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Результаты')

        self.layout = QVBoxLayout()

        self.results_table = QTableWidget()
        self.layout.addWidget(self.results_table)

        self.refresh_results_button = QPushButton("Перезагрузить результаты")
        self.refresh_results_button.clicked.connect(self.refresh_results)
        self.layout.addWidget(self.refresh_results_button)

        self.save_results_button = QPushButton("Сохранить результаты")
        self.save_results_button.clicked.connect(self.save_results)
        self.layout.addWidget(self.save_results_button)

        self.setLayout(self.layout)

    def refresh_results(self):
        try:
            c.execute(
                "SELECT users.username, tests.test_name, results.score, results.errors, results.completed_at"
                " FROM results "
                "INNER JOIN users ON results.user_id=users.id "
                "INNER JOIN tests ON results.test_id=tests.id "
                "ORDER BY results.completed_at DESC")
            results = c.fetchall()

            self.results_table.setColumnCount(5)
            self.results_table.setHorizontalHeaderLabels(["Имя", "Тест", "Процент успеха", "Ошибки", "Закончено"])

            self.results_table.setRowCount(0)
            for i, (username, test_name, score, errors, date) in enumerate(results):
                self.results_table.insertRow(i)
                self.results_table.setItem(i, 0, QTableWidgetItem(username))
                self.results_table.setItem(i, 1, QTableWidgetItem(test_name))
                self.results_table.setItem(i, 2, QTableWidgetItem(str(score)))
                self.results_table.setItem(i, 3, QTableWidgetItem(str(errors)))
                self.results_table.setItem(i, 4, QTableWidgetItem(date))

        except sqlite3.Error as e:
            print("Не удалось выгрузить данные из бд: ", e)

    def save_results(self):
        if self.results_table.rowCount() > 0:
            try:
                path, _ = QFileDialog.getSaveFileName(
                    self, "Сохранить результаты", "", "CSV Files (*.csv)")

                if path:
                    with open(path, 'w', newline='') as stream:
                        writer = csv.writer(stream)
                        header = []
                        for i in range(self.results_table.columnCount()):
                            header.append(self.results_table.horizontalHeaderItem(i).text())
                        writer.writerow(header)
                        for row in range(self.results_table.rowCount()):
                            row_data = []
                            for column in range(self.results_table.columnCount()):
                                item = self.results_table.item(row, column)
                                if item is not None:
                                    row_data.append(
                                        item.text()
                                    )
                                else:
                                    row_data.append('')
                            writer.writerow(row_data)

            except Exception as e:
                print("Не удалось записать в файл: ", e)
        else:
            QMessageBox.warning(self, "Ошибка", "Таблица пуста.")
