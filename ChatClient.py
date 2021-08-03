import socket
import pickle
import threading
import time
from typing import Tuple, Dict, List, Optional
from Const import TCP_HEAD, TEST_SERVER_ADDR
from PyQt5.QtCore import QObject, pyqtSignal


class ChatClient(QObject):
    sign_users_update = pyqtSignal(list)
    sign_channels_update = pyqtSignal(list)
    sign_message_recv = pyqtSignal(str, str)  # source, msg

    def __init__(self):
        super(ChatClient, self).__init__()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.recv_thread = None  # type: Optional[threading.Thread]

    def connect(self):
        self.client.connect(TEST_SERVER_ADDR)
        self.recv_thread = threading.Thread(target=self.recv)
        self.recv_thread.start()

    def recv(self):
        while True:
            msg = pickle.loads(self.client.recv(1024))
            head = msg[0]
            body = msg[1:]
            if head == TCP_HEAD.NAME:
                (users_list,) = body
                self.sign_users_update.emit(users_list)
            elif head == TCP_HEAD.CHANNEL:
                (channels_list,) = body
                self.sign_users_update.emit(channels_list)
            elif head == TCP_HEAD.MSG:
                name, msg = body
                print(body)
                self.sign_message_recv.emit(name, msg)
            else:
                raise UserWarning("未知的指令", head, body)

    def send(self, msg: str):
        bytes_send = pickle.dumps((TCP_HEAD.MSG, msg))
        self.client.send(bytes_send)

    def register_nick_name(self, name: str):
        bytes_send = pickle.dumps((TCP_HEAD.NAME, name))
        self.client.send(bytes_send)

    def register_channel(self, channel: str):
        bytes_send = pickle.dumps((TCP_HEAD.CHANNEL, channel))
        self.client.send(bytes_send)

    def exit(self):
        self.client.close()
        self.recv_thread.join()


# if __name__ == '__main__':
#     from PyQt5.QtCore import QCoreApplication
#     app = QCoreApplication([])
#     client = ChatClient()
#     client.sign_users_update.connect(print)
#     client.sign_channels_update.connect(print)
#     client.sign_message.connect(print)
#     client.connect()
#     client.register_nick_name('bugs bunny')
#     client.register_channel('house')
#     client.send('ah!')
#     app.processEvents()
#     time.sleep(1)
#     app.exec()
