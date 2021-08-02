
import socket
import threading
from PyQt5.QtCore import QObject, pyqtSignal

ADDRESS = ('localhost', 20007)
IP_ADDRESS = ('192.168.50.206', 20008)


class TcpClient(QObject):
    sign_msg_recv = pyqtSignal(str)

    def __init__(self):
        super(TcpClient, self).__init__()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.client.connect(IP_ADDRESS)
        self.recv_thread = threading.Thread(target=self.recv)
        self.recv_thread.start()

    def recv(self):
        while True:
            bytes_data = self.client.recv(1024)
            if not bytes_data:
                break
            str_data = bytes_data.decode('utf-8')
            self.sign_msg_recv.emit(str_data)

    def send(self, string: str):
        self.client.send(string.encode('utf-8'))

    def search(self):
        self.client.send('ls'.encode('utf-8'))

    def exit(self):
        self.client.send('exit'.encode('utf-8'))
        self.recv_thread.join()


if __name__ == '__main__':
    client = TcpClient()
    while True:
        input_data = input('')
        if input_data == 'ls':
            client.search()
        elif input_data == 'exit':
            client.exit()
            break
        else:
            client.send(input_data)
