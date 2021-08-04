
import socket
import threading
import config
from PyQt5.QtCore import QObject, pyqtSignal
from typing import Optional
from switch import Switch

ADDRESS = ('localhost', 20007)
IP_ADDRESS = ('192.168.50.206', 20008)


class TcpClient(QObject):
    sign_msg_recv = pyqtSignal(str)

    def __init__(self):
        super(TcpClient, self).__init__()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.thread: Optional[threading.Thread] = None
        self.CODING = ""

    def connect(self):
        self.client.connect(IP_ADDRESS)
        self.thread = threading.Thread(target=self.receive)
        self.thread.start()

    def receive(self):
        while True:
            try:
                bytes_data = self.client.recv(1024)
                if not bytes_data:
                    break
                str_data = bytes_data.decode('utf-8')
                with Switch(str_data) as case:
                    if case(config.SERVER_CONNECT_SUCCESS_MSG + "," + config.NEED_NAME_INPUT):
                        self.CODING = config.CODE_MSG_NAME
                    if case(config.NEED_CHANNEL_INPUT):
                        self.CODING = config.CODE_MSG_CHANNEL
                    if case.default:
                        self.CODING = config.CODE_MSG_CONTENT
                self.sign_msg_recv.emit(str_data)
            except socket.error:
                break

    def send(self, msg: str):
        if msg in config.CMD_LIST_USER:
            self.client.send((config.CODE_MSG_CONTENT_LS + msg).encode('utf-8'))
        elif msg in config.CMD_EXIT:
            self.client.send((config.CODE_MSG_CONTENT_EXIT + msg).encode('utf-8'))
        else:
            self.client.send((self.CODING + msg).encode('utf-8'))

    def search(self):
        self.client.send(config.CODE_MSG_CONTENT_LS.encode('utf-8'))

    def exit(self):
        self.client.send(config.CODE_MSG_CONTENT_EXIT.encode('utf-8'))
        self.client.close()
        self.thread.join()


if __name__ == '__main__':
    client = TcpClient()
