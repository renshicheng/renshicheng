
import UI
import TestClient
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtWidgets


class Controller(QMainWindow):
    def __init__(self):
        super(Controller, self).__init__()
        # init
        self.ui = UI.Ui_ChatRoom()
        self.ui.setupUi(self)
        self.client = TestClient.TcpClient()
        # signal connect
        self.client.sign_msg_recv.connect(self.receive)
        self.ui.Send.clicked.connect(self.send)
        self.ui.Text.editingFinished.connect(self.send)
        # client connect
        self.client.connect()

    def send(self):
        msg = self.ui.Text.text()
        if msg == 'exit':
            self.close()
        else:
            self.client.send(msg)
            self.ui.Text.clear()

    def receive(self, data_str: str):
        self.ui.Content.addItem(data_str)

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
    app = QApplication(sys.argv)
    ctrl = Controller()
    ctrl.show()
    sys.exit(app.exec_())
