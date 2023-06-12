
import sys

from PyQt6.QtWidgets import QMessageBox, QLabel, QLineEdit, QPushButton, QDialog, QApplication
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
from src.databaseApi.DatabaseApi import DatabaseApi


'''author: kamar baraka'''


class Registration(QDialog):

    def __init__(self, database=None):
        super().__init__()
        self.__init()
        if database is None:
            self.database = DatabaseApi('../../resources/database/database', '../../resources/images/barcodeImages')
        self.database = database

    def __init(self):
        self.setModal(True)
        self.setWindowTitle('Registration')
        self.setFixedSize(430, 470)

        self.__setUpDialog()


    def __setUpDialog(self):

        registration_label = QLabel('<h1>New User</h1>', self)
        registration_label.setFont(QFont('Arial Rounded MT', 18))
        registration_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        registration_label.move(100, 10)

        image = '../../resources/images/user_icon.png'

        registration_profile_pic = QLabel(self)
        pixmap = QPixmap(image)
        registration_profile_pic.setPixmap(pixmap)
        registration_profile_pic.resize(120, 100)
        registration_profile_pic.move(150, 70)

        user_name_tag = QLabel('User Name', self)
        user_name_tag.setFont(QFont('Arial Round MT', 13))
        user_name_tag.resize(100, 30)
        user_name_tag.move(10, 210)

        username_edit = QLineEdit(self)
        username_edit.setPlaceholderText('enter username to use')
        username_edit.resize(300, 30)
        username_edit.move(100, 210)
        self.username_edit = username_edit

        fullname_tag = QLabel('Full Name', self)
        fullname_tag.setFont(QFont('Arial Round MT', 13))
        fullname_tag.resize(100, 30)
        fullname_tag.move(10, 260)

        fullname_edit = QLineEdit(self)
        fullname_edit.setPlaceholderText('enter your full name: First Last')
        fullname_edit.resize(300, 30)
        fullname_edit.move(100, 260)
        self.fullname_edit = fullname_edit

        password_tag = QLabel('Password', self)
        password_tag.setFont(QFont('Arial Round MT', 13))
        password_tag.resize(100, 30)
        password_tag.move(10, 310)

        password_edit = QLineEdit(self)
        password_edit.setPlaceholderText('your password')
        password_edit.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        password_edit.resize(300, 30)
        password_edit.move(100, 310)
        self.password_edit = password_edit

        confirm_tag = QLabel('Confirm', self)
        confirm_tag.setFont(QFont('Arial Round MT', 13))
        confirm_tag.resize(100, 30)
        confirm_tag.move(10, 360)

        confirm_edit = QLineEdit(self)
        confirm_edit.setPlaceholderText('confirm your password')
        confirm_edit.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        confirm_edit.resize(300, 30)
        confirm_edit.move(100, 360)
        self.confirm_edit = confirm_edit

        register_button = QPushButton('register', self)
        register_button.resize(150, 40)
        register_button.move(160, 410)
        self.register_button = register_button
        self.register_button.clicked.connect(self.__Register)

    def __Register(self):

        if (
            self.username_edit.text() == '' or
            self.fullname_edit.text() == '' or
            self.password_edit.text() == '' or
            self.confirm_edit.text() == ''
        ):
            answer = QMessageBox.warning(
                self.register_button,
                'warning', """<p>please fill in all the details</p>""",
                QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok
            )
            if answer == QMessageBox.StandardButton.Ok:
                return 1

        if self.password_edit.text() == self.confirm_edit.text():
            password = self.confirm_edit.text()
            username = self.username_edit.text()
            first_name = self.fullname_edit.text().strip().split(' ')[0]
            last_name = self.fullname_edit.text().strip().split(' ')[1]

            user_profile = {'username': username, 'password': password, 'firstname': first_name, 'lastname': last_name}
            response = self.database.register(user_profile)

            if response != 'ok':
                answer0 = QMessageBox.warning(
                    self,
                    'warning', '<p> error occurred </p>',
                    QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok
                )
                if answer0 == QMessageBox.StandardButton.Ok:
                    return 0

            answer1 = QMessageBox.information(
                self,
                'info', ' registration successful',
                QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok
            )
            if answer1 == QMessageBox.StandardButton.Ok:
                self.close()
                return 0

        answer1 = QMessageBox.warning(
            self,
            'warning',
            '<p> passwords do not match </p>',
            QMessageBox.StandardButton.Ok,
            QMessageBox.StandardButton.Ok
        )

        if answer1 == QMessageBox.StandardButton.Ok:
            self.password_edit.clear()
            self.confirm_edit.clear()
            return 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Registration()
    sys.exit(app.exec())
