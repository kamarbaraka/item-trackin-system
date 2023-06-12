import sys
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog, QLabel, QLineEdit, QCheckBox, QPushButton
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt

from src.databaseApi.DatabaseApi import DatabaseApi
from src.gui.RegistrationWindow import Registration


'''author: kamar baraka'''


class Login(QDialog):

    def __init__(self, database=None):
        super().__init__()
        self.__init()
        if database is None:
            self.database = DatabaseApi('../../resources/database/database', '../../resources/images/barcodeImages')
        self.database = database

    def __init(self):
        self.setModal(True)
        self.setWindowTitle('Login')
        self.setFixedSize(430, 470)

        self.__setUpWindow()

    def __setUpWindow(self):
        login_label = QLabel('<h1>Login</h1>', self)
        login_label.setFont(QFont('Arial Round MT', 15))
        login_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        login_label.move(185, 10)

        self.login_icon = '../../resources/images/user_icon.png'

        login_icon_label = QLabel(self)
        pixmap = QPixmap(self.login_icon)
        login_icon_label.setPixmap(pixmap)
        login_icon_label.resize(100, 100)
        login_icon_label.move(190, 70)

        username_tag = QLabel('User Name', self)
        username_tag.setFont(QFont('Arial Round MT', 13))
        username_tag.resize(100, 30)
        username_tag.move(10, 200)

        username_edit = QLineEdit(self)
        username_edit.resize(300, 30)
        username_edit.move(100, 200)
        self.username_edit = username_edit

        password_tag = QLabel('Password', self)
        password_tag.setFont(QFont('Arial Round MT', 13))
        password_tag.resize(100, 30)
        password_tag.move(10, 250)

        password_edit = QLineEdit(self)
        password_edit.resize(300, 30)
        password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_edit.move(100, 250)
        self.password_edit = password_edit

        show_password_cb = QCheckBox('show password', self)
        show_password_cb.move(100, 300)
        self.show_password_cb = show_password_cb
        self.show_password_cb.toggled.connect(self.__showPasswordChecked)

        login_button = QPushButton('login', self)
        login_button.resize(180, 40)
        login_button.move(100, 330)
        self.login_button = login_button
        self.login_button.clicked.connect(self.__login)

        login_reg_label = QLabel('Dont have an account? ', self)
        login_reg_label.setFont(QFont('Arial Round MT', 10))
        login_reg_label.resize(150, 30)
        login_reg_label.move(20, 400)

        login_reg_button = QPushButton('register', self)
        login_reg_button.resize(150, 30)
        login_reg_button.move(170, 400)
        self.login_reg_button = login_reg_button
        self.login_reg_button.clicked.connect(self.__registerConnect)

    def __registerConnect(self):

        self.register = Registration()
        self.register.show()
        self.close()

    def __showPasswordChecked(self, checked):

        if checked:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            return 0
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def __login(self):

        if (
            self.username_edit.text() == '' or
            self.password_edit.text() == ''
        ):
            answer = QMessageBox.warning(
                self,
                'warning', '<p> please fill the required fields </p>',
                QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok
            )

            if answer == QMessageBox.StandardButton.Ok:
                return 0

        profile = {'username': self.username_edit.text(), 'password': self.password_edit.text()}
        response = self.database.login(profile)

        if response != 'ok':
            answer0 = QMessageBox.warning(
                self,
                'warning', '<p> No such user found, Please review your details </p>',
                QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok
            )
            if answer0 == QMessageBox.StandardButton.Ok:
                return 0

        self.close()
        return 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Login()
    sys.exit(app.exec())
