import UI_1
from ChatClient import ChatClient
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtWidgets
from time import sleep


class Controller(QMainWindow):
    def __init__(self):
        super(Controller, self).__init__()
        # init
        self.ui = UI_1.Ui_ChatRoom()
        self.ui.setupUi(self)
        self.client = ChatClient()
        # signal connect
        self.client.sign_message_recv.connect(self.receive)
        self.client.sign_channels_update.connect(self.update_channels)
        self.client.sign_users_update.connect(self.update_users)
        self.ui.Send.clicked.connect(self.send)
        self.ui.Text.returnPressed.connect(self.send)
        # client connect
        self.client.connect()

        self.client.register_channel('hole')
        sleep(0.1)
        self.client.register_nick_name('bugs bunny')

    def send(self):
        msg = self.ui.Text.text()
        if msg:
            if msg == 'exit':
                self.close()
            else:
                self.client.send(msg)
                self.ui.Text.clear()

    def receive(self, source: str, msg: str):
        self.ui.Content.addItem(source + ':' + msg)

    def update_users(self, users_list: list):
        self.ui.Online.clear()
        self.ui.Online.addItems(users_list)

    def update_channels(self, channels_list: list):
        self.ui.Channel.clear()
        self.ui.Channel.addItems(channels_list)

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, '本程序', '是否要退出聊天程序？',
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            self.client.exit()
        else:
            event.ignore()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    ctrl = Controller()
    ctrl.show()
    sys.exit(app.exec_())
