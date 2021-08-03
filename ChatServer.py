import socket
import pickle
import threading
from typing import Tuple, Dict, List


from Const import TCP_HEAD, TEST_SERVER_ADDR

TYPE_ADDR = Tuple[str, int]


class ChatServer:
    def __init__(self):
        # params
        self.clients = {}  # type: Dict[TYPE_ADDR, Tuple[socket.socket, str, str]] # conn, name, channel
        self.channels = {}  # type: Dict[str, List[TYPE_ADDR]]  # channel, addr_list
        # socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(TEST_SERVER_ADDR)
        self.server.listen(5)
        # threading
        self.thread_accept = threading.Thread(target=self.working_accept, daemon=True)
        self.thread_accept.start()

    def working_accept(self):
        while True:
            client, addr = self.server.accept()
            thread = threading.Thread(target=self.receiving_from_client, args=(client, addr))
            thread.start()

    def receiving_from_client(self, conn: socket.socket, addr: TYPE_ADDR):
        cached_name = None
        cached_channel = None
        is_ready = False
        while True:
            recv_bytes = conn.recv(1024)
            if not recv_bytes:
                # exit code
                self.remove_client(addr, conn, cached_name, cached_channel)
                break
            recv_msg = pickle.loads(recv_bytes)
            head = recv_msg[0]
            body = recv_msg[1:]
            print(recv_msg)
            if head == TCP_HEAD.NAME:
                (name,) = body
                if cached_name is None:
                    cached_name = name

            elif head == TCP_HEAD.CHANNEL:
                (channel,) = body
                if cached_channel is None:
                    cached_channel = channel
            # check ready
            if not is_ready:
                if cached_channel is not None and cached_name is not None:
                    self.client_enter(addr, conn, cached_name, cached_channel)
                    is_ready = True
                continue
            # ...
            if head == TCP_HEAD.MSG:
                (msg,) = body
                self.send_channel(msg, self.clients[addr][2])

    def client_enter(self, addr: TYPE_ADDR, conn: socket.socket, name: str, channel: str):
        print(f'new client connect {addr}  {name}  {channel}')
        self.clients[addr] = (conn, name, channel)
        if channel in self.channels:
            self.channels[channel].append(addr)
        else:
            self.channels[channel] = [addr]
        # broadcast
        self.sync_channels()
        self.sync_users(channel)

    def send_channel(self, msg: str, channel: str):
        for addr in self.channels[channel]:
            conn = self.clients[addr][0]
            name = self.clients[addr][1]
            bytes_send = pickle.dumps((TCP_HEAD.MSG, name, msg))
            conn.send(bytes_send)

    def sync_channels(self):
        channels_list = list(self.channels.keys())
        bytes_msg = pickle.dumps((TCP_HEAD.CHANNEL, channels_list))
        for client in self.clients.values():
            conn = client[0]
            conn.send(bytes_msg)

    def sync_users(self, channel: str):
        users_list = [self.clients[addr][1] for addr in self.channels[channel]]
        bytes_msg = pickle.dumps((TCP_HEAD.NAME, users_list))
        for addr in self.channels[channel]:
            conn = self.clients[addr][0]
            conn.send(bytes_msg)

    def remove_client(self, addr, conn, name, channel):
        print(f'old client disconnected {addr}  {name}  {channel}')
        conn.close()
        del self.clients[addr]
        self.channels[channel].remove(addr)
        # broadcast
        self.sync_channels()
        self.sync_users(channel)

    def exit(self):
        pass


if __name__ == '__main__':
    server = ChatServer()
    input('按下回车键推出')
