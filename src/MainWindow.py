import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton
from src.gui.LoginWindow import Login
from src.gui.RegistrationWindow import Registration


'''author: kamar baraka'''


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.__init()

    def __init(self):

        self.setWindowTitle('Main window')
        self.setFixedSize(500, 300)

        self.__setUpWindow()

        self.show()

    def __setUpWindow(self):

        login_button = QPushButton('login', self)
        login_button.resize(200, 50)
        login_button.move(150, 100)
        login_button.clicked.connect(self.__connectLogin)

        register_button = QPushButton('register', self)
        register_button.resize(200, 50)
        register_button.move(150, 180)
        register_button.clicked.connect(self.__connectRegister)

    def __connectLogin(self):
        self.login = Login()
        self.login.show()

    def __connectRegister(self):
        self.register = Registration()
        self.register.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
