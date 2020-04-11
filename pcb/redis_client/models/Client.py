# -*- coding: utf-8 -*-

import socket, select, threading
from socket import AF_INET, SOCK_STREAM


# 生成套接字 确定地址和端口号 这里可以手动输入地址
def SocketConnect(host, port):
    address = (host, int(port))
    socket_conn = socket.socket(AF_INET, SOCK_STREAM)
    socket_conn.connect_ex(address)  # 主动初始化TCP服务器连接,出错返回错误码,而不是抛出异常
    return socket_conn


# 通信列表
def Communication_List(connect):
    user = [connect]  # 用户连接进来的套接字
    while True:
        # readable, writable, exceptional = select.select(user, [], [])
        # if connect in readable:
        try:
            # 通知连接用户有谁登入
            data = connect.recv(1024)
            # 进行解码
            print(data.decode())
        except socket.error:
            print('Socket is error')
            exit()


# 输入接口
def Input_Interface(connect):
    while True:
        try:
            data = raw_input('>')
            # 有数据输入 就进行数据输出
            if data:
                Output_Interface(connect, data)
        except Exception:
            print('Error Drop Out')
            exit()
            break


# 输出接口
def Output_Interface(connect, data):
    while True:
        try:
            connect.send(data.encode())  # 进行编码
            Input_Interface(connect)  # 输出完后马上调用输入接口
        except Exception:
            print('Error, try to reconnect')
            Input_Interface(connect)  # 有误重新调用输入接口
            exit()


def main(host, port):
    # 套接字连接
    connect = SocketConnect(host, port)
    # 进行通信 通过通信列表告知谁在线
    communication = threading.Thread(target=Communication_List, args=(connect,))
    communication.start()
    # 进行数据 传入传出
    data = threading.Thread(target=Input_Interface, args=(connect,))
    data.start()


class RedisQueue(object):

    def __init__(self):
        self.port = 8888
        self.host = '10.0.0.222'
        self.db = 0
        self.name = 'GM'
        # self._connection(connect)

    def _connection(self, connect):
        value = {
            'host': self.host,
            'port': self.port,
            'db': self.db
        }
        pool = redis.ConnectionPool(**value)
        pool = redis.Redis(connection_pool=pool)
        try:
            if pool.ping():
                x_str = str(connect._sock)
                x_str = x_str[x_str.index('fd='):x_str.index(', fam')]
                x_str = x_str[x_str.index('='):][1:]
                value = {
                    'name_id': x_str,
                    'time': time.time(),
                    'value': None,
                }
                pool.lpush('GM', json.dumps(value))
                return pool
        except Exception:
            return False


if __name__ == '__main__':
    host = raw_input('Server HOST:')
    port = raw_input('Server PORT:')
    main(host, port)

# import time
#
# from socket import *
#
# HOST = '10.0.0.115'
# PORT = 9999
# BUFSIZ = 1024
# ADDR = (HOST, PORT)
#
# tcpCliSock = socket(AF_INET, SOCK_STREAM)
# tcpCliSock.connect(ADDR)
# t = 0
# a = time.time()
# while True:
#     # time.sleep(1)
#     # data=raw_input('>')
#     # t+=1
#     data = '<'+time.ctime()+'>'
#     if not data:
#         break
#     tcpCliSock.send(data)
#     data = tcpCliSock.recv(BUFSIZ)
#     b = time.time()-a
#     if b >= 600:
#         break
#     if not data:
#             break
#     print(data)
# tcpCliSock.close()