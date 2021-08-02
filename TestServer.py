import socket
import threading
import time
from typing import Optional, Dict, List


ADDRESS = ('localhost', 20007)
IP_ADDRESS = ('192.168.50.206', 20008)
SERVER_MSG = '与服务器连接成功，请输入你的昵称:'
CHANNEL_MSG = '请输入要聊天的频道名:'
ENTER_MSG = '进入了聊天室'
QUIT_MSG = '离开了聊天室'


class TcpServer:

    def __init__(self):
        '''
        Param:
            self.client_d: {client:{"name": xxx, "addr": xxx}}
            self.channel_d: {channel: [client]}
        '''
        self.clients_d = {}
        self.channel_d = {}  # type: Dict[str, List[socket.socket]]
        self.client_channel = {}
        self.name_list = []
        self.channel_list = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(IP_ADDRESS)
        self.server.listen(5)
        self.con_thread = threading.Thread(target=self.get_connect, daemon=True)
        self.con_thread.start()
        self.thread1: Optional[threading.Thread] = None
        self.thread2: Optional[threading.Thread] = None
        self.thread3: Optional[threading.Thread] = None

    def get_connect(self):
        while True:
            client, addr = self.server.accept()
            client.send(SERVER_MSG.encode())
            self.thread1 = threading.Thread(target=self.recv_name, args=(client, addr))
            self.thread1.start()

    def recv_name(self, client, addr):
        name = client.recv(1024).decode('utf-8')
        # self.clients_d[client]['name'] = name
        self.clients_d[client] = {'name': name, 'addr': addr}
        self.open_client(name)
        self.name_list.append(name)
        self.thread2 = threading.Thread(target=self.recv_channel, args=(client,))
        self.thread2.start()

    def recv_channel(self, client):
        client.send(CHANNEL_MSG.encode())
        channel = client.recv(1024).decode('utf-8')
        self.client_channel[client] = channel
        self.channel_list.append(channel)
        if channel not in self.channel_d.keys():
            self.channel_d[channel] = [client]
            self.send_broadcast(self.clients_d[client]['name'] + '创建了频道:' + channel)
        else:
            self.channel_d[channel].append(client)
            self.send_broadcast(self.clients_d[client]['name'] + '加入了频道:' + channel)
        self.thread3 = threading.Thread(target=self.deal_msg, args=(client,))
        self.thread3.start()

    def deal_msg(self, client):
        while True:
            recv_data = client.recv(1024).decode('utf-8')
            if recv_data.lower() == 'exit' or not recv_data:
                self.close_client(client)
                break
            elif recv_data.lower() == 'ls':
                self.search(client)
            else:
                msg = self.clients_d[client]['name'] + " " + time.ctime() + "\n" + recv_data
                self.send_channel(msg, self.client_channel[client])

    def send_broadcast(self, msg: str, client=None):
        if client is not None:
            client.send(msg.encode('utf-8'))
        else:
            for client in self.clients_d.keys():
                client.send(msg.encode('utf-8'))

    def send_channel(self, msg: str, channel):
        for c in self.channel_d[channel]:
            c.send(('频道'+channel+':'+msg).encode('utf-8'))

    def search(self, client):
        msg = ""
        for c, v in self.clients_d.items():
            # msg += "{}\t{}\t{}\n".format(v['name'], v['addr'][0], v['addr'][1])
            msg += f'{v["name"]}\t{v["addr"][0]}\t{v["addr"][1]}\n'
        msg = msg[:-1]
        self.send_broadcast(msg, client)

    def open_client(self, name):
        print(name + ENTER_MSG)
        for c in self.clients_d.keys():
            c.send((name + ENTER_MSG + "\n").encode('utf-8'))

    def close_client(self, client):
        name = self.clients_d[client]['name']
        print(name + QUIT_MSG)
        del self.clients_d[client]
        client.close()
        for c in self.clients_d.keys():
            c.send((name + QUIT_MSG + "\n").encode('utf-8'))

    def exit(self):
        self.send_broadcast('服务端退出！')


if __name__ == '__main__':
    server = TcpServer()
    while True:
        input_data = input('输入exit退出服务端:\n')
        if input_data == 'exit':
            server.exit()
            break
