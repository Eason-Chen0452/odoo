# -*- coding: utf-8 -*-

import socket, select, redis, time, json
from socket import AF_INET, SOCK_STREAM
# import tkinter as tk

aisle = []  # 列表通道 存放通信的用户 和 服务端 - 应该就是redis的消息队列
user_name = {}  # 用户名字典


# 启动服务器 生成套接字
def Server(host, port):
    address = (host, int(port))
    server_socket = socket.socket(AF_INET, SOCK_STREAM)
    server_socket.bind(address)  # 绑定地址(主机名,端口号)
    server_socket.listen(5)  # 进行TCP监听
    print('Server Startup')
    return server_socket


# 新用户登入
def NewUserLogin(client, add):
    # client, add = connect.accept()  # 被动接受TCP客户端连接,(阻塞式)等待连接的到来
    print('User Login %s' % (add,))  # 哪个IP登入进来
    data = "Please enter your name first..."
    try:
        # 将data这句话发送到客户端
        client.send(data.encode())
        # 接受客户端回应 得到名字
        name = client.recv(1024)
        # 将此用户加入列表通信当中
        aisle.append(client)
        # 将用户名加入字典当中
        user_name[client] = name.decode()
        # 返回所在人
        user_list = "Currently there is %s" % (User_List(user_name))
        client.send(user_list.encode())
    except Exception:
        # 用户登入失败
        print('User login failed')


# 处理那些用户在聊天室 返回列表
def User_List(user_name):
    name_list = []
    for user in user_name:
        name_list.append(user_name[user])
    return name_list


# 控制台
def ServerStartup(host, port):
    connect = Server(host, port)
    name = RedisQueue()
    queue = name._connection(connect)
    # 将套接字加入通信列表当中
    # aisle.append(connect)
    # user_name[connect] = 'GM'
    while True:
        client, add = connect.accept()
        # readable, writable, exceptional = select.select(aisle, [], [])
        # 进行循环 检查通信列表
        # for conn in readable:
        # 如果通信列表中有用户登入则调用新用户函数
        if client not in aisle:
            NewUserLogin(client, add)
        else:
            # 此布尔值判断是否断开
            disconnect = False
            try:
                # 接受客户端数据
                data = client.recv(1024)
                data = user_name[client] + ': ' + data.decode()
            # 如果套接字出现错误 告知谁退出了
            except socket.error:
                data = user_name[client] + ' Leave'
                disconnect = True
            # 当为TRUE时将这个套接字进行删除
            if disconnect:
                aisle.remove(client)
                del user_name[client]
            else:
                # 如果有数据输出到终端
                if data:
                    print(data)
                # 循环通信列表 将消息发送出去
                for other in aisle:
                    # 除去服务器的套接字 和 客户自己的套接字,其他的进行发送
                    if other != connect and other != client:
                        try:
                            other.send(data.encode())
                        except Exception:
                            print('Conveying Error')


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
                # x_str = str(connect._sock)
                # x_str = x_str[x_str.index('fd='):x_str.index(', fam')]
                # x_str = x_str[x_str.index('='):][1:]
                value = {
                    'name_id': str(connect),
                    'time': time.time(),
                    # 'value': None,
                }
                pool.lpush('aisle', json.dumps(value))
                return pool
        except Exception:
            return False


if __name__ == '__main__':
    host = raw_input('HOST:')
    port = raw_input('PORT:')
    ServerStartup(host, port)

# from twisted.internet.protocol import Factory
# from twisted.protocols.basic import LineReceiver
# from twisted.internet import protocol, reactor
# from time import ctime
# import redis
#
# r = redis.Redis(host='10.0.0.222', port=8888)
# r.ping()
# # PORT = 8123
#
#
# class TSServProtocol(protocol.Protocol):
#
#     def __init__(self,users):
#         self.users = users
#         self.name = None
#
#     def connectionMade(self):
#         clnt = self.clnt = self.transport.getPeer().host
#         print '...connected from:', ctime(), clnt
#
#     def connectionLost(self, reason):
#         clnt=self.clnt=self.transport.getPeer().host
#         print '...lost connected from:',clnt
#         if self.users.has_key(self.name):
#             del self.users[self.name]
#             r.delete(self.name)
#
#     def dataReceived(self, data):
#         data=data.split('&&&')
#         self.users[data[0]]=data[1]
#         r[data[0]]=data[1]
#         self.name=data[0]
#         self.transport.write('[%s] %s' %(ctime(),data))
#
#
# class ChatFactory(Factory):
#     def __init__(self):
#         self.users = {}
#
#     def buildProtocol(self, addr):
#         return TSServProtocol(self.users)
# #factory=protocol.Factory()
# #factory.protocol=TSServProtocol(self.users)
# print 'waiting fot connection...'
# reactor.listenTCP(9999, ChatFactory())
# reactor.run()
