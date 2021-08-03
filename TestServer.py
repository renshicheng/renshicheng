import socket
import threading
import time
import config
from typing import Optional, Dict, List

IP_ADDRESS = ('192.168.50.206', 20008)


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
        self.thread: Optional[threading.Thread] = None

    def get_connect(self):
        while True:
            client, addr = self.server.accept()
            client.send((config.SERVER_CONNECT_SUCCESS_MSG + ',' + config.NEED_NAME_INPUT).encode('utf-8'))
            self.thread = threading.Thread(target=self.deal_msg, args=(client, addr))
            self.thread.start()

    def deal_msg(self, client, addr):
        self.clients_d[client] = {}
        while True:
            recv_data = client.recv(1024).decode('utf-8')
            coding = recv_data[0:4]
            msg = recv_data[4:]
            if coding in config.CODE_MSG_NAME:
                name = msg
                self.clients_d[client] = {'name': name, 'addr': addr}
                self.open_client(name)
                self.name_list.append(name)
                client.send(config.NEED_CHANNEL_INPUT.encode('utf-8'))

            elif coding in config.CODE_MSG_CHANNEL:
                channel = msg
                self.client_channel[client] = channel
                self.channel_list.append(channel)
                if channel not in self.channel_d.keys():
                    self.channel_d[channel] = [client]
                    self.send_broadcast(self.clients_d[client]['name'] + config.CHANNEL_SET + channel)
                else:
                    self.channel_d[channel].append(client)
                    self.send_broadcast(self.clients_d[client]['name'] + config.CHANNEL_JOIN + channel)

            elif coding in config.CODE_MSG_CONTENT_EXIT:
                self.close_client(client)
                break

            elif coding in config.CODE_MSG_CONTENT_LS:
                self.search(client)

            else:
                send_msg = self.clients_d[client]['name'] + " " + time.ctime() + "\n" + recv_data
                self.send_channel(send_msg, self.client_channel[client])

    def send_broadcast(self, msg: str, client=None):
        if client is not None:
            client.send(msg.encode('utf-8'))
        else:
            for client in self.clients_d.keys():
                client.send(msg.encode('utf-8'))

    def send_channel(self, msg: str, channel):
        for c in self.channel_d[channel]:
            c.send(('频道' + channel + ':' + msg).encode('utf-8'))

    def search(self, client):
        msg = ""
        for c, v in self.clients_d.items():
            # msg += "{}\t{}\t{}\n".format(v['name'], v['addr'][0], v['addr'][1])
            msg += f'{v["name"]}\t{v["addr"][0]}\t{v["addr"][1]}\n'
        msg = msg[:-1]
        self.send_broadcast(msg, client)

    def open_client(self, name):
        print(name + config.ENTER_MSG)
        for c in self.clients_d.keys():
            c.send((name + config.ENTER_MSG + "\n").encode('utf-8'))

    def close_client(self, client):
        if "name" in self.clients_d[client].keys():
            name = self.clients_d[client]['name']
            for c in self.clients_d.keys():
                if c == client:
                    continue
                c.send((name + config.QUIT_MSG + "\n").encode('utf-8'))
            print(name + config.QUIT_MSG)
        del self.clients_d[client]
        client.close()

    def exit(self):
        self.send_broadcast('服务端退出！')


if __name__ == '__main__':
    server = TcpServer()
    while True:
        input_data = input('输入exit退出服务端:\n')
        if input_data == 'exit':
            server.exit()
            break
